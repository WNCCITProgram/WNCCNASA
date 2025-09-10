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
from typing import Dict

# Local modules that handle pulling frames from upstream cameras
from broadcast_relay import BroadcastCamera

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
_broadcast_cameras: Dict[str, BroadcastCamera] = {}
_broadcast_lock = threading.Lock()

def get_broadcast_camera(stream_url: str) -> BroadcastCamera:
    with _broadcast_lock:
        cam = _broadcast_cameras.get(stream_url)
        if cam is None:
            cam = BroadcastCamera(stream_url)
            cam.start()
            _broadcast_cameras[stream_url] = cam
            logging.info(f"[BroadcastFactory] Created {stream_url}")
        return cam

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

# Champions page route
@app.route("/aquaponics/champions")
def champions():
    """Page recognizing Aquaponics Champions."""
    return render_template("champions.html")

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

@app.route("/aquaponics/stats")
def stats_page():
    """HTML page that displays waitress/server streaming statistics."""
    return render_template("waitress_stats.html")

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

    cam = get_broadcast_camera(stream_url)
    cam.add_client()

    def generate():
        WARMUP_TIMEOUT = 10
        QUEUE_TIMEOUT = 8
        MAX_TIMEOUTS = 5
        waited = 0.0
        # Wait for first frame
        while cam.last_jpeg is None and waited < WARMUP_TIMEOUT and cam.running:
            with cam._cond:
                cam._cond.wait(timeout=0.2)
            waited += 0.2
        if cam.last_jpeg is None:
            return
        last_sent = -1
        timeouts = 0
        while cam.running:
            with cam._cond:
                signaled = cam._cond.wait_for(
                    lambda: not cam.running or cam.frame_id != last_sent,
                    timeout=QUEUE_TIMEOUT
                )
                if not signaled:
                    timeouts += 1
                    if timeouts >= MAX_TIMEOUTS or not cam.running:
                        break
                    continue
                timeouts = 0
                if not cam.running or cam.last_jpeg is None:
                    continue
                jpeg = cam.last_jpeg
                last_sent = cam.frame_id
            yield (
                b"--frame\r\n"
                b"Content-Type: image/jpeg\r\n"
                b"Content-Length: " + str(len(jpeg)).encode() + b"\r\n\r\n" +
                jpeg + b"\r\n"
            )
            # Optional tiny heartbeat every N frames (no-op comment line)
            # if last_sent % 120 == 0: yield b"#\r\n"
    resp = Response(generate(), mimetype="multipart/x-mixed-replace; boundary=frame",
                    headers={
                        "Cache-Control": "no-cache, no-store, must-revalidate",
                        "Pragma": "no-cache",
                        "Expires": "0",
                    })
    def _close(response):
        cam.remove_client()
        return response
    return resp

@app.route("/aquaponics/health")
def health():
    """
    Simple health check used by monitoring or load balancers.
    Returns JSON if the app is alive.
    """
    return {"status": "ok"}

@app.route("/aquaponics/server_info")
def server_info():
    import threading
    return {
        "server": request.environ.get("SERVER_SOFTWARE", "unknown"),
        "active_threads": len(threading.enumerate()),
        "broadcast_cameras": list(getattr(globals(), "_broadcast_cameras", {}).keys())
    }

@app.route("/aquaponics/waitress_info")
def waitress_info():
    """
    Runtime diagnostics focused on Waitress + streaming load.
    Gives a quick view of thread usage and camera client counts.
    """
    import threading, platform, sys, time
    all_threads = threading.enumerate()
    thread_names = [t.name for t in all_threads]
    waitress_threads = [n for n in thread_names if "waitress" in n.lower()]
    camera_stats = {}
    with _broadcast_lock:
        for url, cam in _broadcast_cameras.items():
            with cam._cond:
                camera_stats[url] = {
                    "clients": cam._clients,
                    "frame_id": cam.frame_id,
                    "has_frame": cam.last_jpeg is not None,
                    "running": cam.running,
                }

    return {
        "server_software": request.environ.get("SERVER_SOFTWARE", "unknown"),
        "python": sys.version.split()[0],
        "platform": platform.platform(),
        "utc_epoch": int(time.time()),
        "threads_total": len(all_threads),
        "threads_waitress": len(waitress_threads),
        "waitress_thread_names_sample": waitress_threads[:10],
        "threads_other": len(all_threads) - len(waitress_threads),
        "cameras": camera_stats
    }

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
    with _broadcast_lock:
        for c in _broadcast_cameras.values():
            c.stop()
        _broadcast_cameras.clear()
    logging.info("Broadcast relays cleaned up")

# ---------------------------------------------------------------------------
# MAIN ENTRY POINT
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import atexit
    atexit.register(cleanup_relays)
    print("Development mode ONLY (use waitress_app.py in production).")
    # DO NOT use debug=True in production behind IIS
    app.run(host="127.0.0.1", port=5000, debug=False)
