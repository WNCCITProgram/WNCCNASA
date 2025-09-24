#!/usr/bin/env python3
"""
Dual Camera Web Streaming Server
=====================================

This script handles streaming from two cameras simultaneously with separate endpoints:
- Camera 0: http://IP:8000/stream0.mjpg
- Camera 1: http://IP:8000/stream1.mjpg
- Dual view: http://IP:8000/index.html (shows both cameras side by side)

Based on the original web_stream.py but extended for dual camera support.
"""

import logging
import json
import cv2
import socketserver
import time
from http import server
from logging.handlers import TimedRotatingFileHandler
from threading import Condition, Thread
from dual_camera_page import generate_html_page

# ------------------------ CONFIGURATION ------------------------- #
# Global streaming settings
MAX_STREAM_FPS = 15  # Maximum FPS for all streams
JPEG_QUALITY = 85  # JPEG compression quality (0-100)

# Logging configuration
LOG_LEVEL = logging.INFO  # Change to logging.DEBUG for more verbose output
LOG_ROTATION_DAYS = 7  # Number of daily log files to keep

# Camera-specific configurations
CAMERA_CONFIGS = {
    0: {
        # Camera 0 - Main/Primary camera with overlay
        "frame_rate": 15,
        "width": 1280,
        "height": 720,
        "enable_overlay": True,
        "overlay_text": "WNCC STEM Club Meeting Thursday at 4 in C1",
        "overlay_cycle_minutes": 10,
        "overlay_duration_seconds": 30,
        "overlay_font_scale": 0.8,
        "overlay_transparency": 0.7,
        "text_transparency": 0.9,
        "text_color": (0, 85, 204),  # Burnt orange in BGR
        "description": "Main Camera (Fish Tank)",
    },
    2: {
        # Camera 2 - Secondary camera without overlay
        "frame_rate": 7.5,
        "width": 1280,
        "height": 720,
        "enable_overlay": False,
        "overlay_text": "",
        "overlay_cycle_minutes": 0,
        "overlay_duration_seconds": 0,
        "overlay_font_scale": 0.7,
        "overlay_transparency": 0.5,
        "text_transparency": 1.0,
        "text_color": (255, 255, 255),  # White in BGR
        "description": "Secondary Camera (Plant Beds)",
    },
}

# Default configuration for cameras not specifically configured
DEFAULT_CAMERA_CONFIG = {
    "frame_rate": 10,
    "width": 1280,
    "height": 720,
    "enable_overlay": False,
    "overlay_text": "Camera Feed",
    "overlay_cycle_minutes": 15,
    "overlay_duration_seconds": 60,
    "overlay_font_scale": 0.7,
    "overlay_transparency": 0.6,
    "text_transparency": 0.9,
    "text_color": (255, 255, 0),  # Yellow in BGR
    "description": "Additional Camera",
}


# Setup logging with 24-hour rotation
def setup_logging():
    """Configure logging with daily rotation and both file and console output."""
    # Create logs directory if it doesn't exist
    import os

    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(LOG_LEVEL)

    # Remove any existing handlers to avoid duplicates
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Formatter for all handlers
    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    )

    # File handler with daily rotation
    file_handler = TimedRotatingFileHandler(
        filename=os.path.join(log_dir, "dual_camera_stream.log"),
        when="midnight",  # Rotate at midnight
        interval=1,  # Every 1 day
        backupCount=LOG_ROTATION_DAYS,  # Keep configured number of days
        encoding="utf-8",
    )
    file_handler.setLevel(LOG_LEVEL)
    file_handler.setFormatter(formatter)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(LOG_LEVEL)
    console_handler.setFormatter(formatter)

    # Add handlers to root logger
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)

    # Prevent propagation to avoid duplicate messages
    root_logger.propagate = False

    return root_logger


# Initialize logging
logger = setup_logging()
logger.info(
    "Dual Camera Streaming Server - Logging initialized with daily rotation"
)


# ------------------------ CAMERA INFO LOADING ------------------------- #
# Load camera info from camera_test.py output
def load_camera_info():
    """Load available cameras from camera_info.json if it exists."""
    try:
        with open("camera_info.json", "r") as f:
            data = json.load(f)
            cameras = [cam["index"] for cam in data["cameras"]]
            logger.info(f"Found cameras from camera_info.json: {cameras}")
            return cameras[:2]  # Use first two cameras
    except (FileNotFoundError, json.JSONDecodeError, KeyError):
        logger.warning(
            "camera_info.json not found or invalid, using default [0, 1]"
        )
        return [0, 1]


CAMERA_INDEXES = [0, 2]  # Use camera 0 and camera 2 instead of [0, 1]


