"""
Enhanced MediaRelay that uses FrameCache for stable streaming from unreliable sources.

This is like a "smart TV relay" that sits between unreliable wireless cameras and web browsers.
It uses the FrameCache system to provide smooth, stable video even when the camera connection
is flaky or slow.
"""
import threading
import time
import queue
import logging
from typing import Set, Optional
from frame_cache import FrameCache, DEFAULT_CACHE_DURATION, DEFAULT_SERVE_DELAY, DEFAULT_FRAME_RATE

# ========== CACHED RELAY CONSTANTS ==========
# These settings control how the relay distributes video to web browsers

CLIENT_QUEUE_SIZE = 50             # max frames each browser can have waiting (larger = more buffering)
STREAM_WORKER_SLEEP = 0.1          # seconds - how often to check for new frames when none available
FRAME_INTERVAL = 1.0 / DEFAULT_FRAME_RATE  # seconds between frames (1/15 = 0.067s for 15 FPS)
CLIENT_REMOVAL_TIMEOUT = 5         # seconds - how long to wait for threads to stop when shutting down

class CachedMediaRelay:
    """
    Media relay that uses frame caching to provide stable streams from unreliable sources.
    Replaces the original MediaRelay for wireless camera connections.
    
    Think of this as a "video distribution center":
    1. It gets frames from the FrameCache (which buffers from the camera)
    2. It converts them to the right format for web browsers
    3. It sends them to all connected browsers at a steady rate
    """
    
    def __init__(self, upstream_url: str, cache_duration: float = DEFAULT_CACHE_DURATION, serve_delay: float = DEFAULT_SERVE_DELAY):
        """
        Initialize the cached media relay.
        
        Args:
            upstream_url: The camera's video stream URL
            cache_duration: How long to cache frames (seconds)
            serve_delay: How long to delay frames for stability (seconds)
        """
        # Store configuration
        self.upstream_url = upstream_url
        
        # Set to store client queues - each connected browser gets a queue
        # A "set" is like a list but doesn't allow duplicates
        self.clients: Set[queue.Queue] = set()
        
        # Lock to protect the client list from multiple threads
        # This prevents crashes when multiple browsers connect/disconnect at once
        self.lock = threading.RLock()
        
        # Control flag
        self.running = False
        
        # Create the frame cache that will buffer frames from the camera
        # This is the component that actually downloads and stores video frames
        self.frame_cache = FrameCache(upstream_url, cache_duration, serve_delay)
        
        # Background thread that distributes frames to browsers
        self.stream_thread: Optional[threading.Thread] = None
        
        # Store the most recent frame for immediate delivery to new browsers
        # When someone opens the webpage, we can show them the current scene right away
        self.last_frame: Optional[bytes] = None
        
        # MIME type for MJPEG streams (tells browsers this is a video stream)
        # This is like a "file type" that browsers understand
        self.content_type = "multipart/x-mixed-replace; boundary=frame"
        
    def start(self):
        """Start the cached relay system"""
        # Don't start if already running (prevents duplicate processes)
        if self.running:
            return
            
        # Set running flag (this tells all our threads to stay active)
        self.running = True
        
        # Start the frame cache (this begins downloading from the camera)
        self.frame_cache.start()
        
        # Start our own thread to distribute frames to browsers
        # daemon=True means this thread stops automatically when the main program stops
        self.stream_thread = threading.Thread(target=self._stream_worker, daemon=True)
        self.stream_thread.start()
        
        logging.info(f"Cached media relay started for {self.upstream_url}")
        
    def stop(self):
        """Stop the cached relay system"""
        # Set the stop flag (tells all threads to finish up and stop)
        self.running = False
        
        # Stop the frame cache (stops downloading from camera)
        self.frame_cache.stop()
        
        # Wait for our distribution thread to finish
        # timeout=5 means "wait up to 5 seconds, then give up"
        if self.stream_thread:
            self.stream_thread.join(timeout=CLIENT_REMOVAL_TIMEOUT)
            
        logging.info("Cached media relay stopped")
        
    def add_client(self) -> queue.Queue:
        """
        Add a client (web browser) and return their queue.
        Each browser gets its own queue to receive video frames.
        
        Think of this like adding someone to a mailing list - they'll get copies
        of every video frame we send out.
        """
        # Create a queue for this browser - it can hold up to CLIENT_QUEUE_SIZE frames
        # A queue is like a line at the grocery store - first in, first out
        client_queue = queue.Queue(maxsize=CLIENT_QUEUE_SIZE)
        
        # Use the lock to safely modify the client list
        # This prevents problems if multiple browsers connect at the exact same time
        with self.lock:
            # Add this browser to our list of clients
            self.clients.add(client_queue)
            
            # If we have a recent frame, send it immediately for faster startup
            # This is like showing the browser the "current scene" right away
            # instead of making them wait for the next frame
            if self.last_frame:
                try:
                    # put_nowait() = add to queue without waiting (fail if queue is full)
                    client_queue.put_nowait(self.last_frame)
                except queue.Full:
                    # If queue is somehow full, just skip this (shouldn't happen with new browser)
                    pass
                    
        # Log the new connection for debugging
        logging.info(f"Client added. Total clients: {len(self.clients)} for {self.upstream_url}")
        return client_queue
        
    def remove_client(self, client_queue: queue.Queue):
        """Remove a client (browser disconnected)"""
        with self.lock:
            # Remove this browser from our client list
            # discard() is like remove() but won't error if the item isn't found
            self.clients.discard(client_queue)
            
        logging.info(f"Client removed. Total clients: {len(self.clients)}")
        
    def _stream_worker(self):
        """
        Worker thread that serves cached frames to clients.
        This runs continuously and sends frames to all connected browsers.
        
        Think of this like a TV station that broadcasts the same signal
        to all TVs that are tuned in.
        """
        last_frame_time = 0  # Track when we last sent a frame
        
        # Keep running until told to stop
        while self.running:
            try:
                current_time = time.time()
                
                # Control frame rate - don't send frames too fast
                # This prevents overwhelming browsers and saves bandwidth
                if current_time - last_frame_time < FRAME_INTERVAL:
                    time.sleep(STREAM_WORKER_SLEEP)  # Wait a bit and try again
                    continue
                    
                # Get the next frame from our cache
                frame_data = self.frame_cache.get_frame_to_serve()
                if not frame_data:
                    # No frame ready yet (cache might be empty or delay not met)
                    time.sleep(STREAM_WORKER_SLEEP)
                    continue
                    
                # Wrap the frame in the proper format for web browsers
                # MJPEG streams need special headers between each frame
                # This is like putting each photo in an envelope with an address
                multipart_frame = (
                    b"--frame\r\n"  # Boundary marker (separates frames)
                    b"Content-Type: image/jpeg\r\n"  # Tell browser this is a JPEG
                    b"Content-Length: " + str(len(frame_data)).encode("ascii") + b"\r\n\r\n"  # Size info
                    + frame_data + b"\r\n"  # The actual JPEG data plus ending
                )
                
                # Store this as the "last frame" for new browsers
                self.last_frame = multipart_frame
                last_frame_time = current_time
                
                # Send this frame to all connected browsers
                self._distribute_frame(multipart_frame)
                
            except Exception as e:
                # Log any errors but keep trying (don't crash the whole system)
                logging.error(f"Error in cached stream worker: {e}")
                time.sleep(1)  # Wait a second before trying again
                
    def _distribute_frame(self, frame_data: bytes):
        """
        Distribute a frame to all connected clients (browsers).
        
        This is like a post office delivering the same letter to multiple addresses.
        
        Args:
            frame_data: The formatted frame data ready to send to browsers
        """
        with self.lock:
            # List to track browsers that are too slow to keep up
            dead_clients = []
            
            # Send the frame to each connected browser
            # list() creates a copy so we can safely modify the original during iteration
            for client_queue in list(self.clients):
                try:
                    # Try to send the frame without blocking
                    # put_nowait() = add to queue immediately or fail if queue is full
                    client_queue.put_nowait(frame_data)
                except queue.Full:
                    # Browser's queue is full - it's not reading frames fast enough
                    # This happens when someone's internet is slow or browser is lagging
                    
                    # Try to make room by dropping the oldest frame
                    try:
                        client_queue.get_nowait()  # Remove oldest frame
                        client_queue.put_nowait(frame_data)  # Add new frame
                    except queue.Full:
                        # Still full after dropping a frame - this browser is too slow
                        # Mark it for removal so it doesn't slow down other browsers
                        dead_clients.append(client_queue)
                        
            # Remove browsers that can't keep up
            # This prevents one slow browser from affecting everyone else
            for dead_client in dead_clients:
                self.clients.discard(dead_client)
                logging.warning("Removed slow client from cached relay")
                
    def get_status(self) -> dict:
        """
        Get relay status including cache information.
        This provides detailed information for monitoring and debugging.
        
        Returns a dictionary with statistics like:
        - How many browsers are connected
        - Whether the system is running properly
        - Cache statistics (frames stored, errors, etc.)
        """
        # Get status from our frame cache
        cache_status = self.frame_cache.get_cache_status()
        
        # Add our own status information
        with self.lock:
            return {
                'relay_running': self.running,                           # Is the relay active?
                'client_count': len(self.clients),                      # How many browsers connected?
                'last_frame_available': self.last_frame is not None,    # Do we have a recent frame?
                'cache': cache_status                                   # All the cache statistics
            }