#!/usr/bin/env python3
"""
File: main_app.py
Author: William Loring
Created on: 2025-07-20

Description: A Flask web application to view MJPEG streams from remote devices.

This Flask application creates a web interface to view video streams from
remote cameras or streaming servers. It can connect to the Picamera2 streaming
server running on a Raspberry Pi and display the video feed on any device
with a web browser.

The application provides:
- A web interface to view the remote stream
- Configuration options for different stream sources
- Responsive design for various devices
"""

# Import necessary libraries
from flask import Flask, render_template, request, redirect, url_for, Response, jsonify
import os
import logging
import logging.handlers
import threading  # For running multiple tasks at the same time
import time
import queue  # For passing data between threads safely
from typing import Dict, Union  # For type hints - helps catch errors and makes code clearer
from cached_relay import CachedMediaRelay
from media_relay import MediaRelay

# ========== LOGGING SETUP ==========
# Logging is like keeping a diary of what the program does
# It helps us debug problems and understand what happened when things go wrong

# Create a "logs" folder to store application log files
LOG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
os.makedirs(LOG_DIR, exist_ok=True)  # Create folder if it doesn't exist
LOG_FILE = os.path.join(LOG_DIR, "main_app.log")

# Set up automatic log file rotation
# This creates a new log file each day and keeps 7 days of history
# Think of it like a spiral notebook where you start a new page each day
rotating_handler = logging.handlers.TimedRotatingFileHandler(
    LOG_FILE, when="midnight", interval=1, backupCount=7, encoding="utf-8"
)

# Customize how rotated log files are named (main_app.2025-08-14.log)
rotating_handler.suffix = "%Y-%m-%d.log"
import re
rotating_handler.extMatch = re.compile(r"^\d{4}-\d{2}-\d{2}\.log$")

# Set the format for log messages: timestamp, level, message
# This makes log entries look like: "2025-01-19 14:30:15 INFO Camera connected successfully"
formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
rotating_handler.setFormatter(formatter)

# Configure the main logger to use our rotating file handler
logger = logging.getLogger()
logger.setLevel(logging.INFO)  # Only log INFO level and above (INFO, WARNING, ERROR)
logger.addHandler(rotating_handler)

logging.info("Logging initialized with rotation - keeping 7 days of logs")

# ========== FLASK APP SETUP ==========
# Flask is a web framework - it handles HTTP requests and responses
# Think of it as the "receptionist" for our web application

# Create the Flask web application
# static_url_path sets where CSS, JS, and image files are served from
app = Flask(__name__, static_url_path="/aquaponics/static")

# Configure for running under IIS (Internet Information Services)
# This allows the app to work correctly when accessed via /aquaponics
# IIS is Microsoft's web server software
app.config["APPLICATION_ROOT"] = os.environ.get("APPL_VIRTUAL_PATH", "/")

# ========== CAMERA CONFIGURATION ==========
# These are the default settings for connecting to the camera
# Think of these like the "phone number" and "address" for the camera

# Default settings for the camera server
# Change these values to match your camera's IP address and port
DEFAULT_STREAM_HOST = "172.16.1.200"  # IP address of the camera/Raspberry Pi
DEFAULT_STREAM_PORT = 8000             # Port the camera server is listening on
DEFAULT_STREAM_PATH = "/stream.mjpg"   # URL path to the video stream

# ========== CACHE CONFIGURATION CONSTANTS ==========
# These control how the frame caching system behaves
# The cache acts like a DVR buffer to smooth out connection problems

WIRELESS_CACHE_DURATION = 15.0    # seconds - keep 15 seconds of frames for wireless cameras
WIRELESS_SERVE_DELAY = 2.0        # seconds - 2 second delay for wireless stability
WIRED_SERVE_DELAY = 0.5           # seconds - shorter delay for stable wired connections

# ========== STREAM PROXY CONSTANTS ==========
# These control the stream proxy behavior

WARMUP_TIMEOUT = 15        # seconds - how long to wait for relay to connect initially
MAX_CONSECUTIVE_TIMEOUTS = 10  # number of timeouts before giving up on client
QUEUE_TIMEOUT = 15         # seconds - how long to wait for each frame


# ========== GLOBAL RELAY MANAGEMENT ==========
# These variables are shared across the entire application
# They keep track of all the video streams we're managing

