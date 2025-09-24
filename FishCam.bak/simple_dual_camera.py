#!/usr/bin/env python3
"""
Simple Side-by-Side Dual Camera Stream
======================================

This approach combines two camera feeds into a single stream by concatenating frames side-by-side.
Easiest to implement with minimal changes to existing web_stream.py structure.

Pros:
- Single stream endpoint (minimal web page changes)
- Uses existing MediaRelay structure
- Bandwidth efficient (one stream instead of two)

Cons:
- Lower resolution per camera (width is halved)
- If one camera fails, whole stream affected
"""

import cv2
import numpy as np
import json
import logging
import time
from threading import Thread, Condition

# Configuration
VIDEO_WIDTH = 640
VIDEO_HEIGHT = 480
JPEG_QUALITY = 85
FRAME_RATE = 10

def load_camera_indexes():
    """Load available cameras from camera_info.json."""
    try:
        with open("camera_info.json", "r") as f:
            data = json.load(f)
            cameras = [cam["index"] for cam in data["cameras"]]
            return cameras[:2]  # First two cameras
    except:
        return [0, 1]  # Default fallback

class DualCameraRelay:
    """
    Modified MediaRelay that handles two cameras and combines them side-by-side.
    Drop-in replacement for your existing MediaRelay class.
    """
    
    def __init__(self):
        self.frame = None
        self.condition = Condition()
        self.running = False
        self.caps = []
        self.capture_thread = None
        self.camera_indexes = load_camera_indexes()
        
        # Label overlay settings
        self.label_start_time = time.time()
        
    def start_capture(self, camera_index=None):
        """
        Start capturing from dual cameras.
        camera_index parameter kept for compatibility but ignored.
        """
        logging.info("Starting dual camera capture...")
        
        # Initialize both cameras
        for i, cam_idx in enumerate(self.camera_indexes):
            try:
                # Try different backends
                cap = None
                for backend in [cv2.CAP_DSHOW, cv2.CAP_V4L2, 0]:
                    try:
                        if backend == 0:
                            cap = cv2.VideoCapture(cam_idx)
                        else:
                            cap = cv2.VideoCapture(cam_idx, backend)
                        
                        if cap and cap.isOpened():
                            break
                        elif cap:
                            cap.release()
                    except:
                        if cap:
                            cap.release()
                        cap = None
                
                if cap and cap.isOpened():
                    # Configure camera
                    cap.set(cv2.CAP_PROP_FRAME_WIDTH, VIDEO_WIDTH)
                    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, VIDEO_HEIGHT)
                    cap.set(cv2.CAP_PROP_FPS, FRAME_RATE)
                    
                    self.caps.append(cap)
                    logging.info(f"✓ Camera {cam_idx} initialized")
                else:
                    logging.warning(f"✗ Camera {cam_idx} failed to initialize")
                    self.caps.append(None)
            except Exception as e:
                logging.error(f"Camera {cam_idx} error: {e}")
                self.caps.append(None)
        
        if not any(self.caps):
            raise RuntimeError("No cameras could be initialized")
        
        # Start capture thread
        self.running = True
        self.capture_thread = Thread(target=self._capture_frames, daemon=True)
        self.capture_thread.start()
        
        logging.info(f"Dual camera capture started with {len([c for c in self.caps if c])} cameras")

    def _capture_frames(self):
        """Capture frames from both cameras and combine side-by-side."""
        frame_interval = 1.0 / FRAME_RATE
        last_frame_time = 0
        
        while self.running:
            current_time = time.time()
            
            # Frame rate limiting
            if current_time - last_frame_time < frame_interval:
                time.sleep(0.01)
                continue
            
            frames = []
            
            # Read from both cameras
            for i, cap in enumerate(self.caps):
                if cap and cap.isOpened():
                    ret, frame = cap.read()
                    if ret and frame is not None:
                        # Resize to half width for side-by-side
                        target_width = VIDEO_WIDTH // 2
                        frame = cv2.resize(frame, (target_width, VIDEO_HEIGHT))
                        
                        # Add camera label
                        self._add_camera_label(frame, i)
                        frames.append(frame)
                    else:
                        # Create black placeholder for failed read
                        frames.append(self._create_placeholder(i, "No Signal"))
                else:
                    # Create placeholder for disconnected camera
                    frames.append(self._create_placeholder(i, "Disconnected"))
            
            # If we have no frames, create dual placeholder
            if not frames:
                combined_frame = self._create_dual_placeholder()
            elif len(frames) == 1:
                # Only one camera working - duplicate it or add placeholder
                if len(self.caps) > 1:
                    frames.append(self._create_placeholder(1, "Camera Offline"))
                combined_frame = np.hstack(frames)
            else:
                # Combine frames horizontally (side-by-side)
                combined_frame = np.hstack(frames)
            
            # Add main overlay (periodic label)
            combined_frame = self._add_main_overlay(combined_frame)
            
            # Encode to JPEG
            encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), JPEG_QUALITY]
            result, jpeg = cv2.imencode('.jpg', combined_frame, encode_param)
            
            if result:
                with self.condition:
                    self.frame = jpeg.tobytes()
                    self.condition.notify_all()
                    
                last_frame_time = current_time
    
    def _create_placeholder(self, camera_num, message):
        """Create a placeholder frame for failed/missing camera."""
        target_width = VIDEO_WIDTH // 2
        placeholder = np.zeros((VIDEO_HEIGHT, target_width, 3), dtype=np.uint8)
        
        # Add text
        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(placeholder, f"Camera {self.camera_indexes[camera_num] if camera_num < len(self.camera_indexes) else camera_num}", 
                   (10, 30), font, 0.7, (255, 255, 255), 2)
        cv2.putText(placeholder, message, (10, 60), font, 0.6, (100, 100, 100), 2)
        
        return placeholder
    
    def _create_dual_placeholder(self):
        """Create placeholder when no cameras are working."""
        placeholder = np.zeros((VIDEO_HEIGHT, VIDEO_WIDTH, 3), dtype=np.uint8)
        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(placeholder, "No Cameras Available", 
                   (VIDEO_WIDTH//2 - 120, VIDEO_HEIGHT//2), font, 1, (100, 100, 100), 2)
        return placeholder
    
    def _add_camera_label(self, frame, camera_num):
        """Add camera identifier to individual frame."""
        if camera_num < len(self.camera_indexes):
            label = f"Cam {self.camera_indexes[camera_num]}"
            cv2.putText(frame, label, (5, 20), cv2.FONT_HERSHEY_SIMPLEX, 
                       0.5, (0, 255, 255), 1)
    
    def _add_main_overlay(self, frame):
        """Add main periodic overlay (WNCC label)."""
        current_time = time.time()
        cycle_duration = 15 * 60  # 15 minutes
        
        # Check if we should show label (60 seconds every 15 minutes)
        time_in_cycle = (current_time - self.label_start_time) % cycle_duration
        should_show_label = time_in_cycle < 60
        
        if should_show_label:
            label = "WNCC STEM Club - Dual Camera View"
            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = 0.8
            color = (0, 255, 255)  # Yellow
            thickness = 2
            
            # Get text size for background
            (text_width, text_height), baseline = cv2.getTextSize(label, font, font_scale, thickness)
            
            # Position at bottom
            x = 20
            y = frame.shape[0] - 20
            
            # Draw background rectangle
            cv2.rectangle(frame, (x-5, y-text_height-5), (x+text_width+5, y+baseline+5), (0, 0, 0), -1)
            
            # Draw text
            cv2.putText(frame, label, (x, y), font, font_scale, color, thickness)
            
        return frame

    def get_frame(self):
        """Get the latest combined frame."""
        with self.condition:
            self.condition.wait()
            return self.frame

    def stop_capture(self):
        """Stop capture and release cameras."""
        self.running = False
        if self.capture_thread:
            self.capture_thread.join()
        
        for cap in self.caps:
            if cap:
                cap.release()
        
        logging.info("Dual camera capture stopped")

# Usage example:
"""
To use this in your existing web_stream.py:

1. Replace your MediaRelay class with DualCameraRelay
2. Change initialization from:
   relay.start_capture(camera_index)
   to:
   relay.start_capture()  # camera_index ignored, uses camera_info.json

3. Update your HTML page title to mention "Dual Camera"

That's it! The rest of your code stays the same.
"""

if __name__ == "__main__":
    # Test the dual camera relay
    import logging
    logging.basicConfig(level=logging.INFO)
    
    relay = DualCameraRelay()
    try:
        relay.start_capture()
        print("Dual camera relay test started. Press Ctrl+C to stop.")
        
        # Test for 10 seconds
        import time
        time.sleep(10)
        
    except KeyboardInterrupt:
        print("Stopping...")
    finally:
        relay.stop_capture()
        print("Test complete.")
