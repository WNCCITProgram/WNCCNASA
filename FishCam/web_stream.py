# ============================================================================
# File: web_stream.py (OPTIMIZED VERSION)
# Author: William Loring
#
# Description:
#   This program creates a web server that captures video from a USB camera
#   and streams it live to web browsers. Students can view the camera feed
#   by opening a web browser and going to the server's address.
#
#   OPTIMIZATIONS FOR SPEED AND BANDWIDTH:
#   - Reduced default resolution to 640x480 (from 1280x720) for less bandwidth
#   - Added JPEG quality control (85% quality) to balance size vs quality
#   - Frame rate limiting to max 15 FPS to reduce bandwidth usage
#   - Camera warm-up sequence to reduce initial lag
#   - Optional known camera index to skip detection (faster startup)
#   - Responsive web page design with CSS styling
#   - Overlay label feature: displays "WNCC STEM Club" for 60 seconds every 15 minutes
#
#   This file is heavily commented for beginning Python programmers in a
#   community college setting. It explains programming concepts, real-world
#   hardware issues, and how web streaming works.
#
# Educational Topics Covered:
#   - Object-Oriented Programming (classes and methods)
#   - Threading (running multiple tasks at the same time)
#   - HTTP servers and web protocols
#   - Camera/video capture with OpenCV
#   - Error handling with try/except blocks
#   - Network programming basics
#   - Real-world troubleshooting and hardware limitations
#   - Performance optimization techniques
#   - Real-time image overlay and text rendering
# ============================================================================


# --------------------------- IMPORTS (Libraries) -------------------------- #
# These are modules (libraries) that add extra features to Python

import logging  # For recording error messages and debug info
import os  # For file system operations and path handling
import re  # For regular expressions (pattern matching)
from logging.handlers import (
    TimedRotatingFileHandler,
)  # For rotating log files by day
import socketserver  # For creating network servers that handle multiple clients
import time  # For adding delays and timing operations
from http import server  # For creating HTTP web servers
from threading import (
    Condition,  # For synchronizing threads (like a traffic signal)
    Thread,  # For running background tasks
)  # For running multiple tasks simultaneously
from typing import Optional  # For type hints

from web_stream_page import PAGE

# Import OpenCV library for camera control
# Install: sudo apt install python3-opencv
# or pip install opencv-python
import cv2

# --------------------------- LOGGING SETUP -------------------------------- #
# Logging is like a diary for your program. It records what happens and any errors.
# This helps you debug problems and see what your code is doing.
#
# We use TimedRotatingFileHandler to create a new log file each day and keep 7 days of logs.
# Each log file will be named like
# 'web_stream.log', 'web_stream.2024-08-05.log', etc.

# Get the root logger
logger = logging.getLogger()

# Clear any existing handlers to prevent duplicates
logger.handlers.clear()

log_formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")

# Create logs directory relative to this script's location
script_dir = os.path.dirname(os.path.abspath(__file__))
logs_dir = os.path.join(script_dir, "logs")
os.makedirs(logs_dir, exist_ok=True)

# Create the log file path
log_file_path = os.path.join(logs_dir, "web_stream.log")

file_handler = TimedRotatingFileHandler(
    log_file_path, when="midnight", interval=1, backupCount=7
)
file_handler.setFormatter(log_formatter)
# Add date to rotated log files in format: web_stream.YYYY-MM-DD.log
file_handler.suffix = ".%Y-%m-%d.log"
file_handler.extMatch = re.compile(r"^\.\d{4}-\d{2}-\d{2}\.log$")

console_handler = logging.StreamHandler()
console_handler.setFormatter(log_formatter)

# Configure logging with our handlers
logger.setLevel(logging.INFO)
logger.addHandler(file_handler)
logger.addHandler(console_handler)

# Prevent propagation to avoid duplicate messages
logger.propagate = False

# ------------------------ CONFIGURATION VARIABLES ------------------------- #
# These are constants (values that don't change) that control how the camera behaves.
# You can change these to adjust the video quality and frame rate.

FRAME_RATE = 10  # How many pictures per second we want the camera to take
# Note: Some cameras may ignore this setting and use their own preferred rate.
# This is normal hardware behavior - the camera will tell us what it's actually using.
# Frame rate limiting for bandwidth control
MAX_STREAM_FPS = (
    10  # Maximum FPS to send to clients (independent of camera FPS)
)

VIDEO_WIDTH = 1280
VIDEO_HEIGHT = 720

# JPEG compression quality (0-100, higher = better quality but more bandwidth)
JPEG_QUALITY = 85  # Good balance between quality and bandwidth

