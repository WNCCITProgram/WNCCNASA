/*
 * ============================================================================
 * dual_stream.js
 * Full-featured manager for TWO MJPEG streams (fish + plants).
 * Combines all robustness features from original single stream (stream.js):
 *  - Warmup hint (non-fatal if endpoint missing)
 *  - Delayed spinner (reduces flicker)
 *  - Load timeout + exponential backoff
 *  - Visibility + window focus + IntersectionObserver
 *  - Page bfcache restore handling (pageshow persisted)
 *  - Health monitoring (relay_status optional)
 *  - Legacy fallback safety net (every 2 minutes)
 *  - Broken image detection (naturalHeight === 0)
 *  - Manual retry button (if present)
 *
 * HTML element IDs expected (each optional, code degrades gracefully):
 *   fish:   fish-stream, fish-stream-loading, fish-stream-error, retry-fish-stream
 *   plants: plants-stream, plants-stream-loading, plants-stream-error, retry-plants-stream
 *
 * Global variables expected from template:
 *   window.fishStreamUrl, window.plantsStreamUrl
 * ============================================================================
 * EXTRA EXPLANATION (ADDED):
 * This file controls how two <img> tags on the page receive live MJPEG data.
 * Each <img> points to a Flask proxy endpoint that returns multipart JPEG frames.
 * Instead of just setting img.src once, we manage retries, visibility, and error states
 * so the user experience is smoother even if the network or cameras hiccup.
 */

// Define a class to manage a single camera stream (either fish or plants)
class SingleStreamController {
    // Constructor function - runs when we create a new instance of this class
    constructor(opts) {
        // Core references passed in from the caller
        this.name = opts.name;           // Simple label to tell which stream this is ('fish' or 'plants')
        this.img = opts.img;             // The actual <img> HTML element where stream frames will appear
        this.loadingEl = opts.loadingEl || null;  // Optional HTML element that shows a loading message/spinner
        this.errorEl = opts.errorEl || null;      // Optional HTML element that shows an error message
        this.retryBtn = opts.retryBtn || null;    // Optional button element to let user manually retry
        this.baseUrl = opts.url;                 // Base URL of the stream proxy (server endpoint)

        // Retry logic and current state tracking variables
        this.maxRetries = 5;            // How many times to auto-retry before showing error to user
        this.retryCount = 0;            // How many retries have happened in the current cycle
        this.retryDelay = 2000;         // Delay in milliseconds before the next retry attempt
        this.retryDelayMax = 30000;     // Do not let the retry delay grow beyond this (30 seconds)
        this.streamActive = false;      // Boolean: becomes true once at least one frame loads successfully
        this.lastFrameTime = Date.now();// Timestamp: used to decide when to show the spinner (avoid flicker)

        // Track page/window visibility so we can pause or reduce work if tab/window not active
        this.isPageVisible = true;      // Boolean: true when browser tab is visible (not hidden)
        this.isWindowFocused = true;    // Boolean: true when browser window has focus (not blurred)

        // Timer and interval IDs for cleanup later (JavaScript timers return numeric IDs)
        this.loadTimeout = null;        // Timer: if first frame doesn't arrive in time => trigger error
        this.spinnerTimeout = null;     // Timer: decides when to reveal loading spinner/message
        this.healthCheckInterval = null;// Interval: long-term health monitor that runs periodically
        this.visibilityProbeInterval = null; // Interval: short-term quick check for problems

        // Tunable timing constants (all in milliseconds)
        this.initialLoadTimeoutMs = 20000; // How long to wait for first frame before calling it "stuck" (20 sec)
        this.spinnerDelayMs = 5000;        // Only show loading UI if waiting this long (prevents flash) (5 sec)
        this.healthIntervalMs = 45000;     // How often to run deeper health checks (45 sec)
        this.visibilityProbeMs = 10000;    // How often to run quick stall detection (10 sec)

        this.init(); // Call the initialization function immediately when object is created
    }