# Dictionary to store media relay instances for different camera URLs
# Key = camera URL, Value = MediaRelay or CachedMediaRelay object
_media_relay: Dict[str, Union[MediaRelay, CachedMediaRelay]] = {}
_relay_lock = threading.Lock()  # Protects the relay dictionary from multiple threads


def get_media_relay(stream_url: str) -> Union[MediaRelay, CachedMediaRelay]:
    """
    Get or create a media relay for the given camera stream URL.
    Now uses caching for better wireless stability.
    
    This is like a "relay factory" - if we already have a relay for this camera,
    return it. If not, create a new one.
    
    Args:
        stream_url: The full URL to the camera stream
        
    Returns:
        Either a MediaRelay (for wired cameras) or CachedMediaRelay (for wireless)
    """
    with _relay_lock:  # Make sure only one thread can modify the relay dictionary at a time
        if stream_url not in _media_relay:
            # Determine if this is likely a wireless camera (adjust logic as needed)
            is_wireless = DEFAULT_STREAM_HOST in stream_url  # Your Pi camera IP

            if is_wireless:
                # Use cached relay for wireless cameras
                # Wireless connections are unreliable, so we use caching for stability
                delay = WIRELESS_SERVE_DELAY
                cache_duration = WIRELESS_CACHE_DURATION
                logging.info(f"Creating cached relay for wireless camera: {stream_url}")
                
                relay = CachedMediaRelay(
                    upstream_url=stream_url,
                    cache_duration=cache_duration,
                    serve_delay=delay
                )
            else:
                # Use legacy relay for wired cameras (if you want to keep some as legacy)
                # Wired connections are more reliable, so we can use the simpler relay
                logging.info(f"Creating legacy relay for wired camera: {stream_url}")
                relay = MediaRelay(stream_url)
                
            relay.start()  # Start the relay's background thread
            _media_relay[stream_url] = relay  # Store it for future use
            logging.info(f"Created media relay for {stream_url}")
        
        return _media_relay[stream_url]


# ========== WEB ROUTES (URLs) ==========
# These functions handle different URLs that users can visit
# Each @app.route decorator creates a new webpage or API endpoint

@app.route("/aquaponics", methods=["GET", "POST"])
def index():
    """
    Main page route - displays the aquaponics dashboard
    Accessible at: http://yourserver/aquaponics
    
    This is like the "front door" of our web application
    """
    # Use the default camera settings
    host = DEFAULT_STREAM_HOST
    port = DEFAULT_STREAM_PORT
    path = DEFAULT_STREAM_PATH
     
    # Generate URL for the stream proxy (this ensures all streams go through our relay)
    # url_for() creates the correct URL even if we're running under /aquaponics
    stream_url = url_for("stream_proxy", host=host, port=port, path=path)
    logging.info(f"Serving main page with stream URL: {stream_url}")
    
    # Render the HTML template with the stream URL
    # This loads the HTML file and fills in variables like {{stream_url}}
    return render_template("index.html", 
                         host=host, 
                         port=port, 
                         path=path, 
                         stream_url=stream_url)


@app.route("/aquaponics/about")
def about():
    """
    About page route
    Accessible at: http://yourserver/aquaponics/about
    """
    return render_template("about.html")


@app.route("/aquaponics/contact", methods=["GET"])
def contact():
    """
    Contact page route for the WNCC STEM Club
    Accessible at: http://yourserver/aquaponics/contact
    """
    return render_template("contact.html")


@app.route("/aquaponics/sensors")
def sensors():
    """
    Sensors page route - displays sensor data and charts
    Accessible at: http://yourserver/aquaponics/sensors
    """
    return render_template("sensors.html")


