"""
MediaRelay module for video stream distribution.

This module provides the MediaRelay class for distributing video streams
from cameras to multiple web browsers efficiently.
"""

import threading
import time
import queue
import logging
import requests
from typing import Set

# ========== MEDIA RELAY CONSTANTS ==========
# These control how the legacy MediaRelay behaves

RETRY_DELAY_MIN = 1         # Start with 1 second retry delay
RETRY_DELAY_MAX = 30        # Maximum retry delay of 30 seconds
RETRY_DELAY_MULTIPLIER = 1.5  # Exponential backoff multiplier
CLIENT_QUEUE_SIZE = 20      # Buffer size for each client (video chunks)
CLIENT_TIMEOUT = 0.5        # Seconds to wait for slow clients
CHUNK_SIZE = 4096          # Size of data chunks to read from camera (4KB)
WARMUP_TIMEOUT = 15        # Seconds to wait for initial connection
CONNECT_TIMEOUT = 10       # Seconds to wait for HTTP connection
READ_TIMEOUT = 300         # Seconds to wait for data from camera


class MediaRelay:
    """
    Media Relay Class - The Smart Video Distributor
    
    Think of this like a cable TV splitter for video streams:
    - It connects to the camera ONCE
    - Multiple web browsers can watch the same stream
    - If the camera goes offline, it automatically tries to reconnect
    - It removes slow clients so they don't affect others
    
    This is much more efficient than having each browser connect directly
    to the camera, which would overwhelm it.
    
    Why we need this:
    - Cameras can usually only handle a few connections at once
    - If 10 people try to watch, the camera might crash
    - The MediaRelay acts as a "middleman" that shares the stream
    """

    def __init__(self, stream_url: str):
        """Initialize the media relay for a specific camera stream"""
        self.stream_url = stream_url           # URL of the camera stream
        self.clients: Set[queue.Queue] = set() # Set of connected web browsers (no duplicates)
        self.running = False                   # Is the relay currently active?
        self.thread = None                     # Background thread for stream handling
        self.lock = threading.Lock()           # Prevents race conditions between threads
        self.last_frame = None                 # Most recent video frame (for instant display)
        self.content_type = "multipart/x-mixed-replace"  # MJPEG MIME type

    def start(self):
        """Start the media relay in a background thread"""
        with self.lock:  # Thread-safe operation (only one thread can run this at a time)
            if not self.running:
                self.running = True
                # Create a daemon thread (dies when main program exits)
                # This prevents the program from hanging if we forget to stop the thread
                self.thread = threading.Thread(
                    target=self._stream_worker, daemon=True
                )
                self.thread.start()
                logging.info(f"Media relay started for {self.stream_url}")

    def stop(self):
        """Stop the media relay and clean up resources"""
        with self.lock:
            if self.running:
                self.running = False
                if self.thread:
                    self.thread.join(timeout=5)  # Wait up to 5 seconds for thread to finish
                logging.info(f"Media relay stopped for {self.stream_url}")

    def add_client(self) -> queue.Queue:
        """
        Add a new client (web browser) to receive the stream
        Returns a queue that will receive video data
        
        A queue is like a line at the grocery store - first in, first out
        Each browser gets their own queue so they can receive frames independently
        """
        client_queue = queue.Queue(maxsize=CLIENT_QUEUE_SIZE)  # Buffer for video chunks
        with self.lock:
            self.clients.add(client_queue)
            # If we have a recent frame, send it immediately for faster startup
            # This is like showing someone the "current scene" when they tune in
            if self.last_frame:
                try:
                    client_queue.put_nowait(self.last_frame)
                except queue.Full:
                    pass  # Queue is full, skip this frame
        
        logging.info(
            f"Client added. Total clients: {len(self.clients)} for {self.stream_url}"
        )
        return client_queue

    def remove_client(self, client_queue: queue.Queue):
        """Remove a client when they disconnect"""
        with self.lock:
            self.clients.discard(client_queue)  # Remove from set (safe if not present)
        logging.info(f"Client removed. Total clients: {len(self.clients)}")

    def _stream_worker(self):
        """
        Background worker thread that maintains the connection to the camera
        This runs continuously and handles reconnections if the camera goes offline
        
        Think of this as a dedicated employee whose only job is to maintain
        the connection to the camera and keep video flowing
        """
        retry_delay = RETRY_DELAY_MIN  # Start with minimum retry delay

        while self.running:
            try:
                logging.info(f"Connecting to camera stream: {self.stream_url}")
                
                # Make HTTP request to camera with streaming enabled
                # Increased timeout and added keep-alive for better connection stability
                # This is like making a phone call to the camera and asking for video
                response = requests.get(
                    self.stream_url, 
                    stream=True,  # Don't download everything at once - stream it piece by piece
                    timeout=(CONNECT_TIMEOUT, READ_TIMEOUT),  # (connect_timeout, read_timeout) in seconds
                    headers={
                        'Connection': 'keep-alive',  # Keep the connection open
                        'Cache-Control': 'no-cache'  # Always get fresh data
                    }
                )
                response.raise_for_status()  # Raise exception if HTTP error (404, 500, etc.)

                # Get the content type from the camera response
                # This tells us what kind of video format the camera is sending
                self.content_type = response.headers.get(
                    "Content-Type", "multipart/x-mixed-replace"
                )

                # Reset retry delay on successful connection
                retry_delay = RETRY_DELAY_MIN

                logging.info(f"Stream connected successfully: {self.stream_url}")

                # Read video data in chunks and distribute to clients
                last_data_time = time.time()
                
                # This loop continuously reads video data from the camera
                for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
                    if not self.running:  # Stop if relay is shutting down
                        break

                    # Debug: log chunk sizes occasionally so we can see activity
                    try:
                        if chunk:
                            self.last_frame = chunk  # Save for new clients
                            last_data_time = time.time()
                            # Log unusual chunk sizes for debugging
                            if len(chunk) < 100 or len(chunk) > 10000:
                                logging.debug(f"Received chunk size={len(chunk)} bytes from {self.stream_url}")
                            self._distribute_chunk(chunk)  # Send to all clients
                        else:
                            # Check for connection stall
                            # If we haven't received data for too long, something is wrong
                            if time.time() - last_data_time > READ_TIMEOUT:
                                logging.warning(f"No data received for {READ_TIMEOUT} seconds, reconnecting...")
                                break
                            # otherwise continue waiting for data
                    except Exception as e:
                        logging.exception(f"Error processing chunk from {self.stream_url}: {e}")
                        break

            except Exception as e:
                logging.error(f"Stream connection error for {self.stream_url}: {e}")

                # Notify all clients about the error
                # Send None to signal that something went wrong
                with self.lock:
                    for client_queue in list(self.clients):
                        try:
                            client_queue.put_nowait(None)  # None signals an error
                        except queue.Full:
                            pass

                # Wait before retrying with exponential backoff
                # (retry_delay increases each time, up to max_retry_delay)
                # This prevents hammering a broken camera with connection attempts
                if self.running:
                    logging.info(f"Retrying connection in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                    retry_delay = min(retry_delay * RETRY_DELAY_MULTIPLIER, RETRY_DELAY_MAX)

    def _distribute_chunk(self, chunk: bytes):
        """
        Send a chunk of video data to all connected clients
        Remove clients that are too slow to keep up, but try briefly first
        
        This is like a mail carrier delivering the same letter to multiple houses
        If someone's mailbox is full, we try once more, then skip that house
        """
        with self.lock:
            dead_clients = []  # List of clients to remove
            
            # Send to each connected browser
            for client_queue in list(self.clients):
                try:
                    # Try to send data without blocking first
                    client_queue.put_nowait(chunk)
                except queue.Full:
                    # Client's queue is full (they're slow). Try a short blocking put before giving up.
                    try:
                        client_queue.put(chunk, timeout=CLIENT_TIMEOUT)  # Wait briefly
                    except queue.Full:
                        # Still can't send - this client is too slow
                        dead_clients.append(client_queue)

            # Remove slow/unresponsive clients
            # This prevents one slow browser from affecting everyone else
            for dead_client in dead_clients:
                self.clients.discard(dead_client)
                logging.warning("Removed slow client from media relay")