/*
 * =============================================================================
 * STREAM MANAGER - Handles live video streaming from the aquaponics camera
 * =============================================================================
 * This code manages the live video feed on the webpage. It handles:
 * - Loading the video stream
 * - Retrying when the connection fails
 * - Pausing when the page isn't visible (saves bandwidth)
 * - Monitoring stream health
 */

class StreamManager {
    constructor() {
        // =====================================================================
        // FIND HTML ELEMENTS - Get references to elements on the page
        // =====================================================================
        this.streamImg = document.getElementById('stream');           // The <img> tag that shows the video
        this.streamLoading = document.getElementById('stream-loading'); // Loading message element
        this.streamError = document.getElementById('stream-error');   // Error message element
        this.retryButton = document.getElementById('retry-stream');   // Button to retry connection
        
        // =====================================================================
        // CONNECTION SETTINGS - How we handle retries and timeouts
        // =====================================================================
        this.maxRetries = 5;        // Maximum number of times to retry connection
        this.retryCount = 0;        // Current retry attempt number
        this.retryDelay = 2000;     // Wait time between retries (starts at 2 seconds)
        
        // =====================================================================
        // TIMERS AND INTERVALS - For managing background tasks
        // =====================================================================
        this.loadTimeout = null;              // Timer for detecting load failures
        this.loadingSpinnerTimeout = null;    // Timer for showing loading spinner
        this.healthCheckInterval = null;      // Timer for checking stream health
        this.visibilityCheckInterval = null;  // Timer for checking page visibility
        this.lastFrameTime = Date.now();      // When we last received a video frame
        
        // =====================================================================
        // STATUS TRACKING - Keep track of what's happening
        // =====================================================================
        this.isPageVisible = true;    // Is the browser tab currently visible?
        this.isWindowFocused = true;  // Is the browser window focused?
        this.streamActive = false;    // Is the video stream currently working?
        
        // Start everything up
        this.init();
    }
    
    /*
     * =============================================================================
     * INITIALIZATION - Set up event listeners and start the stream
     * =============================================================================
     */
    init() {
        // Make sure we have the required HTML elements and stream URL
        if (!this.streamImg || !window.streamUrl) {
            console.error('Stream elements or URL not found');
            return;
        }
        
        // =====================================================================
        // SET UP EVENT LISTENERS - What happens when things occur
        // =====================================================================
        this.streamImg.onload = () => this.onStreamLoad();    // Video loaded successfully
        this.streamImg.onerror = () => this.onStreamError();  // Video failed to load
        this.retryButton.onclick = () => this.retryConnection(); // User clicked retry
        
        // Set up page visibility detection (pause when tab not visible)
        this.setupVisibilityHandlers();
        
        // =====================================================================
        // START THE STREAM - Warm up the connection then begin streaming
        // =====================================================================
        this.warmupRelay().then(() => {
            // Relay is ready, start streaming after short delay
            setTimeout(() => {
                this.startStream();
            }, 500);
        }).catch(() => {
            // Warmup failed, try streaming anyway after longer delay
            setTimeout(() => {
                this.startStream();
            }, 1000);
        });
        
        // Start background monitoring tasks
        this.startHealthCheck();        // Check if stream is working
        this.startVisibilityMonitoring(); // Monitor page visibility
    }
    