@app.route("/aquaponics/stream_proxy")
def stream_proxy():
    """
    Stream proxy route - this is where the actual video stream is served
    All video requests go through this to use the media relay system
    
    This is the "heart" of our streaming system - it connects browsers to camera feeds
    
    URL parameters:
    - host: Camera IP address
    - port: Camera port number  
    - path: URL path on camera server
    """
    # Get camera parameters from URL (with defaults)
    # request.args.get() safely gets URL parameters
    host = request.args.get("host", DEFAULT_STREAM_HOST)
    port = int(request.args.get("port", DEFAULT_STREAM_PORT))
    path = request.args.get("path", DEFAULT_STREAM_PATH)

    # Build the complete camera URL
    stream_url = f"http://{host}:{port}{path}"

    # Get the media relay for this camera (creates one if needed)
    relay = get_media_relay(stream_url)
    client_queue = relay.add_client()  # Add this browser as a client

    def generate():
        """
        Generator function that yields video data to the browser
        This runs in the background for each connected browser
        
        A generator is like a conveyor belt that produces video frames one at a time
        instead of loading everything into memory at once
        """
        # Wait for the relay to have a valid frame (upstream connected)
        waited = 0
        while relay.last_frame is None and waited < WARMUP_TIMEOUT:
            time.sleep(0.1)  # Check every 100 milliseconds
            waited += 0.1
        if relay.last_frame is None:
            logging.warning(f"Relay did not connect upstream in {WARMUP_TIMEOUT}s; client may disconnect.")

        try:
            consecutive_timeouts = 0
            
            # Main loop - continuously send video frames to the browser
            while True:
                try:
                    # Wait for video data with shorter timeout but more retries
                    chunk = client_queue.get(timeout=QUEUE_TIMEOUT)
                    consecutive_timeouts = 0  # Reset on successful receive

                    # None indicates an error from the relay
                    if chunk is None:
                        logging.warning("Media relay indicated error, closing client connection")
                        break

                    yield chunk  # Send this chunk to the browser

                except queue.Empty:
                    # No data received within timeout period
                    consecutive_timeouts += 1
                    logging.debug(f"Client queue timeout #{consecutive_timeouts} (waited {QUEUE_TIMEOUT}s) for {stream_url}")
                    
                    # Timeout - check if relay is still running
                    if not relay.running:
                        logging.warning("Media relay stopped, closing client connection")
                        break
                    if consecutive_timeouts >= MAX_CONSECUTIVE_TIMEOUTS:
                        logging.warning(f"Too many consecutive timeouts ({consecutive_timeouts * QUEUE_TIMEOUT}s total), closing client connection")
                        break
                    
                    # Log periodic timeout info for debugging
                    if consecutive_timeouts % 3 == 0:  # Every 45 seconds
                        logging.info(f"Client timeout #{consecutive_timeouts}, relay still running, continuing...")
                    # Continue waiting for data
                    continue

        except Exception as e:
            logging.error(f"Error in stream generator: {e}")
        finally:
            # Always clean up when client disconnects
            # This is like hanging up the phone when the conversation ends
            relay.remove_client(client_queue)
            logging.info("Client disconnected while serving /aquaponics/stream_proxy")

    # Return HTTP response with video stream
    # Response() creates a streaming HTTP response that sends data continuously
    return Response(
        generate(),
        mimetype=relay.content_type,  # Set correct MIME type for MJPEG
        headers={
            # Prevent caching of video stream
            # These headers tell browsers not to store the video in cache
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache",
            "Expires": "0",
        },
    )


@app.route("/aquaponics/health")
def health():
    """
    Health check endpoint - useful for monitoring if the app is running
    Returns JSON with status information
    
    This is like taking the application's "pulse" to make sure it's alive
    """
    return {"status": "ok", "message": "Stream viewer is running"}


@app.route("/aquaponics/debug_stream")
def debug_stream():
    """
    Debug endpoint - provides detailed information about the stream connection
    This is like looking "under the hood" to see what's happening
    """
    host = request.args.get("host", DEFAULT_STREAM_HOST)
    port = int(request.args.get("port", DEFAULT_STREAM_PORT))
    path = request.args.get("path", DEFAULT_STREAM_PATH)
    stream_url = f"http://{host}:{port}{path}"
    
    # Collect diagnostic information
    debug_info = {
        "timestamp": time.time(),
        "stream_url": stream_url,
        "relay_exists": stream_url in _media_relay,
        "active_relays_total": len(_media_relay)
    }
    
    # Add relay-specific information if it exists
    if stream_url in _media_relay:
        relay = _media_relay[stream_url]
        debug_info.update({
            "relay_running": relay.running,
            "connected_clients": len(relay.clients),
            "has_last_frame": relay.last_frame is not None,
            "content_type": relay.content_type,
            "last_frame_size": len(relay.last_frame) if relay.last_frame else 0
        })
    
    return debug_info


