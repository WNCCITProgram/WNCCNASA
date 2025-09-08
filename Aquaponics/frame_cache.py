"""
Frame caching system for unreliable wireless camera streams.
Buffers frames from upstream and serves them with a configurable delay.

This system acts as a "buffer" between an unreliable wireless camera and web browsers.
It downloads frames from the camera, stores them temporarily, and serves them to browsers
with a slight delay. This smooths out connection problems and provides stable video.
"""
import threading
import time
import logging
from collections import deque
from typing import Optional
import requests
from dataclasses import dataclass

# ========== FRAME CACHE CONSTANTS ==========
# These constants control how the frame caching system behaves

DEFAULT_SERVE_DELAY = 2.0       # seconds - delay before serving frames for stability (prevents stuttering)
DEFAULT_CACHE_DURATION = 15.0    # seconds - how long to keep frames in cache (like a DVR buffer)
DEFAULT_FRAME_RATE = 15         # fps - target frame rate for output ( frames per second)
MAX_BUFFER_SIZE = 4 * 1024 * 1024  # bytes - max buffer size to prevent memory bloat (4 MB)
BUFFER_TRIM_SIZE = 1024 * 1024     # bytes - size to trim buffer to when it gets too large (1 MB)
FETCH_CHUNK_SIZE = 4096            # bytes - chunk size for reading upstream (4 KB at a time)
CONNECTION_TIMEOUT = 10            # seconds - timeout for upstream connections
RETRY_DELAY_MIN = 1.0             # seconds - minimum retry delay when connection fails
RETRY_DELAY_MAX = 30.0            # seconds - maximum retry delay when connection fails
RETRY_DELAY_MULTIPLIER = 1.5      # multiplier for exponential backoff (delays get longer each retry)

@dataclass
class CachedFrame:
    """
    A single video frame stored in our cache.
    Think of this like a photo with a timestamp and sequence number.
    """
    data: bytes        # The actual JPEG image data
    timestamp: float   # When this frame was captured (Unix timestamp)
    sequence: int      # Frame number (1st frame, 2nd frame, etc.)