    // Initialization function - sets up event handlers and starts the stream
    init() {
        // Safety check: if required elements are missing, silently do nothing and return
        if (!this.img || !this.baseUrl) return;

        // Set up event handlers for the image element
        this.img.onload = () => this.onStreamLoad();   // Arrow function: fires when image successfully loads a frame
        this.img.onerror = () => this.onStreamError(); // Arrow function: fires if connection fails or gets bad data
        
        // If a retry button exists in the HTML, wire it up to our retry function
        if (this.retryBtn) this.retryBtn.onclick = () => this.retryConnection();

        // Set up event listeners to detect when the browser tab becomes hidden or visible again
        document.addEventListener('visibilitychange', () => {
            this.isPageVisible = !document.hidden; // Update our visibility tracking variable
            this.handleVisibilityChange();         // React to the new visibility state
        });
        
        // Set up event listeners to detect when user focuses or unfocuses the browser window
        window.addEventListener('focus', () => {
            this.isWindowFocused = true;           // Track when user focuses the window
            this.handleVisibilityChange();        // React to focus change
        });
        window.addEventListener('blur', () => {
            this.isWindowFocused = false;          // Track when window loses focus
            this.handleVisibilityChange();        // React to blur change
        });
        
        // Before the page fully unloads, stop the stream to cleanup networking
        window.addEventListener('beforeunload', () => this.stopStream());
        
        // Handle case where browser uses back/forward cache (bfcache) - restart stream if needed
        window.addEventListener('pageshow', (e) => {
            if (e.persisted) this.retryConnection(true); // If page came from cache, force restart
        });

        // Use IntersectionObserver API to detect if the stream container is scrolled into view
        // This is an optional performance optimization
        if ('IntersectionObserver' in window && this.img.parentElement) {
            // Create an observer that watches when elements enter/exit the viewport
            const observer = new IntersectionObserver(entries => {
                entries.forEach(entry => {
                    // When parent container enters viewport AND stream is inactive, restart it
                    if (entry.target === this.img.parentElement && entry.isIntersecting) {
                        if (this.shouldBeActive() && !this.streamActive) {
                            this.retryConnection(true); // Force a fresh restart
                        }
                    }
                });
            }, { threshold: 0.1 }); // Trigger when 10% of element is visible
            observer.observe(this.img.parentElement); // Start watching the parent container
        }

        // Attempt backend warmup (this won't break things if it fails)
        this.warmupRelay()
            .finally(() => setTimeout(() => this.startStream(), 400)); // After warmup (success or fail), wait 400ms then start

        // Start periodic monitoring loops that run in the background
        this.startHealthChecks();    // Start the longer-interval health monitor
        this.startVisibilityProbe(); // Start the quicker stall detection probe
    }

    /* ---------------------------- Warmup (optional) ---------------------------- */
    // Async function to attempt warming up the backend relay (makes first connection faster)
    async warmupRelay() {
        try {
            // Create a proper URL object so we can safely extract query parameters from baseUrl
            const url = new URL(this.baseUrl, window.location.origin);
            const params = url.search;       // Get query string part (includes ? if present)
            
            // Call optional warmup endpoint on server (safe even if endpoint returns 404)
            const resp = await fetch('/aquaponics/warmup_relay' + params, { method: 'GET' });
            if (!resp.ok) return;            // If response not OK (404, 500, etc), skip silently
            await resp.json().catch(() => {}); // Try to parse JSON response, ignore if invalid
        } catch (_) { 
            /* ignore all errors silently - warmup is best-effort only */ 
        }
    }

    /* --------------------------- Visibility decisions -------------------------- */
    // Function to determine if the stream should be actively running
    shouldBeActive() {
        // Only treat stream as "should run" if BOTH tab is visible AND window has focus
        return this.isPageVisible && this.isWindowFocused;
    }