@app.route("/aquaponics/relay_status")
def relay_status():
    """
    Debug endpoint - shows information about active media relays
    Useful for troubleshooting connection issues
    
    This gives us a "bird's eye view" of all active video streams
    """
    status = {}
    with _relay_lock:
        for stream_url, relay in _media_relay.items():
            status[stream_url] = {
                "running": relay.running,
                "connected_clients": len(relay.clients),
                "content_type": relay.content_type,
                "has_last_frame": relay.last_frame is not None,
            }

    return {"active_relays": len(_media_relay), "relays": status}


@app.route("/aquaponics/warmup_relay")
def warmup_relay():
    """
    Pre-warm the media relay to reduce initial connection delay
    This can be called before users visit the main page to speed up loading
    
    Think of this like warming up a car engine before driving -
    it makes everything work faster when you actually need it
    """
    host = request.args.get("host", DEFAULT_STREAM_HOST)
    port = int(request.args.get("port", DEFAULT_STREAM_PORT))
    path = request.args.get("path", DEFAULT_STREAM_PATH)

    stream_url = f"http://{host}:{port}{path}"

    try:
        # Start the media relay
        relay = get_media_relay(stream_url)

        # Wait a moment for connection to establish
        time.sleep(0.5)

        return {
            "status": "success",
            "message": "Relay warmed up",
            "running": relay.running,
            "has_last_frame": relay.last_frame is not None,
        }
    except Exception as e:
        logging.error(f"Error warming up relay: {e}")
        return {"status": "error", "message": str(e)}, 500


@app.route("/aquaponics/cache_status")
def cache_status():
    """
    Get status of all frame caches and relays - returns JSON only
    
    This endpoint provides detailed statistics about the caching system
    for monitoring and debugging purposes
    """
    status = {}
    
    with _relay_lock:
        for url, relay in _media_relay.items():
            try:
                if isinstance(relay, CachedMediaRelay):
                    # New cached relay with full status
                    status[url] = relay.get_status()
                else:
                    # Legacy relay - create compatible status
                    status[url] = {
                        'type': 'legacy_relay',
                        'relay_running': getattr(relay, 'running', False),
                        'client_count': len(getattr(relay, 'clients', [])),
                        'last_frame_available': getattr(relay, 'last_frame', None) is not None
                    }
            except Exception as e:
                logging.error(f"Error getting status for {url}: {e}")
                status[url] = {
                    'type': 'error',
                    'error': str(e),
                    'relay_running': False,
                    'client_count': 0
                }
                
    return jsonify(status)  # Convert Python dictionary to JSON format


# ========== TEMPLATE HELPER FUNCTIONS ==========

@app.context_processor
def inject_urls():
    """
    Make application root URL available to all templates
    This helps with generating correct URLs when running under /aquaponics
    
    This is like giving every HTML template a "business card" with our address
    """
    return dict(app_root=app.config["APPLICATION_ROOT"])


# ========== CLEANUP FUNCTIONS ==========

def cleanup_relays():
    """
    Clean up all media relays when the application shuts down
    This ensures camera connections are properly closed
    
    This is like turning off all the lights and locking the doors when leaving work
    """
    with _relay_lock:
        for relay in _media_relay.values():
            relay.stop()  # Stop each relay's background thread
        _media_relay.clear()  # Empty the dictionary
    logging.info("All media relays cleaned up")


# ========== MAIN PROGRAM ==========
# This section only runs when the script is executed directly (not imported)

if __name__ == "__main__":
    import atexit
    
    # Register cleanup function to run when program exits
    # This ensures proper shutdown even if the program is terminated
    atexit.register(cleanup_relays)

    # Print startup information to help users know how to access the application
    print("Starting Flask Stream Viewer with Media Relay...")
    print(f"Default camera server: {DEFAULT_STREAM_HOST}:{DEFAULT_STREAM_PORT}")
    print("Open your web browser and go to: http://localhost:5000")
    print("Or access from other devices at: http://<this-device-ip>:443")
    print("Check relay status at: http://localhost:443/aquaponics/relay_status")

    # Start the Flask web server
    # host="0.0.0.0" means accept connections from any IP address (not just localhost)
    # port=5000 is the port the web server will listen on
    # debug=True provides detailed error messages (turn off in production)
    app.run(host="0.0.0.0", port=5000, debug=True)