# Helper function to get camera configuration
def get_camera_config(camera_index):
    """Get configuration for a specific camera, with fallback to default."""
    return CAMERA_CONFIGS.get(camera_index, DEFAULT_CAMERA_CONFIG)


# ------------------------ MEDIA RELAY CLASS ------------------------- #
class MediaRelay:
    """Handles single camera capture and frame distribution."""

    def __init__(self, camera_index):
        self.camera_index = camera_index
        self.frame = None
        self.condition = Condition()
        self.running = False
        self.cap = None
        self.capture_thread = None

        # Load camera-specific configuration
        self.config = get_camera_config(camera_index)

        # Initialize overlay timing if enabled for this camera
        if self.config["enable_overlay"]:
            self.label_start_time = time.time()
            self.label_shown = False

    def start_capture(self):
        """Start capturing from the assigned camera."""
        logger.info(f"[Camera {self.camera_index}] Starting capture...")

        # Try multiple backends for compatibility
        backends = [cv2.CAP_DSHOW, cv2.CAP_V4L2, 0]  # DirectShow, V4L2, default

        for backend in backends:
            try:
                if backend == 0:
                    self.cap = cv2.VideoCapture(self.camera_index)
                else:
                    self.cap = cv2.VideoCapture(self.camera_index, backend)

                if self.cap.isOpened():
                    logger.info(
                        f"[Camera {self.camera_index}] Opened with backend {backend}"
                    )
                    break
                else:
                    self.cap.release()
            except Exception as e:
                logger.warning(
                    f"[Camera {self.camera_index}] Backend {backend} failed: {e}"
                )

        if not self.cap or not self.cap.isOpened():
            raise RuntimeError(f"Could not open camera {self.camera_index}")

        # Configure camera with camera-specific settings
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.config["width"])
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.config["height"])
        self.cap.set(cv2.CAP_PROP_FPS, self.config["frame_rate"])

        # Log actual settings
        actual_w = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        actual_h = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        actual_fps = self.cap.get(cv2.CAP_PROP_FPS)
        logger.info(
            f"[Camera {self.camera_index}] {self.config['description']} - Settings: {actual_w}x{actual_h} @ {actual_fps} FPS"
        )

        # Start capture thread
        self.running = True
        self.capture_thread = Thread(target=self._capture_frames, daemon=True)
        self.capture_thread.start()

    def _capture_frames(self):
        """Background thread that captures frames from camera."""
        frame_interval = 1.0 / MAX_STREAM_FPS
        last_frame_time = 0

        while self.running and self.cap:
            current_time = time.time()

            # Frame rate limiting
            if current_time - last_frame_time < frame_interval:
                time.sleep(0.01)
                continue

            ret, frame = self.cap.read()
            if not ret:
                logger.warning(
                    f"[Camera {self.camera_index}] Failed to read frame"
                )
                continue

            # Add overlay if enabled for this camera
            if self.config["enable_overlay"]:
                frame = self._add_overlay(frame)

            # Encode to JPEG
            encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), JPEG_QUALITY]
            result, jpeg = cv2.imencode(".jpg", frame, encode_param)

            if result:
                # Update shared frame
                with self.condition:
                    self.frame = jpeg.tobytes()
                    self.condition.notify_all()

                last_frame_time = current_time

    def _add_overlay(self, frame):
        """Add text overlay to frame using camera-specific configuration."""
        current_time = time.time()
        cycle_duration = (
            self.config["overlay_cycle_minutes"] * 60
        )  # Convert minutes to seconds

        # Check if we should show label
        time_in_cycle = (current_time - self.label_start_time) % cycle_duration
        should_show_label = (
            time_in_cycle < self.config["overlay_duration_seconds"]
        )

        if should_show_label:
            # Add camera identifier and label
            label = f"Camera {self.camera_index}: {self.config['overlay_text']}"
            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = self.config["overlay_font_scale"]
            color = self.config["text_color"]  # Use configured color
            thickness = 2

            # Get text size for background
            (text_width, text_height), baseline = cv2.getTextSize(
                label, font, font_scale, thickness
            )

            # Position at bottom left
            x, y = 20, frame.shape[0] - 20

            # Create semi-transparent background
            overlay = frame.copy()
            cv2.rectangle(
                overlay,
                (x - 5, y - text_height - 5),
                (x + text_width + 5, y + baseline + 5),
                (0, 0, 0),  # Black background
                -1,
            )

            # Apply background transparency
            cv2.addWeighted(
                overlay,
                self.config["overlay_transparency"],
                frame,
                1 - self.config["overlay_transparency"],
                0,
                frame,
            )

            # Draw text with configured transparency
            text_overlay = frame.copy()
            cv2.putText(
                text_overlay, label, (x, y), font, font_scale, color, thickness
            )
            cv2.addWeighted(
                text_overlay,
                self.config["text_transparency"],
                frame,
                1 - self.config["text_transparency"],
                0,
                frame,
            )

        return frame

    def get_frame(self):
        """Get the latest frame for streaming."""
        with self.condition:
            self.condition.wait()
            return self.frame

    def stop_capture(self):
        """Stop the capture thread and release camera."""
        self.running = False
        if self.capture_thread:
            self.capture_thread.join()
        if self.cap:
            self.cap.release()
        logger.info(f"[Camera {self.camera_index}] Stopped")


