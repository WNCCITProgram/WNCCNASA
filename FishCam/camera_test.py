#!/usr/bin/env python3
"""
Filename: camera_test.py
Description: Test and report the FPS and resolution of a USB camera using OpenCV.
Detects available cameras, opens the first working one, and prints its actual settings.
"""

import cv2
import logging
import os
import json
import sys
import platform

# Setup logging to console only
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s"
)


def get_camera_backend():
    """Return appropriate camera backend for the current platform."""
    system = platform.system().lower()
    if system == 'linux':
        return cv2.CAP_V4L2
    elif system == 'windows':
        return cv2.CAP_DSHOW  # DirectShow for Windows
    else:
        return 0  # Default backend for macOS and others


def list_working_cameras(max_index=10, test_frames=3):
    """Return a list of all working camera indexes (0..max_index)."""
    backend = get_camera_backend()
    backend_name = "V4L2" if backend == cv2.CAP_V4L2 else "DirectShow" if backend == cv2.CAP_DSHOW else "Default"
    working = []
    for cam_idx in range(max_index + 1):
        logging.info(f"Testing camera {cam_idx} with {backend_name}...")
        cap = cv2.VideoCapture(cam_idx, backend)
        if not cap.isOpened():
            logging.debug(f"Camera {cam_idx} could not be opened.")
            cap.release()
            continue
        good = False
        for _ in range(test_frames):
            ret, frame = cap.read()
            if ret and frame is not None:
                good = True
                break
        if good:
            logging.info(f"✓ Working camera index {cam_idx}")
            working.append(cam_idx)
        else:
            logging.warning(f"Camera {cam_idx} opened but produced no frames")
        cap.release()
    return working


def print_camera_info(camera_index):
    """Open camera and print its actual FPS and resolution."""
    backend = get_camera_backend()
    cap = cv2.VideoCapture(camera_index, backend)
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
    Try a list of common resolutions and FPS values.
    Print only the ones that are accepted by the camera.
    """
    common_resolutions = [
        (320, 240),
        (640, 480),
        (800, 600),
        (1024, 768),
        (1280, 720),
        (1280, 1024),
        (1600, 1200),
        (1920, 1080),
    ]
    common_fps = [5, 10, 15, 20, 24, 25, 30, 60]
    cap = cv2.VideoCapture(camera_index, get_camera_backend())
    if not cap.isOpened():
        print(f"Could not open camera {camera_index}.")
        return

    print(f"\nSupported configurations for camera {camera_index}:")
    print(f"{'Resolution':>12} | {'FPS':>6}")
    print("-" * 25)

    working_configs = []

    for width, height in common_resolutions:
        # Set resolution and try 20 FPS (to match JSON output)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        cap.set(cv2.CAP_PROP_FPS, 20)
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
        print(
            "No configurations matched exactly. Camera may only support specific resolutions."
        )
        print("\nActual camera behavior (showing what camera reports):")
        print(f"{'Requested':>12} | {'Camera Reports':>15}")
        print("-" * 32)
        # Show a few examples of what the camera actually does
        for width, height in common_resolutions[
            :4
        ]:  # Just test first 4 resolutions
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
            actual_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            actual_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            print(f"{width}x{height: <5} | {actual_width}x{actual_height: <6}")

    cap.release()


def probe_camera_resolutions(camera_index, resolutions=None):
    """Return a dict of supported resolutions for a camera index.

    We consider a resolution "supported" if after setting width/height the
    camera reports exactly those values. FPS reported is whatever the device
    returns after setting 20 FPS (to match console output).
    """
    if resolutions is None:
        resolutions = [
            (320, 240),
            (640, 480),
            (800, 600),
            (1024, 768),
            (1280, 720),
            (1280, 1024),
            (1600, 1200),
            (1920, 1080),
        ]

    cap = cv2.VideoCapture(camera_index, get_camera_backend())
    if not cap.isOpened():
        return {"index": camera_index, "error": "cannot_open"}

    # First get default info with same settings as print_camera_info
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 800)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 600)
    cap.set(cv2.CAP_PROP_FPS, 20)
    default_info = {
        "width": int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
        "height": int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
        "fps": cap.get(cv2.CAP_PROP_FPS),
    }

    supported = []
    for (w, h) in resolutions:
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, w)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, h)
        cap.set(cv2.CAP_PROP_FPS, 20)  # Try to set 20 FPS like console mode
        actual_w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        actual_h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        if actual_w == w and actual_h == h:
            fps = cap.get(cv2.CAP_PROP_FPS)
            supported.append({"width": w, "height": h, "fps": fps})

    cap.release()
    return {"index": camera_index, "default": default_info, "supported_resolutions": supported}


def probe_all_cameras(max_index=10):
    """Probe all camera indexes up to max_index and return JSON-serializable data."""
    results = []
    working = list_working_cameras(max_index=max_index)
    for idx in working:
        results.append(probe_camera_resolutions(idx))
    return {"cameras": results, "count": len(results)}


if __name__ == "__main__":
    try:
        max_idx = int(os.environ.get("CAM_MAX_INDEX", "8"))
    except ValueError:
        max_idx = 8

    print("Camera Test Utility (OpenCV)")
    print("=============================")
    
    # Always probe cameras and save to JSON
    data = probe_all_cameras(max_index=max_idx)
    json_output = json.dumps(data, indent=2)
    
    # Save to camera_info.json
    try:
        with open("camera_info.json", 'w') as f:
            f.write(json_output)
        print("Camera information saved to: camera_info.json")
    except IOError as e:
        print(f"Error saving to camera_info.json: {e}")

    working = list_working_cameras(max_index=max_idx)
    if not working:
        print("No working USB camera detected!")
        print("Please check connections and permissions.")
    else:
        print("Working camera indexes:", ", ".join(map(str, working)))
        print()
        
        # Show info for ALL working cameras, not just the first
        for i, cam_idx in enumerate(working):
            if i > 0:
                print("\n" + "="*50)
            print(f"Camera {cam_idx} Details:")
            print_camera_info(cam_idx)
            scan_supported_resolutions_and_fps(cam_idx)
