// Enhanced stream management with proper loading states and visibility handling
class StreamManager {
    constructor() {
        this.streamImg = document.getElementById('stream');
        this.streamLoading = document.getElementById('stream-loading');
        this.streamError = document.getElementById('stream-error');
        this.retryButton = document.getElementById('retry-stream');
        
        this.maxRetries = 5;
        this.retryCount = 0;
        this.retryDelay = 2000; // Start with 2 seconds
        this.loadTimeout = null;
        this.healthCheckInterval = null;
        this.visibilityCheckInterval = null;
        
        // Page visibility tracking
        this.isPageVisible = true;
        this.isWindowFocused = true;
        this.streamActive = false;
        
        this.init();
    }
    
    init() {
        if (!this.streamImg || !window.streamUrl) {
            console.error('Stream elements or URL not found');
            return;
        }
        
        // Set up event listeners
        this.streamImg.onload = () => this.onStreamLoad();
        this.streamImg.onerror = () => this.onStreamError();
        this.retryButton.onclick = () => this.retryConnection();
        
        // Set up visibility and focus listeners
        this.setupVisibilityHandlers();
        
        // Pre-warm the relay before starting the stream
        this.warmupRelay().then(() => {
            // Start the stream after warmup
            setTimeout(() => {
                this.startStream();
            }, 500);
        }).catch(() => {
            // If warmup fails, try anyway
            setTimeout(() => {
                this.startStream();
            }, 1000);
        });
        
        // Set up periodic health check
        this.startHealthCheck();
        
        // Set up visibility monitoring
        this.startVisibilityMonitoring();
    }
    