# ------------------------ HTML PAGE GENERATION ------------------------- #
# HTML page generation has been moved to dual_camera_page.py


# ------------------------ HTTP HANDLER ------------------------- #
class DualStreamingHandler(server.BaseHTTPRequestHandler):
    active_connections = 0

    def do_GET(self):
        if self.path == "/" or self.path == "/index.html":
            # Serve dynamically generated main page
            content = generate_html_page(
                CAMERA_INDEXES, get_camera_config
            ).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.send_header("Content-Length", str(len(content)))
            self.end_headers()
            self.wfile.write(content)

        elif self.path == "/stream0.mjpg":
            self._stream_camera(
                camera_relays[0] if len(camera_relays) > 0 else None, 0
            )

        elif self.path == "/stream1.mjpg":  # Keep this path but serve camera 2
            self._stream_camera(
                camera_relays[1] if len(camera_relays) > 1 else None, 2  # Camera 2 data
            )

        else:
            # 404 for unknown paths
            self.send_error(404)

    def _stream_camera(self, relay, camera_num):
        """Stream frames from a specific camera relay."""
        if relay is None:
            self.send_error(503, f"Camera {camera_num} not available")
            return

        DualStreamingHandler.active_connections += 1
        logger.info(
            f"New client for camera {camera_num} from {self.client_address[0]}. "
            f"Active: {DualStreamingHandler.active_connections}"
        )

        self.send_response(200)
        self.send_header("Age", "0")
        self.send_header("Cache-Control", "no-cache, private")
        self.send_header("Pragma", "no-cache")
        self.send_header(
            "Content-Type", "multipart/x-mixed-replace; boundary=FRAME"
        )
        self.end_headers()

        try:
            while True:
                frame = relay.get_frame()
                if frame is not None:
                    self.wfile.write(b"--FRAME\r\n")
                    self.send_header("Content-Type", "image/jpeg")
                    self.send_header("Content-Length", str(len(frame)))
                    self.end_headers()
                    self.wfile.write(frame)
                    self.wfile.write(b"\r\n")
        except Exception as e:
            logger.warning(f"Camera {camera_num} client disconnected: {e}")
        finally:
            DualStreamingHandler.active_connections -= 1
            logger.info(
                f"Camera {camera_num} client disconnected. "
                f"Active: {DualStreamingHandler.active_connections}"
            )

    def log_message(self, format, *args):
        # Suppress default HTTP logging (we have our own)
        return


# ------------------------ MAIN ------------------------- #
class ThreadedHTTPServer(socketserver.ThreadingMixIn, server.HTTPServer):
    allow_reuse_address = True
    daemon_threads = True


camera_relays = []


def main():
    global camera_relays

    logger.info("=== Dual Camera Streaming Server ===")
    logger.info(f"Attempting to use cameras: {CAMERA_INDEXES}")

    # Initialize camera relays
    for cam_idx in CAMERA_INDEXES:
        try:
            relay = MediaRelay(cam_idx)
            relay.start_capture()
            camera_relays.append(relay)
            logger.info(f"✓ Camera {cam_idx} initialized successfully")
        except Exception as e:
            logger.error(f"✗ Camera {cam_idx} failed to initialize: {e}")
            camera_relays.append(None)  # Placeholder for failed cameras

    if not any(camera_relays):
        logger.error("No cameras could be initialized. Exiting.")
        return

    # Start HTTP server
    try:
        httpd = ThreadedHTTPServer(("", 8000), DualStreamingHandler)
        logger.info("Server starting on http://0.0.0.0:8000")
        logger.info("Available endpoints:")
        if camera_relays[0]:
            logger.info("  Camera 0: http://0.0.0.0:8000/stream0.mjpg")
        if len(camera_relays) > 1 and camera_relays[1]:
            logger.info("  Camera 1: http://0.0.0.0:8000/stream1.mjpg")
        logger.info("  Dual view: http://0.0.0.0:8000/")

        httpd.serve_forever()

    except KeyboardInterrupt:
        logger.info("Shutting down...")
    finally:
        # Cleanup
        for relay in camera_relays:
            if relay:
                relay.stop_capture()


if __name__ == "__main__":
    main()
