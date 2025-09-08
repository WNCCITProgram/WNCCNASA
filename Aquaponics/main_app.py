#!/usr/bin/env python3
"""
Flask web application that shows two live MJPEG camera streams:
 - Fish Tank (camera 0)
 - Plant Bed (camera 2 mapped as /stream1.mjpg on the Pi side)

Designed with clear comments for learners.
This version keeps:
 - Clean structure
 - Rotating log files (no noisy debug routes)
 - Simple relay caching for efficiency

Does NOT include extra debug endpoints or complex UI logic.
"""

from flask import Flask, render_template, request, url_for, Response
import os
import logging
import logging.handlers
import threading
import time
import queue
from typing import Dict, Union

# Local modules that handle pulling frames from upstream cameras
from cached_relay import CachedMediaRelay   # Relay with small frame cache
from media_relay import MediaRelay          # Basic relay (not used here but available)

# ---------------------------------------------------------------------------
# LOGGING SETUP
# ---------------------------------------------------------------------------
# We log to files so we can review what happened later (errors, starts, etc.)
LOG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
os.makedirs(LOG_DIR, exist_ok=True)

# Base filename (Flask will create one per day using rotation)
LOG_FILE = os.path.join(LOG_DIR, "main_app")

# TimedRotatingFileHandler creates a new log file at midnight and keeps 7 days
handler = logging.handlers.TimedRotatingFileHandler(
    LOG_FILE,
    when="midnight",
    interval=1,
    backupCount=7,
    encoding="utf-8"
)
handler.suffix = "%Y-%m-%d.log"
handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))

# Root logger (shared across modules)
logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(handler)
logging.info("Application start")

# ---------------------------------------------------------------------------
# FLASK APP SETUP
# ---------------------------------------------------------------------------
# static_url_path lets static files be served under /aquaponics/static
app = Flask(__name__, static_url_path="/aquaponics/static")

# APPLICATION_ROOT allows IIS or reverse proxy to mount at /aquaponics
app.config["APPLICATION_ROOT"] = os.environ.get("APPL_VIRTUAL_PATH", "/")

# ---------------------------------------------------------------------------
# CAMERA CONFIGURATION
# ---------------------------------------------------------------------------
# These values describe where the upstream Raspberry Pi (or server) streams live.
# If the Pi's IP changes on the network, update DEFAULT_STREAM_HOST.
DEFAULT_STREAM_HOST = "172.16.1.200"
DEFAULT_STREAM_PORT = 8000

# Paths exposed by the Raspberry Pi streaming script:
#   /stream0.mjpg  -> physical camera index 0 (fish)
#   /stream1.mjpg  -> physical camera index 2 (plants) mapped by your Pi script
DEFAULT_STREAM_PATH_0 = "/stream0.mjpg"  # Fish tank
DEFAULT_STREAM_PATH_1 = "/stream1.mjpg"  # Plant bed

# ---------------------------------------------------------------------------
# RELAY / STREAMING TUNING
# ---------------------------------------------------------------------------
# The relay creates ONE upstream connection per unique camera URL and shares
# frames with all connected viewers. This saves bandwidth and CPU.
WIRELESS_CACHE_DURATION = 15.0   # Seconds of frames to retain (smoothing hiccups)
WIRELESS_SERVE_DELAY = 2.0       # Delay used by CachedMediaRelay to stabilize order
WARMUP_TIMEOUT = 15              # Seconds to wait for first frame before giving up
MAX_CONSECUTIVE_TIMEOUTS = 10    # If client sees this many empty waits, disconnect
QUEUE_TIMEOUT = 15               # Seconds each client waits for a frame before retry

# Dictionary that holds active relay objects keyed by the full upstream URL
_media_relay: Dict[str, Union[MediaRelay, CachedMediaRelay]] = {}
# Lock prevents race conditions if multiple users connect at the same time
_relay_lock = threading.Lock()

# ---------------------------------------------------------------------------
# RELAY FACTORY
# ---------------------------------------------------------------------------
def get_media_relay(stream_url: str) -> Union[MediaRelay, CachedMediaRelay]:
    """
    Return an existing relay for a camera URL, or create a new one.
    A relay:
      - Opens the upstream MJPEG stream once
      - Distributes frames to all connected browser clients
    We use CachedMediaRelay for a small buffer that helps absorb short drops.
    """
    with _relay_lock:
        relay = _media_relay.get(stream_url)
        if relay is None:
            relay = CachedMediaRelay(
                upstream_url=stream_url,
                cache_duration=WIRELESS_CACHE_DURATION,
                serve_delay=WIRELESS_SERVE_DELAY,
            )
            relay.start()  # Starts its background thread pulling frames
            _media_relay[stream_url] = relay
            logging.info(f"Relay created: {stream_url}")
        return relay