    // Function called whenever visibility or focus state changes
    handleVisibilityChange() {
        // If we just became visible/focused AND stream is currently off, restart it
        if (this.shouldBeActive()) {
            if (!this.streamActive) this.retryConnection(true); // Force fresh restart
        }
        // Note: we don't explicitly pause streams when hidden - they'll restart when visible again
    }

    /* ----------------------------- Stream lifecycle ---------------------------- */
    // Main function to start or restart the stream
    startStream() {
        // Do nothing if user can't currently see or interact with the page
        if (!this.shouldBeActive()) return;

        this.retryCount++; // Increment counter - record that we're attempting (or re-attempting) a connection

        // Show loading container immediately (but do not change its text content)
        if (this.loadingEl) {
            this.loadingEl.style.display = 'block';    // Make loading element visible
            if (this.errorEl) this.errorEl.style.display = 'none';  // Hide error element if it exists
            if (this.img) this.img.style.display = 'none';          // Hide image element initially
        }

        // NEW: Immediately show original loading text for first attempt only
        if (this.retryCount === 1 && this.loadingEl) {
            this.loadingEl.textContent = this.originalLoadingText; // Restore any original loading message
        }

        // Set up delayed spinner reveal to avoid distracting flicker for fast connections
        if (this.spinnerTimeout) clearTimeout(this.spinnerTimeout); // Cancel any existing spinner timer
        this.spinnerTimeout = setTimeout(() => {
            // Only show spinner if still not loaded AND enough time has passed since last frame
            if (!this.streamActive && Date.now() - this.lastFrameTime > this.spinnerDelayMs) {
                this.showLoading(); // Switch to standard loading display
            }
        }, this.spinnerDelayMs);

        // Set up timeout: if first frame doesn't show up in time, trigger error handling
        if (this.loadTimeout) clearTimeout(this.loadTimeout); // Cancel any existing load timer
        this.loadTimeout = setTimeout(() => this.onStreamError(), this.initialLoadTimeoutMs);

        // Create URL with cache-busting timestamp so browser doesn't reuse a cached image
        const url = this.baseUrl + (this.baseUrl.includes('?') ? '&' : '?') + 't=' + Date.now();
        this.img.src = url; // Setting img.src starts fetching the MJPEG stream from server
    }

    // Function to stop the stream and clean up timers
    stopStream() {
        // Cancel any active timers to prevent them from firing after stream is stopped
        if (this.loadTimeout) clearTimeout(this.loadTimeout);
        if (this.spinnerTimeout) clearTimeout(this.spinnerTimeout);
        
        // Clearing img.src stops all network activity for this image element
        this.img.src = '';
        this.streamActive = false; // Mark stream as inactive
    }

    // Function to retry the connection (either forced fresh start or continued from current state)
    retryConnection(force = false) {
        // If force is true, reset retry counters like we're starting over completely fresh
        if (force) {
            this.retryCount = 0;     // Reset attempt counter to zero
            this.retryDelay = 2000;  // Reset delay back to initial 2 seconds
        }
        this.streamActive = false;   // Mark stream as inactive
        this.startStream();          // Start the stream (which will increment retryCount)
    }

    /* ---------------------------- Event handlers ------------------------------- */
    // Event handler called when image successfully loads a frame
    onStreamLoad() {
        // Cancel timers since we got a successful frame
        if (this.loadTimeout) clearTimeout(this.loadTimeout);
        if (this.spinnerTimeout) clearTimeout(this.spinnerTimeout);
        
        this.streamActive = true;        // Mark stream as successfully active
        this.lastFrameTime = Date.now(); // Update timestamp so spinner logic works correctly
        this.retryCount = 0;             // Reset retry counter since connection worked
        this.retryDelay = 2000;          // Reset delay back to initial 2-second value
        this.showStream();               // Switch UI to show the live image and hide loading/error
    }