    /*
     * =============================================================================
     * PAGE VISIBILITY HANDLING - Pause/resume stream based on page visibility
     * =============================================================================
     * This saves bandwidth by not streaming when user can't see the page
     */
    setupVisibilityHandlers() {
        // =====================================================================
        // PAGE VISIBILITY API - Detect when browser tab is hidden/visible
        // =====================================================================
        document.addEventListener('visibilitychange', () => {
            this.isPageVisible = !document.hidden;
            console.log('Page visibility changed:', this.isPageVisible ? 'visible' : 'hidden');
            this.handleVisibilityChange();
        });
        
        // =====================================================================
        // WINDOW FOCUS EVENTS - Detect when browser window gets/loses focus
        // =====================================================================
        window.addEventListener('focus', () => {
            this.isWindowFocused = true;
            console.log('Window focused');
            this.handleVisibilityChange();
        });
        
        window.addEventListener('blur', () => {
            this.isWindowFocused = false;
            console.log('Window blurred');
            this.handleVisibilityChange();
        });
        
        // =====================================================================
        // PAGE LIFECYCLE EVENTS - Handle page closing/reloading
        // =====================================================================
        window.addEventListener('beforeunload', () => {
            console.log('Page unloading, stopping stream');
            this.stopStream();
        });
        
        // Handle browser back button or page reload
        window.addEventListener('pageshow', (event) => {
            if (event.persisted) {
                console.log('Page restored from cache, restarting stream');
                this.retryConnection();
            }
        });
        
        // =====================================================================
        // INTERSECTION OBSERVER - Detect if video element is visible on screen
        // =====================================================================
        if ('IntersectionObserver' in window) {
            const observer = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.target === this.streamImg.parentElement) {
                        const isInView = entry.isIntersecting;
                        console.log('Stream element in viewport:', isInView);
                        if (isInView && this.shouldStreamBeActive() && !this.streamActive) {
                            this.retryConnection();
                        }
                    }
                });
            }, { threshold: 0.1 }); // Trigger when 10% of element is visible
            
            observer.observe(this.streamImg.parentElement);
        }
    }
    
    /*
     * =============================================================================
     * VISIBILITY CHANGE HANDLER - Decide what to do when visibility changes
     * =============================================================================
     */
    handleVisibilityChange() {
        if (this.shouldStreamBeActive()) {
            // Page is visible, make sure stream is running
            if (!this.streamActive || this.streamImg.style.display === 'none') {
                console.log('Page is visible, ensuring stream is active');
                this.retryConnection();
            }
        } else {
            console.log('Page is not visible, stream can pause');
            // Could pause stream here to save bandwidth
            // this.pauseStream();
        }
    }
    
    /*
     * =============================================================================
     * UTILITY METHODS - Helper functions
     * =============================================================================
     */
    
    // Should the stream be running right now?
    shouldStreamBeActive() {
        return this.isPageVisible && this.isWindowFocused;
    }
    
    /*
     * =============================================================================
     * BACKGROUND MONITORING - Check stream health periodically
     * =============================================================================
     */
    startVisibilityMonitoring() {
        this.visibilityCheckInterval = setInterval(() => {
            if (this.shouldStreamBeActive() && this.streamActive) {
                // Check if image appears broken (loaded but no actual image data)
                if (this.streamImg.complete && this.streamImg.naturalHeight === 0) {
                    console.log('Stream appears broken, restarting');
                    this.retryConnection();
                }
            }
        }, 10000); // Check every 10 seconds
    }
    
    /*
     * =============================================================================
     * RELAY WARMUP - Prepare the video relay before starting stream
     * =============================================================================
     * This tells the server to start connecting to the camera before we request video
     */
    async warmupRelay() {
        try {
            // Extract parameters from the stream URL
            const url = new URL(window.streamUrl, window.location.origin);
            const params = new URLSearchParams(url.search);
            
            // Send warmup request to server
            const warmupUrl = '/aquaponics/warmup_relay?' + params.toString();
            const response = await fetch(warmupUrl);
            const data = await response.json();
            
            console.log('Relay warmup:', data);
            return data;
        } catch (error) {
            console.log('Relay warmup failed:', error);
            throw error;
        }
    }
    
    /*
     * =============================================================================
     * STREAM CONTROL METHODS - Start, stop, and manage the video stream
     * =============================================================================
     */
    
    // Start the video stream
    startStream() {
        // Don't start if page isn't visible
        if (!this.shouldStreamBeActive()) {
            console.log('Page not visible, delaying stream start');
            return;
        }
        
        // =====================================================================
        // LOADING SPINNER MANAGEMENT - Show spinner only if loading takes too long
        // =====================================================================
        if (this.loadingSpinnerTimeout) {
            clearTimeout(this.loadingSpinnerTimeout);
        }
        this.loadingSpinnerTimeout = setTimeout(() => {
            // Show loading spinner if no frame for more than 5 seconds
            if (!this.streamActive && (Date.now() - this.lastFrameTime) > 5000) {
                this.showLoading();
            }
        }, 5000);

        this.retryCount++;

        // =====================================================================
        // TIMEOUT MANAGEMENT - Set maximum time to wait for stream to load
        // =====================================================================
        if (this.loadTimeout) {
            clearTimeout(this.loadTimeout);
        }
        
        // Give the stream 20 seconds to load before declaring it failed
        this.loadTimeout = setTimeout(() => {
            this.onStreamError();
        }, 20000);

        // =====================================================================
        // START THE ACTUAL STREAM - Set the image source to the video URL
        // =====================================================================
        // Add timestamp to prevent caching issues
        const url = window.streamUrl + (window.streamUrl.includes('?') ? '&' : '?') + 't=' + new Date().getTime();
        this.streamImg.src = url;
        console.log('Starting stream:', url);
    }
    
    // Stop the video stream
    stopStream() {
        if (this.loadTimeout) {
            clearTimeout(this.loadTimeout);
        }
        this.streamImg.src = '';        // Clear the image source
        this.streamActive = false;      // Mark stream as inactive
        console.log('Stream stopped');
    }
    
    /*
     * =============================================================================
     * EVENT HANDLERS - What happens when stream loads or fails
     * =============================================================================
     */
    
    // Called when video loads successfully
    onStreamLoad() {
        console.log('Stream loaded successfully');
        
        // Clear the loading timeout since we loaded successfully
        if (this.loadTimeout) {
            clearTimeout(this.loadTimeout);
        }
        
        // Reset retry counters since we succeeded
        this.retryCount = 0;
        this.retryDelay = 2000;
        this.streamActive = true;
        this.lastFrameTime = Date.now();
        
        // Clear loading spinner timeout
        if (this.loadingSpinnerTimeout) {
            clearTimeout(this.loadingSpinnerTimeout);
        }
        
        // Show the video stream
        this.showStream();
    }
    
    // Called when video fails to load
    onStreamError() {
        console.log('Stream error occurred, retry count:', this.retryCount);
        
        // Clear loading timeout
        if (this.loadTimeout) {
            clearTimeout(this.loadTimeout);
        }
        
        this.streamActive = false;
        
        // =====================================================================
        // RETRY LOGIC - Try again if we haven't exceeded max retries
        // =====================================================================
        if (this.shouldStreamBeActive() && this.retryCount < this.maxRetries) {
            // Wait longer each time (exponential backoff)
            setTimeout(() => {
                this.retryDelay = Math.min(this.retryDelay * 1.5, 30000); // Max 30 seconds
                this.startStream();
            }, this.retryDelay);
        } else if (!this.shouldStreamBeActive()) {
            console.log('Page not visible, not retrying stream');
        } else {
            // Max retries exceeded, show error message
            this.showError();
        }
    }
    
    // Manual retry triggered by user clicking retry button
    retryConnection() {
        this.retryCount = 0;        // Reset retry counter
        this.retryDelay = 2000;     // Reset delay to 2 seconds
        this.streamActive = false;  // Mark as inactive
        this.startStream();         // Try again
    }
    
    /*
     * =============================================================================
     * UI STATE MANAGEMENT - Show/hide different elements based on stream status
     * =============================================================================
     */
    
    // Show loading spinner and message
    showLoading() {
        this.streamImg.style.display = 'none';      // Hide video
        this.streamError.style.display = 'none';    // Hide error message
        this.streamLoading.style.display = 'block'; // Show loading message
    }
    
    // Show the video stream
    showStream() {
        this.streamLoading.style.display = 'none';  // Hide loading message
        this.streamError.style.display = 'none';    // Hide error message
        this.streamImg.style.display = 'block';     // Show video
    }
    
    // Show error message and retry button
    showError() {
        this.streamLoading.style.display = 'none';  // Hide loading message
        this.streamImg.style.display = 'none';      // Hide video
        this.streamError.style.display = 'block';   // Show error message
    }
    
    /*
     * =============================================================================
     * HEALTH MONITORING - Periodically check if stream is working properly
     * =============================================================================
     */
    startHealthCheck() {
        // Check every 45 seconds, but only if page is visible
        this.healthCheckInterval = setInterval(async () => {
            // Skip health check if page is not visible (saves resources)
            if (!this.shouldStreamBeActive()) {
                return;
            }
            
            try {
                // Ask server about relay status
                const response = await fetch('/aquaponics/relay_status');
                const data = await response.json();
                
                // =====================================================================
                // HEALTH CHECK LOGIC - Restart stream if problems detected
                // =====================================================================
                if (data.active_relays === 0 && this.streamActive) {
                    console.log('No active relays detected, restarting stream');
                    this.retryConnection();
                } else if (this.streamActive && this.streamImg.style.display !== 'none') {
                    // Check if image loaded but has no actual content
                    if (this.streamImg.complete && this.streamImg.naturalHeight === 0) {
                        console.log('Stream appears broken during health check, restarting');
                        this.retryConnection();
                    }
                } else if (!this.streamActive && this.shouldStreamBeActive()) {
                    console.log('Stream should be active but is not, restarting');
                    this.retryConnection();
                }
            } catch (error) {
                console.log('Health check failed:', error);
            }
        }, 45000); // Check every 45 seconds
    }
    
    /*
     * =============================================================================
     * CLEANUP - Stop all timers and clean up resources
     * =============================================================================
     */
    cleanup() {
        // Stop all background timers
        if (this.healthCheckInterval) {
            clearInterval(this.healthCheckInterval);
        }
        if (this.visibilityCheckInterval) {
            clearInterval(this.visibilityCheckInterval);
        }
        if (this.loadTimeout) {
            clearTimeout(this.loadTimeout);
        }
        if (this.loadingSpinnerTimeout) {
            clearTimeout(this.loadingSpinnerTimeout);
        }
        
        // Stop the stream
        this.stopStream();
    }
}

/*
 * =============================================================================
 * GLOBAL INITIALIZATION - Set up the stream manager when page loads
 * =============================================================================
 */

// Global variable to hold our stream manager
let streamManager = null;

// Initialize when the HTML page is fully loaded
document.addEventListener('DOMContentLoaded', () => {
    streamManager = new StreamManager();
});

// Clean up when user leaves the page
window.addEventListener('beforeunload', () => {
    if (streamManager) {
        streamManager.cleanup();
    }
});

/*
 * =============================================================================
 * FALLBACK SAFETY NET - Legacy auto-refresh as last resort
 * =============================================================================
 * This is a backup system that runs every 2 minutes to catch any issues
 * that the main monitoring systems might miss
 */
setInterval(() => {
    if (streamManager && streamManager.shouldStreamBeActive()) {
        const streamImg = document.getElementById('stream');
        // If image appears loaded but has no content, restart
        if (streamImg && streamImg.style.display !== 'none' && streamImg.complete && streamImg.naturalHeight === 0) {
            console.log('Legacy fallback: restarting broken stream');
            streamManager.retryConnection();
        }
    }
}, 120000); // Check every 2 minutes as final safety net