    setupVisibilityHandlers() {
        // Page Visibility API
        document.addEventListener('visibilitychange', () => {
            this.isPageVisible = !document.hidden;
            console.log('Page visibility changed:', this.isPageVisible ? 'visible' : 'hidden');
            this.handleVisibilityChange();
        });
        
        // Window focus/blur events
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
        
        // Page lifecycle events
        window.addEventListener('beforeunload', () => {
            console.log('Page unloading, stopping stream');
            this.stopStream();
        });
        
        // Handle page reload/back button
        window.addEventListener('pageshow', (event) => {
            if (event.persisted) {
                console.log('Page restored from cache, restarting stream');
                this.retryConnection();
            }
        });
        
        // Intersection Observer to detect if stream element is in viewport
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
            }, { threshold: 0.1 });
            
            observer.observe(this.streamImg.parentElement);
        }
    }
    
    handleVisibilityChange() {
        if (this.shouldStreamBeActive()) {
            if (!this.streamActive || this.streamImg.style.display === 'none') {
                console.log('Page is visible, ensuring stream is active');
                this.retryConnection();
            }
        } else {
            console.log('Page is not visible, stream can pause');
            // Optionally pause stream when not visible to save bandwidth
            // this.pauseStream();
        }
    }
    
    shouldStreamBeActive() {
        return this.isPageVisible && this.isWindowFocused;
    }
    
    startVisibilityMonitoring() {
        // Check stream health when page becomes visible
        this.visibilityCheckInterval = setInterval(() => {
            if (this.shouldStreamBeActive() && this.streamActive) {
                // Check if image is actually displaying
                if (this.streamImg.complete && this.streamImg.naturalHeight === 0) {
                    console.log('Stream appears broken, restarting');
                    this.retryConnection();
                }
            }
        }, 10000); // Check every 10 seconds
    }
    
    async warmupRelay() {
        try {
            const url = new URL(window.streamUrl, window.location.origin);
            const params = new URLSearchParams(url.search);
            
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
    
    startStream() {
        if (!this.shouldStreamBeActive()) {
            console.log('Page not visible, delaying stream start');
            return;
        }
        
        this.showLoading();
        this.retryCount++;
        
        // Clear any existing timeout
        if (this.loadTimeout) {
            clearTimeout(this.loadTimeout);
        }
        
        // Set a timeout for loading - increased for better stability
        this.loadTimeout = setTimeout(() => {
            this.onStreamError();
        }, 20000); // Increased from 15 to 20 second timeout
        
        // Add cache busting parameter
        const url = window.streamUrl + (window.streamUrl.includes('?') ? '&' : '?') + 't=' + new Date().getTime();
        this.streamImg.src = url;
        console.log('Starting stream:', url);
    }
    
    stopStream() {
        if (this.loadTimeout) {
            clearTimeout(this.loadTimeout);
        }
        this.streamImg.src = '';
        this.streamActive = false;
        console.log('Stream stopped');
    }
    
    onStreamLoad() {
        console.log('Stream loaded successfully');
        if (this.loadTimeout) {
            clearTimeout(this.loadTimeout);
        }
        
        this.retryCount = 0;
        this.retryDelay = 2000;
        this.streamActive = true;
        this.showStream();
    }
    
    onStreamError() {
        console.log('Stream error occurred, retry count:', this.retryCount);
        if (this.loadTimeout) {
            clearTimeout(this.loadTimeout);
        }
        
        this.streamActive = false;
        
        // Only retry if page is visible
        if (this.shouldStreamBeActive() && this.retryCount < this.maxRetries) {
            // Exponential backoff
            setTimeout(() => {
                this.retryDelay = Math.min(this.retryDelay * 1.5, 30000);
                this.startStream();
            }, this.retryDelay);
        } else if (!this.shouldStreamBeActive()) {
            console.log('Page not visible, not retrying stream');
        } else {
            this.showError();
        }
    }
    
    retryConnection() {
        this.retryCount = 0;
        this.retryDelay = 2000;
        this.streamActive = false;
        this.startStream();
    }
    
    showLoading() {
        this.streamImg.style.display = 'none';
        this.streamError.style.display = 'none';
        this.streamLoading.style.display = 'block';
    }
    
    showStream() {
        this.streamLoading.style.display = 'none';
        this.streamError.style.display = 'none';
        this.streamImg.style.display = 'block';
    }
    
    showError() {
        this.streamLoading.style.display = 'none';
        this.streamImg.style.display = 'none';
        this.streamError.style.display = 'block';
    }
    
    startHealthCheck() {
        // Check relay status every 45 seconds, but only if page is visible
        this.healthCheckInterval = setInterval(async () => {
            if (!this.shouldStreamBeActive()) {
                return; // Skip health check if page is not visible
            }
            
            try {
                const response = await fetch('/aquaponics/relay_status');
                const data = await response.json();
                
                if (data.active_relays === 0 && this.streamActive) {
                    console.log('No active relays detected, restarting stream');
                    this.retryConnection();
                } else if (this.streamActive && this.streamImg.style.display !== 'none') {
                    // Check if image is actually loading
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
        }, 45000); // Increased from 30 to 45 seconds to reduce server load
    }
    
    cleanup() {
        // Clean up intervals and event listeners
        if (this.healthCheckInterval) {
            clearInterval(this.healthCheckInterval);
        }
        if (this.visibilityCheckInterval) {
            clearInterval(this.visibilityCheckInterval);
        }
        if (this.loadTimeout) {
            clearTimeout(this.loadTimeout);
        }
        this.stopStream();
    }
}

// Global stream manager instance
let streamManager = null;

// Initialize stream manager when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    streamManager = new StreamManager();
});

// Clean up when page unloads
window.addEventListener('beforeunload', () => {
    if (streamManager) {
        streamManager.cleanup();
    }
});

// Legacy auto-refresh for fallback (much reduced frequency since we have better monitoring)
setInterval(() => {
    if (streamManager && streamManager.shouldStreamBeActive()) {
        const streamImg = document.getElementById('stream');
        if (streamImg && streamImg.style.display !== 'none' && streamImg.complete && streamImg.naturalHeight === 0) {
            console.log('Legacy fallback: restarting broken stream');
            streamManager.retryConnection();
        }
    }
}, 120000); // Check every 2 minutes as final fallback