# Skip camera detection if you know your camera index (faster startup)
# Set to 0, 1, 2, etc. if you know your camera index, or None to auto-detect
KNOWN_CAMERA_INDEX = 0

# Label overlay configuration
ENABLE_LABEL_OVERLAY = True  # Set to False to completely disable label feature
LABEL_TEXT = "WNCC STEM Club Meeting Thursday at 4 in C1"  # Text to display on video
LABEL_CYCLE_MINUTES = 10  # Show label every X minutes
LABEL_DURATION_SECONDS = 30  # Show label for X seconds each cycle
LABEL_FONT_SCALE = 0.8  # Size of the label text
# Background transparency (0.0 = transparent, 1.0 = opaque)
LABEL_TRANSPARENCY = 0.7
# Text transparency for overlays (0.0 = fully transparent, 1.0 = fully opaque)
TEXT_TRANSPARENCY = 0.9
# Text color for overlays (BGR)
TEXT_COLOR = (0, 85, 204)  # Burnt orange in BGR for OpenCV



# --------------------- MEDIA RELAY (FRAME BROADCASTER) -------------------- #
class MediaRelay:
    """
    MediaRelay pattern for sharing a single webcam source across multiple connections.
    This class captures frames from the camera in a background thread and allows
    multiple clients to subscribe and receive the latest frame.

    Key Concepts:
    - Only one thread talks to the camera (saves resources)
    - All clients (web browsers) get the latest frame from the relay
    - Uses threading.Condition to let clients wait for new frames
    """

    def __init__(self):
        # This will store the most recent camera frame as JPEG bytes
        self.frame = None

        # Condition is like a traffic light for threads: it lets them wait for new frames
        self.condition = Condition()

        # Control variables for the camera and background thread
        self.running = False
        self.cap = None
        self.capture_thread = None

        # Label timing control (only initialize if label overlay is enabled)
        if ENABLE_LABEL_OVERLAY:
            self.label_start_time = time.time()  # When we started the current cycle
            self.label_shown = False  # Track if label is currently being shown

    # ------------------------ START CAPTURE ------------------------------- #
    def start_capture(self, camera_index=0):
        # Start capturing video from the USB camera
        # camera_index: 0 = first camera, 1 = second, etc.
        logging.info(
            f"[MediaRelay] Opening camera {camera_index} with V4L2 backend..."
        )
        # Open camera using OpenCV and the V4L2 backend (best for Raspberry Pi)
        self.cap = cv2.VideoCapture(camera_index, cv2.CAP_V4L2)
        if not self.cap.isOpened():
            # If camera failed to open, raise an error and stop the program
            raise RuntimeError(
                f"Could not open camera {camera_index} with V4L2 backend"
            )
        logging.info(
            f"[MediaRelay] ✓ Camera {camera_index} opened successfully with V4L2"
        )
        # Set camera resolution and frame rate
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, VIDEO_WIDTH)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, VIDEO_HEIGHT)
        self.cap.set(cv2.CAP_PROP_FPS, FRAME_RATE)
        # Check what settings the camera actually accepted (hardware may override)
        actual_width = self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        actual_height = self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
        actual_fps = self.cap.get(cv2.CAP_PROP_FPS)
        logging.info(
            f"[MediaRelay] Requested settings: {VIDEO_WIDTH}x{VIDEO_HEIGHT} @ {FRAME_RATE} FPS"
        )
        logging.info(
            f"[MediaRelay] Actual camera settings: {int(actual_width)}x{int(actual_height)} @ {actual_fps} FPS"
        )
        if actual_fps != FRAME_RATE:
            logging.warning(
                f"[MediaRelay] Note: Camera is using {actual_fps} FPS instead of requested {FRAME_RATE} FPS"
            )
            logging.info(
                "[MediaRelay] This is normal - many cameras have fixed frame rates or limited options"
            )
            logging.info("[MediaRelay] The streaming will still work properly")

        # Warm up the camera by capturing and discarding a few frames
        # This helps reduce initial lag and ensures stable image quality
        logging.info("[MediaRelay] Warming up camera...")
        for i in range(5):
            ret, _ = self.cap.read()
            if not ret:
                logging.warning(
                    f"[MediaRelay] Frame {i+1} failed during warm-up"
                )
            time.sleep(0.1)  # Small delay between warm-up frames
        logging.info("[MediaRelay] Camera warm-up complete")

        # Start the background thread to capture frames
        self.running = True
        self.capture_thread = Thread(target=self._capture_frames)
        self.capture_thread.daemon = True
        self.capture_thread.start()

    # ------------------------ CAPTURE FRAMES ------------------------------- #
    def _capture_frames(self):
        """This method runs in a background thread and keeps grabbing frames from the camera
        It stores the latest frame and notifies all waiting clients"""
        frame_time = (
            1.0 / MAX_STREAM_FPS
        )  # Calculate time between frames for rate limiting
        last_frame_time = 0

        while self.running:
            if self.cap is not None:
                current_time = time.time()

                # Rate limiting: only process frames at the specified max FPS
                if current_time - last_frame_time < frame_time:
                    time.sleep(0.001)  # Small sleep to prevent busy waiting
                    continue

                # Try to read one frame from the camera
                ret, frame = self.cap.read()
                if ret:
                    # Add WNCC STEM Club label timing logic (only if enabled)
                    if ENABLE_LABEL_OVERLAY:
                        current_cycle_time = current_time - self.label_start_time

                        # Show label for configured duration every configured interval
                        cycle_duration = LABEL_CYCLE_MINUTES * 60  # Convert minutes to seconds
                        if current_cycle_time >= cycle_duration:  # Reset cycle
                            self.label_start_time = current_time
                            current_cycle_time = 0
                            self.label_shown = False

                        # Show label for first X seconds of each cycle
                        show_label = current_cycle_time < LABEL_DURATION_SECONDS

                        # Add overlay text if it's time to show it
                        if show_label:
                            # Add semi-transparent background for better text visibility
                            overlay = frame.copy()

                            # Calculate text size and position
                            font = cv2.FONT_HERSHEY_SIMPLEX
                            thickness = 2

                            # Get text size to position it properly
                            (text_width, text_height), baseline = cv2.getTextSize(
                                LABEL_TEXT, font, LABEL_FONT_SCALE, thickness)

                            # Position in bottom-left corner with some padding
                            x = 20  # 20 pixels from left edge
                            # 20 pixels from bottom edge
                            y = frame.shape[0] - 20

                            # Draw semi-transparent background rectangle
                            cv2.rectangle(overlay,
                                          (x - 10, y - text_height - 10),
                                          (x + text_width + 10, y + 10),
                                          (0, 0, 0), -1)  # Black background

                            # Blend the overlay with the original frame for transparency
                            cv2.addWeighted(
                                overlay, LABEL_TRANSPARENCY, frame, 1 - LABEL_TRANSPARENCY, 0, frame)

                            # Add label text using the configured text color and transparency
                            if TEXT_TRANSPARENCY < 1.0:
                                text_overlay = frame.copy()
                                cv2.putText(text_overlay, LABEL_TEXT, (x, y), font,
                                           LABEL_FONT_SCALE, TEXT_COLOR, thickness)
                                cv2.addWeighted(text_overlay, TEXT_TRANSPARENCY, frame, 1 - TEXT_TRANSPARENCY, 0, frame)
                            else:
                                cv2.putText(frame, LABEL_TEXT, (x, y), font,
                                           LABEL_FONT_SCALE, TEXT_COLOR, thickness)

                            # Log when label appears (only once per state change)
                            if not self.label_shown:
                                logging.info(
                                    f"[MediaRelay] Label '{LABEL_TEXT}' displayed for {LABEL_DURATION_SECONDS}s")
                                self.label_shown = True
                        else:
                            # Log when label disappears (only once per state change)
                            if self.label_shown:
                                logging.info(
                                    f"[MediaRelay] Label '{LABEL_TEXT}' hidden - next display in {LABEL_CYCLE_MINUTES} minutes")
                                self.label_shown = False

                    # Convert the frame to JPEG format with controlled quality for web streaming
                    encode_params = [cv2.IMWRITE_JPEG_QUALITY, JPEG_QUALITY]
                    _, buffer = cv2.imencode(".jpg", frame, encode_params)
                    frame_bytes = buffer.tobytes()

                    # Notify all clients that a new frame is ready
                    with self.condition:
                        self.frame = frame_bytes
                        self.condition.notify_all()

                    last_frame_time = current_time
                else:
                    # If frame capture failed, wait a tiny bit before trying again
                    time.sleep(0.01)
            else:
                # If camera connection is lost, exit the loop
                break

    # ------------------------- GET FRAME ---------------------------------- #
    def get_frame(self):
        """
        Wait for and return the latest frame (for use by each client).
        Each client (browser) calls this to get the newest frame.
        """
        with self.condition:
            self.condition.wait()  # Wait until a new frame is available
            return self.frame

    def stop(self):
        # Cleanly stop the background thread and release the camera
        self.running = False
        if self.capture_thread:
            self.capture_thread.join()
        if self.cap:
            self.cap.release()