# ---------------------------------------------------------------------------
# ROUTES: WEB PAGES
# ---------------------------------------------------------------------------
@app.route("/aquaponics", methods=["GET", "POST"])
def index():
    """
    Main page. Builds two proxy URLs (one per camera) and passes them
    to the template. A timestamp param helps defeat browser caching.
    """
    host = DEFAULT_STREAM_HOST
    port = DEFAULT_STREAM_PORT

    # Build fish camera proxy URL (still goes through this Flask app)
    fish_stream_url = url_for(
        "stream_proxy",
        host=host,
        port=port,
        path=DEFAULT_STREAM_PATH_0
    )

    # Build plant camera proxy URL
    plants_stream_url = url_for(
        "stream_proxy",
        host=host,
        port=port,
        path=DEFAULT_STREAM_PATH_1
    )

    return render_template(
        "index.html",
        fish_stream_url=fish_stream_url,
        plants_stream_url=plants_stream_url,
        host=host,
        port=port,
        timestamp=int(time.time())  # basic cache-buster
    )

@app.route("/aquaponics/about")
def about():
    """Static About page."""
    return render_template("about.html")

@app.route("/aquaponics/contact")
def contact():
    """Static Contact page."""
    return render_template("contact.html")

@app.route("/aquaponics/sensors")
def sensors():
    """Sensor dashboard page (template only here)."""
    return render_template("sensors.html")

@app.route("/aquaponics/photos")
def photos():
    """Photo gallery page."""
    return render_template("photos.html")

# ---------------------------------------------------------------------------
# STREAM PROXY ENDPOINT
# ---------------------------------------------------------------------------
@app.route("/aquaponics/stream_proxy")
def stream_proxy():
    """
    Proxies an upstream MJPEG stream through this server.
    Steps:
      1. Read query parameters (host, port, path).
      2. Construct full upstream URL (e.g. http://172.16.1.200:8000/stream0.mjpg).
      3. Get or create a relay for that URL.
      4. Attach this browser as a client (queue).
      5. Yield frame chunks to the browser in a multipart MJPEG response.
    The browser <img> tag renders the stream continuously.
    """
    # Get parameters or fall back to defaults
    host = request.args.get("host", DEFAULT_STREAM_HOST)
    port = int(request.args.get("port", DEFAULT_STREAM_PORT))
    path = request.args.get("path", DEFAULT_STREAM_PATH_0)

    # Build complete upstream URL
    stream_url = f"http://{host}:{port}{path}"

    # Acquire (or create) relay
    relay = get_media_relay(stream_url)

    # Each client gets its own queue of incoming data chunks (frames)
    client_queue = relay.add_client()

    def generate():
        """
        Generator that yields multipart MJPEG chunks to the browser.
        It blocks waiting for frame data and stops if the relay stops or times out.
        """
        # Warm-up: wait until the relay has at least one frame or timeout
        waited = 0.0
        while relay.last_frame is None and waited < WARMUP_TIMEOUT:
            time.sleep(0.1)
            waited += 0.1

        consecutive_timeouts = 0

        try:
            while True:
                try:
                    # Wait for next frame chunk from relay
                    chunk = client_queue.get(timeout=QUEUE_TIMEOUT)
                    consecutive_timeouts = 0  # Reset because we received data

                    # None signals relay failure or termination
                    if chunk is None:
                        break

                    # Send raw frame bytes (already formatted by relay)
                    yield chunk

                except queue.Empty:
                    # No frame arrived in QUEUE_TIMEOUT seconds
                    consecutive_timeouts += 1
                    # If relay died or too many misses, end stream
                    if not relay.running or consecutive_timeouts >= MAX_CONSECUTIVE_TIMEOUTS:
                        break
        finally:
            # Remove this client from relay to free resources
            relay.remove_client(client_queue)

    # Return streaming HTTP response
    return Response(
        generate(),
        mimetype=relay.content_type,  # Usually multipart/x-mixed-replace; boundary=frame
        headers={
            # Prevent caching so the browser keeps requesting live frames
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache",
            "Expires": "0",
        },
    )

@app.route("/aquaponics/health")
def health():
    """
    Simple health check used by monitoring or load balancers.
    Returns JSON if the app is alive.
    """
    return {"status": "ok"}

# ---------------------------------------------------------------------------
# TEMPLATE CONTEXT
# ---------------------------------------------------------------------------
@app.context_processor
def inject_urls():
    """
    Makes app_root available in all templates if needed for building links.
    """
    return dict(app_root=app.config["APPLICATION_ROOT"])

# ---------------------------------------------------------------------------
# CLEANUP LOGIC
# ---------------------------------------------------------------------------
def cleanup_relays():
    """
    Called at shutdown to stop all relay threads cleanly.
    Prevents orphan background threads after server exit.
    """
    with _relay_lock:
        for relay in _media_relay.values():
            relay.stop()
        _media_relay.clear()
    logging.info("Relays cleaned up")

# ---------------------------------------------------------------------------
# MAIN ENTRY POINT
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import atexit
    atexit.register(cleanup_relays)

    print("Aquaponics streaming server running.")
    print("Access at: http://localhost:5000/aquaponics")

    # debug=False for production-like behavior