    // Event handler called when image fails to load (timeout or network error)
    onStreamError() {
        // Cancel load timeout since we're now handling the error
        if (this.loadTimeout) clearTimeout(this.loadTimeout);
        this.streamActive = false; // Mark stream as inactive

        // If user can't see the page/window, wait until they return (don't waste resources)
        if (!this.shouldBeActive()) return;

        // Check if we should try again or give up
        if (this.retryCount < this.maxRetries) {
            // Schedule a retry with exponentially growing delay (but capped at maximum)
            setTimeout(() => {
                // Increase delay by 50% each time, but don't exceed the maximum
                this.retryDelay = Math.min(this.retryDelay * 1.5, this.retryDelayMax);
                this.startStream(); // Try starting the stream again
            }, this.retryDelay);
        } else {
            // Too many retries failed -> show error UI to user
            this.showError();
        }
    }

    /* ------------------------------- UI states -------------------------------- */
    // Function to show only the loading UI element
    showLoading() {
        if (this.loadingEl) this.loadingEl.style.display = 'block';  // Show loading
        if (this.errorEl) this.errorEl.style.display = 'none';       // Hide error
        if (this.img) this.img.style.display = 'none';               // Hide image
    }

    // Function to show only the stream image
    showStream() {
        if (this.loadingEl) this.loadingEl.style.display = 'none';   // Hide loading
        if (this.errorEl) this.errorEl.style.display = 'none';       // Hide error
        if (this.img) this.img.style.display = 'block';              // Show image
    }

    // Function to show only the error message
    showError() {
        if (this.loadingEl) this.loadingEl.style.display = 'none';   // Hide loading
        if (this.errorEl) this.errorEl.style.display = 'block';      // Show error
        if (this.img) this.img.style.display = 'none';               // Hide image
    }

    /* -------------------------- Background monitoring -------------------------- */
    // Function to start periodic health checks (runs less frequently for deeper checks)
    startHealthChecks() {
        // Set up interval that runs every healthIntervalMs (45 seconds) to detect silent failures
        this.healthCheckInterval = setInterval(async () => {
            // Don't run health check if user isn't looking at the page
            if (!this.shouldBeActive()) return;

            // Check if image element says it's "loaded" but has zero dimensions (indicates broken stream)
            if (this.streamActive && this.img.complete && this.img.naturalHeight === 0) {
                this.retryConnection(true); // Force a fresh restart
                return; // Exit early since we're restarting
            }
            
            // If we think the stream is OFF but user is actively viewing -> try to restart automatically
            if (!this.streamActive) {
                this.retryConnection(false); // Continue with current retry sequence
            }

            // Optional server-side relay status check (gracefully ignore if endpoint doesn't exist)
            try {
                // Fetch relay status from server with no caching
                const resp = await fetch('/aquaponics/relay_status', { cache: 'no-store' });
                if (!resp.ok) return; // If request fails, skip this check
                
                const data = await resp.json(); // Parse JSON response
                // If server reports "no active relays" while we think we are active, restart
                if (data.active_relays === 0 && this.streamActive) {
                    this.retryConnection(true); // Force fresh restart
                }
            } catch (_) { 
                /* ignore any fetch errors or JSON parsing errors */ 
            }
        }, this.healthIntervalMs);
    }

    // Function to start faster lightweight checks to catch stalled frames sooner
    startVisibilityProbe() {
        // Set up interval that runs every visibilityProbeMs (10 seconds) for quick stall detection
        this.visibilityProbeInterval = setInterval(() => {
            // Don't run probe if user isn't looking at the page
            if (!this.shouldBeActive()) return;
            
            // Quick check: if image claims to be loaded but has zero height, restart
            if (this.streamActive && this.img.complete && this.img.naturalHeight === 0) {
                this.retryConnection(true); // Force fresh restart
            }
        }, this.visibilityProbeMs);
    }