# -------------------- STREAMING HANDLER (Web Requests) -------------------- #
class StreamingHandler(server.BaseHTTPRequestHandler):
    """
    This class handles HTTP requests from web browsers.

    When someone opens a web browser and goes to our server's address,
    their browser sends an HTTP request. This class processes those requests
    and sends back the appropriate response (web page or video stream).

    Key Concepts:
    - Inheritance (this class extends BaseHTTPRequestHandler)
    - HTTP protocol basics (GET requests, response codes, headers)
    - Method overriding (we override do_GET from the parent class)
    - String manipulation and encoding
    - Binary data handling
    """

    # Class variable to track the number of active streaming connections
    active_stream_connections = 0

    # -------------------------- DO GET ------------------------------------ #
    def do_GET(self):
        # This method handles GET requests from browsers (like when you type a URL)
        # It decides what to send back based on the requested path
        if self.path == "/":
            # Redirect root path to the main page
            self.send_response(301)
            self.send_header("Location", "/index.html")
            self.end_headers()
        elif self.path == "/index.html":
            # Send the main HTML page
            content = PAGE.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.send_header("Content-Length", str(len(content)))
            self.end_headers()
            self.wfile.write(content)
        elif self.path == "/stream.mjpg":
            # This is the video stream (MJPEG format)
            # Increment the connection counter and log new connection
            StreamingHandler.active_stream_connections += 1
            logging.info(
                f"New streaming client connected from {self.client_address[0]}. "
                f"Active connections: {StreamingHandler.active_stream_connections}"
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
                    # Get the latest frame from the MediaRelay
                    if relay is None:
                        # If relay is not initialized, break out of the loop
                        break
                    frame = relay.get_frame()
                    if frame is not None:
                        # Send the frame boundary marker
                        self.wfile.write(b"--FRAME\r\n")
                        # Send headers for this JPEG image
                        self.send_header("Content-Type", "image/jpeg")
                        self.send_header("Content-Length", str(len(frame)))
                        self.end_headers()
                        # Send the actual image data
                        self.wfile.write(frame)
                        self.wfile.write(b"\r\n")
            except Exception as e:
                # If the browser disconnects or there's a network error, log it
                logging.warning(
                    "Removed streaming client %s: %s",
                    self.client_address,
                    str(e),
                )
            finally:
                # Decrement the connection counter when client disconnects
                StreamingHandler.active_stream_connections -= 1
                logging.info(
                    f"Streaming client {self.client_address[0]} disconnected. "
                    f"Active connections: {StreamingHandler.active_stream_connections}"
                )
        else:
            # Any other path: send a 404 Not Found error
            self.send_error(404)
            self.end_headers()


# -------------------- STREAMING SERVER (Multi-Client) --------------------- #
class StreamingServer(socketserver.ThreadingMixIn, server.HTTPServer):
    """
    This class creates the web server that handles multiple clients simultaneously.

    Key Concepts:
    - Multiple inheritance (inherits from both ThreadingMixIn and HTTPServer)
    - Mixin classes (ThreadingMixIn adds threading capability)
    - Class attributes (variables that belong to the class, not instances)
    - Server architecture and design patterns

    ThreadingMixIn allows the server to handle multiple browser connections at once.
    Each client gets its own thread and can independently receive the MJPEG stream.
    The MediaRelay object is shared, but frame access is synchronized for thread safety.
    """

    # Class attributes - these apply to all instances of this class

    # Allow reusing the network address immediately after shutdown
    # Without this, you might get "Address already in use" errors
    allow_reuse_address = True

    # Use daemon threads for client connections
    # This means all client threads will close when the main program exits
    daemon_threads = True


# ======================= GLOBAL VARIABLES ================================= #
# Global MediaRelay object that will be initialized in main()
relay: Optional["MediaRelay"] = None


# ====================== MAIN PROGRAM STARTS HERE ========================== #
# This is where the actual program execution begins.
# Everything above this point was just defining classes and functions.
# Now we use those classes to create and run our camera streaming server.


def find_working_camera():
    """
    Find a working camera efficiently.
    Returns the camera index if found, None otherwise.
    """
    # If user specified a known camera index, try that first (fastest startup)
    if KNOWN_CAMERA_INDEX is not None:
        logging.info(f"Trying known camera index {KNOWN_CAMERA_INDEX}...")
        test_cap = cv2.VideoCapture(KNOWN_CAMERA_INDEX, cv2.CAP_V4L2)
        if test_cap.isOpened():
            ret, frame = test_cap.read()
            if ret and frame is not None:
                logging.info(f"✓ Known camera {KNOWN_CAMERA_INDEX} is working")
                test_cap.release()
                return KNOWN_CAMERA_INDEX
            else:
                logging.warning(
                    f"Known camera {KNOWN_CAMERA_INDEX} opens but cannot capture frames"
                )
        else:
            logging.warning(f"Known camera {KNOWN_CAMERA_INDEX} not available")
        test_cap.release()

    # If known camera failed or not specified, search for cameras
    logging.info("Detecting available cameras...")
    for cam_idx in range(4):
        logging.info(f"Testing camera {cam_idx} with V4L2...")
        test_cap = cv2.VideoCapture(cam_idx, cv2.CAP_V4L2)
        if test_cap.isOpened():
            ret, frame = test_cap.read()
            if ret and frame is not None:
                logging.info(f"✓ Found working camera at index {cam_idx}")
                test_cap.release()
                return cam_idx
            else:
                logging.warning(
                    f"Camera {cam_idx} opens but cannot capture frames"
                )
        else:
            logging.info(f"Camera {cam_idx} not available")
        test_cap.release()

    return None


def main():
    global relay  # Declare relay as global so it can be accessed by StreamingHandler

    # Create the MediaRelay (frame broadcaster) object
    # This will manage the camera and share frames with all clients
    relay = MediaRelay()

    # Print status messages to help users understand what's happening
    logging.info("Starting USB camera streaming server with V4L2 backend...")

    # Find a working camera
    working_camera_idx = find_working_camera()

    # Check if we found a working camera
    if working_camera_idx is None:
        # No camera found - print helpful error message and exit
        logging.error("No USB cameras detected with V4L2 backend!")
        logging.error("Please check:")
        logging.error("  - USB camera is connected properly")
        logging.error("  - Camera is not being used by another application")
        logging.error("  - Camera permissions: sudo usermod -a -G video $USER")
        logging.error("  - Available devices: ls -la /dev/video*")
        logging.error("  - V4L2 info: v4l2-ctl --list-devices")
        # Exit the program with error code 1 (means something went wrong)
        exit(1)

    # Start the camera capture
    try:
        # Double-check that we have a valid camera index
        if working_camera_idx is not None:
            # Start capturing frames in the background
            relay.start_capture(camera_index=working_camera_idx)
            logging.info(
                f"Successfully started camera {working_camera_idx} with V4L2 backend (MediaRelay pattern)"
            )
        else:
            # This shouldn't happen if our logic above is correct, but just in case...
            raise RuntimeError("No working camera index found")
    except Exception as e:
        # If camera startup fails, print error and exit
        logging.error(f"Failed to start camera: {e}")
        exit(1)

    # Now start the web server
    try:
        # Create the network address for our server
        # ("", 8000) means:
        # - "" = listen on all available network interfaces (localhost, WiFi, Ethernet)
        # - 8000 = port number (like a channel number for network communication)
        address = ("", 8000)

        # Create the HTTP server object
        # This combines our StreamingHandler (processes requests) with
        # the StreamingServer (manages network connections)
        server = StreamingServer(address, StreamingHandler)

        # Get network information to display to the user
        import socket  # Import here since we only need it once

        hostname = socket.gethostname()  # Get the computer's name
        try:
            # Try to get the computer's IP address on the local network
            local_ip = socket.gethostbyname(hostname)

            # Print connection information for users
            logging.info(f"Streaming server started successfully!")
            logging.info(f"Local access: http://localhost:8000/")
            logging.info(f"Network access: http://{local_ip}:8000/")
            logging.info(f"Raspberry Pi access: http://{hostname}.local:8000/")
        except:
            # If we can't get the IP address, just show localhost
            logging.info("Streaming server started on http://localhost:8000/")

        logging.info("Press Ctrl+C to stop the server")
        logging.info("-" * 50)

        # Start the server and keep it running
        # serve_forever() is a blocking call - the program waits here
        # and processes incoming requests until we stop it
        server.serve_forever()

    except KeyboardInterrupt:
        # This exception occurs when user presses Ctrl+C
        logging.info("Streaming stopped by user")

    finally:
        # This block always runs, even if an error occurred
        # It ensures we clean up resources properly

        # Stop the camera capture thread and close camera connection
        relay.stop()

        logging.info("Cleanup completed. Goodbye!")


# If this script is run directly (not imported), call the main function
if __name__ == "__main__":
    # Configure logging to show messages on the console
    logging.basicConfig(level=logging.INFO)

    # Start the main program
    main()
else:
    # If this script is imported as a module, we don't run the main function
    # This allows other scripts to use the MediaRelay and StreamingServer classes
    logging.info(
        "web_stream.py module imported. Use main() to start the server."
    )
