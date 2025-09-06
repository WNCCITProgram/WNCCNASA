#!/usr/bin/env python3
"""
Filename: camera_test.py
Description: Test and report the FPS and resolution of a USB camera using OpenCV.
Detects available cameras, opens the first working one, and prints its actual settings.
"""

import cv2
import logging
import os

# Setup logging to console only
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s"
)


def find_working_camera(max_index=3):
    """Try camera indices 0 to max_index, return the first working index."""
    for cam_idx in range(max_index + 1):
        logging.info(f"Testing camera {cam_idx} with V4L2...")
        cap = cv2.VideoCapture(cam_idx, cv2.CAP_V4L2)
        if cap.isOpened():
            ret, frame = cap.read()
            if ret and frame is not None:
                logging.info(f"✓ Found working camera at index {cam_idx}")
                cap.release()
                return cam_idx
            else:
                logging.warning(
                    f"Camera {cam_idx} opens but cannot capture frames"
                )
        else:
            logging.info(f"Camera {cam_idx} not available")
        cap.release()
    return None


def print_camera_info(camera_index):
    """Open camera and print its actual FPS and resolution."""
    cap = cv2.VideoCapture(camera_index, cv2.CAP_V4L2)
    if not cap.isOpened():
        print(f"Could not open camera {camera_index}.")
        return
    # Try to set some typical values (these may be ignored by hardware)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 800)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 600)
    cap.set(cv2.CAP_PROP_FPS, 20)
    # Get actual settings
    actual_width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
    actual_height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
    actual_fps = cap.get(cv2.CAP_PROP_FPS)
    print(f"Camera {camera_index} actual settings:")
    print(f"  Resolution: {int(actual_width)}x{int(actual_height)}")
    print(f"  FPS: {actual_fps}")
    cap.release()


def scan_supported_resolutions_and_fps(camera_index):
    """
    Try a list of common resolutions and FPS values, and print only the ones that are accepted by the camera.
    """
    common_resolutions = [
        (320, 240), (640, 480), (800, 600), (1024, 768), (1280, 720), (1280, 1024), (1600, 1200), (1920, 1080)
    ]
    common_fps = [5, 10, 15, 20, 24, 25, 30, 60]
    cap = cv2.VideoCapture(camera_index, cv2.CAP_V4L2)
    if not cap.isOpened():
        print(f"Could not open camera {camera_index}.")
        return
    
    print(f"\nSupported configurations for camera {camera_index}:")
    print(f"{'Resolution':>12} | {'FPS':>6}")
    print("-" * 25)
    
    working_configs = []
    
    for width, height in common_resolutions:
        for fps in common_fps:
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
            cap.set(cv2.CAP_PROP_FPS, fps)
            actual_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            actual_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            actual_fps = cap.get(cv2.CAP_PROP_FPS)
            
            # Only show configurations that work (resolution matches what we requested)
            if actual_width == width and actual_height == height:
                config = f"{width}x{height}"
                if config not in [wc[0] for wc in working_configs]:
                    working_configs.append((config, actual_fps))
                    print(f"{width}x{height: <5} | {actual_fps: <6.1f}")
    
    if not working_configs:
        print("No configurations matched exactly. Camera may only support specific resolutions.")
        print("\nActual camera behavior (showing what camera reports):")
        print(f"{'Requested':>12} | {'Camera Reports':>15}")
        print("-" * 32)
        # Show a few examples of what the camera actually does
        for width, height in common_resolutions[:4]:  # Just test first 4 resolutions
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
            actual_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            actual_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            print(f"{width}x{height: <5} | {actual_width}x{actual_height: <6}")
    
    cap.release()


if __name__ == "__main__":
    print("Camera Test Utility (OpenCV)")
    print("=============================")
    cam_idx = find_working_camera()
    if cam_idx is not None:
        print_camera_info(cam_idx)
        scan_supported_resolutions_and_fps(cam_idx)
    else:
        print("No working USB camera detected!")
        print("Please check connections and permissions.")