    // Extra safety net function (triggered less frequently by the manager class)
    legacyFallbackCheck() {
        // Final check for broken image state - only restart if all conditions met
        if (this.shouldBeActive() &&                    // User can see the page
            this.img.style.display !== 'none' &&        // Image is supposed to be visible
            this.img.complete &&                         // Browser says image is "loaded"
            this.img.naturalHeight === 0) {              // But image has no actual height
            this.retryConnection(true); // Force a fresh restart
        }
    }

    /* ------------------------------- Cleanup ----------------------------------- */
    // Function to stop all intervals and timers and release resources
    cleanup() {
        // Stop all background monitoring intervals
        if (this.healthCheckInterval) clearInterval(this.healthCheckInterval);
        if (this.visibilityProbeInterval) clearInterval(this.visibilityProbeInterval);
        
        // Cancel any pending timers
        if (this.loadTimeout) clearTimeout(this.loadTimeout);
        if (this.spinnerTimeout) clearTimeout(this.spinnerTimeout);
        
        this.stopStream(); // Stop the stream and clear img.src
    }
}

/* ---------------------------- Dual manager wrapper --------------------------- */
// Class that manages both fish and plants streams together
class DualStreamManager {
    // Constructor creates controller instances for both cameras
    constructor() {
        // Create one SingleStreamController instance for the fish camera
        this.fish = new SingleStreamController({
            name: 'fish',                                          // Identifier for this stream
            img: document.getElementById('fish-stream'),           // Find the fish image element in HTML
            loadingEl: document.getElementById('fish-stream-loading'), // Find fish loading element (optional)
            errorEl: document.getElementById('fish-stream-error'),     // Find fish error element (optional)
            retryBtn: document.getElementById('retry-fish-stream'),    // Find fish retry button (optional)
            url: window.fishStreamUrl                                  // Get fish stream URL from global variable
        });

        // Create one SingleStreamController instance for the plants camera
        this.plants = new SingleStreamController({
            name: 'plants',                                            // Identifier for this stream
            img: document.getElementById('plants-stream'),             // Find the plants image element in HTML
            loadingEl: document.getElementById('plants-stream-loading'), // Find plants loading element (optional)
            errorEl: document.getElementById('plants-stream-error'),     // Find plants error element (optional)
            retryBtn: document.getElementById('retry-plants-stream'),    // Find plants retry button (optional)
            url: window.plantsStreamUrl                                  // Get plants stream URL from global variable
        });

        // Set up occasional extra fallback check that helps catch corner cases both monitors might miss
        this.legacyInterval = setInterval(() => {
            // Call legacy fallback check on both streams (if they exist)
            this.fish && this.fish.legacyFallbackCheck();     // Check fish stream health
            this.plants && this.plants.legacyFallbackCheck(); // Check plants stream health
        }, 120000); // Run every 2 minutes (120,000 milliseconds)
    }

    // Function to clean up both stream controllers and stop the legacy interval
    cleanup() {
        // Stop the legacy fallback interval
        if (this.legacyInterval) clearInterval(this.legacyInterval);
        
        // Clean up individual stream controllers (if they exist)
        this.fish && this.fish.cleanup();     // Clean up fish stream
        this.plants && this.plants.cleanup(); // Clean up plants stream
    }
}

/* ---------------------------- Global initialization -------------------------- */
let dualStreamManager = null; // Global variable to hold reference to our manager so we can clean up later

// Wait for HTML document to be fully parsed before initializing
document.addEventListener('DOMContentLoaded', () => {
    // Create the dual stream manager instance (this starts both camera streams)
    dualStreamManager = new DualStreamManager();
});

// Before the page unloads, ensure all timers and network connections are properly stopped
window.addEventListener('beforeunload', () => {
    // Clean up the manager if it exists (stops all timers, intervals, and network requests)
    if (dualStreamManager) {
        dualStreamManager.cleanup();
    }
});