class FrameCache:
    """
    Caches frames from an upstream MJPEG stream and serves them with a delay.
    This smooths out wireless connection issues by maintaining a buffer.
    
    Think of this like a DVR that records a live TV show and lets you watch
    it a few seconds behind real-time to avoid buffering issues.
    """
    
    def __init__(self, upstream_url: str, cache_duration: float = DEFAULT_CACHE_DURATION, serve_delay: float = DEFAULT_SERVE_DELAY):
        """
        Initialize the frame cache system.
        
        Args:
            upstream_url: The camera's video stream URL (like "http://192.168.1.100:8000/stream.mjpg")
            cache_duration: How many seconds of video to keep in memory
            serve_delay: How many seconds to delay before serving frames (for stability)
        """
        # Store the configuration
        self.upstream_url = upstream_url
        self.cache_duration = cache_duration
        self.serve_delay = serve_delay
        
        # Create a deque (double-ended queue) to store frames - like a circular buffer
        self.frames: deque[CachedFrame] = deque()
        
        # Create a lock to prevent multiple threads from modifying the frame list at once
        self.lock = threading.RLock()  # RLock = Reentrant Lock (can be locked multiple times by same thread)
        
        # Control flags
        self.running = False           # Is the cache system currently active?
        self.sequence_counter = 0      # Counter to number each frame (1, 2, 3, ...)
        
        # Worker thread for fetching frames from the camera
        self.fetch_thread: Optional[threading.Thread] = None
        
        # Statistics - keep track of what's happening
        self.frames_received = 0       # How many frames we've downloaded from the camera
        self.frames_served = 0         # How many frames we've sent to browsers
        self.upstream_errors = 0       # How many times the camera connection failed
        
    def start(self):
        """Start the frame caching system"""
        # Don't start if we're already running
        if self.running:
            return
            
        # Set the running flag to True
        self.running = True
        
        # Create and start a background thread to fetch frames from the camera
        # daemon=True means this thread will automatically stop when the main program stops
        self.fetch_thread = threading.Thread(target=self._fetch_worker, daemon=True)
        self.fetch_thread.start()
        
        # Log that we started successfully
        logging.info(f"Frame cache started for {self.upstream_url} (delay={self.serve_delay}s)")
        
    def stop(self):
        """Stop the frame caching system"""
        # Set running flag to False (this tells the worker thread to stop)
        self.running = False
        
        # Wait for the worker thread to finish (with a 5 second timeout)
        if self.fetch_thread:
            self.fetch_thread.join(timeout=5)
            
        logging.info("Frame cache stopped")
        
    def _fetch_worker(self):
        """
        Worker thread that continuously fetches frames from upstream camera.
        This runs in the background and never stops until the cache is stopped.
        """
        # Start with a short retry delay
        retry_delay = RETRY_DELAY_MIN
        
        # Keep trying to connect to the camera until we're told to stop
        while self.running:
            try:
                logging.info(f"Connecting to upstream camera: {self.upstream_url}")
                
                # Make an HTTP request to the camera's video stream
                # stream=True means we'll read the data piece by piece, not all at once
                response = requests.get(
                    self.upstream_url,
                    stream=True,                    # Read data as it comes in
                    timeout=CONNECTION_TIMEOUT,     # Give up after 10 seconds if no response
                    headers={'User-Agent': 'FrameCache/1.0'}  # Identify ourselves to the camera
                )
                
                # Check if the request was successful (status code 200, 201, etc.)
                response.raise_for_status()
                
                logging.info("Connected to upstream camera successfully")
                retry_delay = RETRY_DELAY_MIN  # Reset retry delay on success
                
                # Parse the MJPEG stream and extract individual frames
                self._parse_mjpeg_stream(response)
                
            except Exception as e:
                # Something went wrong - log the error
                self.upstream_errors += 1
                logging.error(f"Upstream connection error: {e}")
                
                # If we're still supposed to be running, wait and try again
                if self.running:
                    logging.info(f"Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                    
                    # Increase the retry delay for next time (exponential backoff)
                    # This prevents hammering a broken camera with connection attempts
                    retry_delay = min(retry_delay * RETRY_DELAY_MULTIPLIER, RETRY_DELAY_MAX)
                    
    def _parse_mjpeg_stream(self, response):
        """
        Parse MJPEG stream and extract individual JPEG frames.
        
        MJPEG is like a series of JPEG photos sent one after another.
        Each JPEG starts with 0xFF 0xD8 and ends with 0xFF 0xD9.
        We need to find these markers to extract complete frames.
        """
        # Create a buffer to accumulate incoming data
        buffer = bytearray()
        
        try:
            # Read data from the camera in chunks
            for chunk in response.iter_content(chunk_size=FETCH_CHUNK_SIZE):
                # Stop if we're told to shut down
                if not self.running:
                    break
                    
                # Skip empty chunks
                if not chunk:
                    continue
                    
                # Add this chunk to our buffer
                buffer.extend(chunk)
                
                # Look for complete JPEG frames in the buffer
                while True:
                    # Find JPEG start marker (0xFF 0xD8)
                    start = buffer.find(b'\xff\xd8')
                    if start == -1:
                        # No start marker found, need more data
                        break
                        
                    # Find JPEG end marker (0xFF 0xD9) after the start
                    end = buffer.find(b'\xff\xd9', start + 2)
                    if end == -1:
                        # Incomplete frame, keep buffer and wait for more data
                        # But don't let the buffer grow too large (prevents memory problems)
                        if len(buffer) > MAX_BUFFER_SIZE:
                            buffer = buffer[-BUFFER_TRIM_SIZE:]  # Keep only the last 1MB
                        break
                        
                    # We found a complete frame! Extract it
                    frame_data = bytes(buffer[start:end + 2])  # Include the end marker
                    
                    # Remove this frame from the buffer
                    del buffer[:end + 2]
                    
                    # Store this frame in our cache
                    self._cache_frame(frame_data)
                    
        except Exception as e:
            logging.error(f"Error parsing MJPEG stream: {e}")
            raise  # Re-raise the exception so the caller knows something went wrong
            
    def _cache_frame(self, frame_data: bytes):
        """
        Add a frame to the cache.
        This is called every time we get a new frame from the camera.
        """
        # Get the current time
        timestamp = time.time()
        
        # Use the lock to prevent other threads from modifying the frame list
        with self.lock:
            # Create a cached frame object with all the info
            cached_frame = CachedFrame(
                data=frame_data,                    # The JPEG image data
                timestamp=timestamp,                # When we received it
                sequence=self.sequence_counter      # Frame number
            )
            
            # Increment counters
            self.sequence_counter += 1
            self.frames_received += 1
            
            # Add the frame to the end of our cache
            self.frames.append(cached_frame)
            
            # Remove old frames that are older than our cache duration
            # This is like deleting old recordings to make room for new ones
            cutoff_time = timestamp - self.cache_duration
            while self.frames and self.frames[0].timestamp < cutoff_time:
                self.frames.popleft()  # Remove from the front of the deque
                
            # Log statistics occasionally (every 100 frames) for debugging
            if self.frames_received % 100 == 0:
                logging.debug(f"Cache stats: {len(self.frames)} frames, {self.frames_received} received, {self.frames_served} served")
                
    def get_frame_to_serve(self) -> Optional[bytes]:
        """
        Get a frame that's ready to be served (accounting for delay).
        This is called when a web browser wants the next frame.
        
        Returns:
            The JPEG frame data if available, or None if no frame is ready
        """
        current_time = time.time()
        
        # Calculate what time frames need to be from to be "old enough" to serve
        # This implements the delay - we only serve frames that are at least X seconds old
        serve_time = current_time - self.serve_delay
        
        # Use the lock to safely access the frame list
        with self.lock:
            # Look through frames from newest to oldest to find the most recent
            # frame that's old enough to serve
            frame_to_serve = None
            for frame in reversed(self.frames):  # Start from the newest frame
                if frame.timestamp <= serve_time:   # Is this frame old enough?
                    frame_to_serve = frame
                    break  # Found it! Stop looking
                    
            # If we found a suitable frame, return it
            if frame_to_serve:
                self.frames_served += 1  # Update statistics
                return frame_to_serve.data
                
        # No frame is ready to serve yet
        return None
        
    def get_cache_status(self) -> dict:
        """
        Get cache status information for monitoring and debugging.
        This returns a dictionary with statistics about the cache.
        """
        with self.lock:
            return {
                'running': self.running,                    # Is the cache active?
                'frames_in_cache': len(self.frames),        # How many frames are stored?
                'frames_received': self.frames_received,    # Total frames downloaded
                'frames_served': self.frames_served,        # Total frames sent to browsers
                'upstream_errors': self.upstream_errors,    # How many connection failures?
                'cache_duration': self.cache_duration,      # Cache settings
                'serve_delay': self.serve_delay,
                # Calculate how old the oldest and newest frames are
                'oldest_frame_age': time.time() - self.frames[0].timestamp if self.frames else 0,
                'newest_frame_age': time.time() - self.frames[-1].timestamp if self.frames else 0
            }