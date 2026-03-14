/**
 * Breathing Inspiration Experience with Carousel
 * JavaScript for dynamic color adaptation, content rotation, and carousel functionality
 */

class ImageCarousel {
    constructor(images, options = {}) {
        this.images = images || [];
        this.currentIndex = 0;
        this.timer = null;
        this.isPlaying = false;
        this.isPaused = false;
        
        // Configuration from options or defaults
        this.imageDuration = options.imageDuration || 5000; // 5 seconds
        this.transitionDuration = options.transitionDuration || 1500; // 1.5 seconds
        this.kenBurnsEnabled = options.kenBurnsEnabled !== false; // Default enabled
        
        // Callback functions
        this.onImageChange = options.onImageChange || (() => {});
        this.onComplete = options.onComplete || (() => {});
        
        // DOM elements
        this.mainImageEl = document.getElementById('main-image');
        this.mobileImageEl = document.getElementById('mobile-image');
        this.indicatorsEl = document.getElementById('carousel-indicators');
        this.mobileIndicatorsEl = document.getElementById('mobile-carousel-indicators');
        
        // Ken Burns state
        this.kenBurnsAnimations = ['ken-burns-in', 'ken-burns-out', 'ken-burns-pan-left', 'ken-burns-pan-right'];
        this.currentKenBurns = 0;
        
        // Image preloading
        this.preloadedImages = new Map();
        
        // Check for reduced motion preference
        this.prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
        if (this.prefersReducedMotion) {
            this.kenBurnsEnabled = false;
        }
        
        // Touch gesture state
        this.touchStartX = 0;
        this.touchStartY = 0;
        this.touchStartTime = 0;
        this.isTouchSwiping = false;
        this.minSwipeDistance = 50;
        this.maxSwipeTime = 300;
        
        this.init();
    }
    
    init() {
        if (this.images.length <= 1) {
            this.hideIndicators();
            return;
        }
        
        this.createIndicators();
        this.showIndicators();
        this.updateIndicators();
        this.setupTouchHandlers();
    }
    
    createIndicators() {
        const createDots = (container) => {
            if (!container) return;
            
            container.innerHTML = '';
            this.images.forEach((_, index) => {
                const dot = document.createElement('button');
                dot.className = 'carousel-dot';
                dot.setAttribute('aria-label', `View variation ${index + 1}`);
                dot.addEventListener('click', () => {
                    this.goToIndex(index);
                });
                container.appendChild(dot);
            });
        };
        
        createDots(this.indicatorsEl);
        createDots(this.mobileIndicatorsEl);
    }
    
    updateIndicators() {
        const updateDots = (container) => {
            if (!container) return;
            
            const dots = container.querySelectorAll('.carousel-dot');
            dots.forEach((dot, index) => {
                dot.classList.toggle('active', index === this.currentIndex);
            });
        };
        
        updateDots(this.indicatorsEl);
        updateDots(this.mobileIndicatorsEl);
    }
    
    setupTouchHandlers() {
        // Set up touch events on image elements for swipe gestures
        const imageElements = [this.mainImageEl, this.mobileImageEl].filter(el => el);
        
        imageElements.forEach(element => {
            if (!element) return;
            
            // Touch start
            element.addEventListener('touchstart', (e) => {
                const touch = e.touches[0];
                this.touchStartX = touch.clientX;
                this.touchStartY = touch.clientY;
                this.touchStartTime = Date.now();
                this.isTouchSwiping = false;
            }, { passive: true });
            
            // Touch move - detect if user is swiping
            element.addEventListener('touchmove', (e) => {
                if (e.touches.length !== 1) return;
                
                const touch = e.touches[0];
                const deltaX = Math.abs(touch.clientX - this.touchStartX);
                const deltaY = Math.abs(touch.clientY - this.touchStartY);
                
                // If horizontal movement is greater than vertical, it's a swipe
                if (deltaX > deltaY && deltaX > 10) {
                    this.isTouchSwiping = true;
                    // Prevent scrolling during horizontal swipes
                    e.preventDefault();
                }
            });
            
            // Touch end - process swipe
            element.addEventListener('touchend', (e) => {
                if (!this.isTouchSwiping || e.changedTouches.length !== 1) return;
                
                const touch = e.changedTouches[0];
                const deltaX = touch.clientX - this.touchStartX;
                const deltaY = Math.abs(touch.clientY - this.touchStartY);
                const deltaTime = Date.now() - this.touchStartTime;
                
                // Check if it's a valid swipe (horizontal, fast enough, long enough)
                if (Math.abs(deltaX) >= this.minSwipeDistance && 
                    deltaTime <= this.maxSwipeTime && 
                    deltaY <= Math.abs(deltaX) / 2) {
                    
                    // Prevent default tap behavior
                    e.preventDefault();
                    
                    if (deltaX > 0) {
                        // Swipe right - go to previous image
                        this.previous();
                    } else {
                        // Swipe left - go to next image
                        this.next();
                    }
                }
                
                this.isTouchSwiping = false;
            }, { passive: false });
        });
    }
    
    showIndicators() {
        if (this.indicatorsEl) this.indicatorsEl.classList.remove('hidden');
        if (this.mobileIndicatorsEl) this.mobileIndicatorsEl.classList.remove('hidden');
    }
    
    hideIndicators() {
        if (this.indicatorsEl) this.indicatorsEl.classList.add('hidden');
        if (this.mobileIndicatorsEl) this.mobileIndicatorsEl.classList.add('hidden');
    }
    
    async updateImage() {
        if (this.currentIndex >= this.images.length) return;
        
        const image = this.images[this.currentIndex];
        const imagePath = image.path;
        
        try {
            // Use preloaded image if available, otherwise load normally
            let imageLoaded = this.preloadedImages.has(imagePath);
            
            if (!imageLoaded) {
                const response = await fetch(imagePath);
                if (!response.ok) {
                    throw new Error('Image not found');
                }
            }
            
            // Clear any existing Ken Burns animations
            this.clearKenBurnsAnimations();
            
            // Update image sources with smooth transition
            if (this.mainImageEl) {
                this.mainImageEl.classList.add('carousel-image-transition');
                this.mainImageEl.src = imagePath;
                this.mainImageEl.alt = `AI-generated artwork variation ${this.currentIndex + 1} of ${this.images.length}`;
            }
            if (this.mobileImageEl) {
                this.mobileImageEl.classList.add('carousel-image-transition');
                this.mobileImageEl.src = imagePath;
                this.mobileImageEl.alt = `AI-generated artwork variation ${this.currentIndex + 1} of ${this.images.length}`;
            }
            
            // Apply Ken Burns effect after a short delay
            if (this.kenBurnsEnabled) {
                setTimeout(() => {
                    this.applyKenBurnsEffect();
                }, 100);
            }
            
            // Preload next image
            this.preloadNextImage();
            
            // Notify parent of image change
            this.onImageChange(this.currentIndex, image);
            
        } catch (error) {
            console.warn('Carousel image not found:', imagePath);
            // Try next image or fallback
        }
    }
    
    clearKenBurnsAnimations() {
        const elements = [this.mainImageEl, this.mobileImageEl].filter(el => el);
        elements.forEach(el => {
            this.kenBurnsAnimations.forEach(animClass => {
                el.classList.remove(animClass);
            });
        });
    }
    
    applyKenBurnsEffect() {
        if (!this.kenBurnsEnabled) return;
        
        // Randomly select Ken Burns animation
        const animationIndex = Math.floor(Math.random() * this.kenBurnsAnimations.length);
        const animationClass = this.kenBurnsAnimations[animationIndex];
        
        const elements = [this.mainImageEl, this.mobileImageEl].filter(el => el);
        elements.forEach(el => {
            el.classList.add(animationClass);
        });
        
        this.currentKenBurns = animationIndex;
    }
    
    preloadNextImage() {
        if (this.images.length <= 1) return;
        
        // Preload the next 2 images for smoother navigation
        const nextIndex = (this.currentIndex + 1) % this.images.length;
        const nextNextIndex = (this.currentIndex + 2) % this.images.length;
        
        this.preloadImage(this.images[nextIndex].path, true); // High priority
        
        // Only preload the second next image if we have more than 2 images
        if (this.images.length > 2) {
            this.preloadImage(this.images[nextNextIndex].path, false); // Low priority
        }
    }
    
    preloadImage(imagePath, highPriority = false) {
        if (this.preloadedImages.has(imagePath)) return;
        
        // Use Intersection Observer API for better performance if available
        if (window.IntersectionObserver && !highPriority) {
            this.lazyPreloadImage(imagePath);
        } else {
            this.immediatePreloadImage(imagePath, highPriority);
        }
    }
    
    immediatePreloadImage(imagePath, highPriority = false) {
        const img = new Image();
        img.onload = () => {
            this.preloadedImages.set(imagePath, true);
        };
        img.onerror = () => {
            console.warn('Failed to preload image:', imagePath);
            this.preloadedImages.set(imagePath, false);
        };
        
        // Use fetchpriority if supported (modern browsers)
        if ('fetchPriority' in img && highPriority) {
            img.fetchPriority = 'high';
        }
        
        img.src = imagePath;
    }
    
    lazyPreloadImage(imagePath) {
        // Create a dummy element for intersection observation
        const placeholder = document.createElement('div');
        placeholder.style.position = 'absolute';
        placeholder.style.top = '0';
        placeholder.style.left = '0';
        placeholder.style.width = '1px';
        placeholder.style.height = '1px';
        placeholder.style.visibility = 'hidden';
        document.body.appendChild(placeholder);
        
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    this.immediatePreloadImage(imagePath, false);
                    observer.disconnect();
                    document.body.removeChild(placeholder);
                }
            });
        }, {
            rootMargin: '100px' // Start loading when 100px away from viewport
        });
        
        observer.observe(placeholder);
        
        // Cleanup after 5 seconds if not triggered
        setTimeout(() => {
            try {
                observer.disconnect();
                if (placeholder.parentNode) {
                    document.body.removeChild(placeholder);
                }
            } catch (e) {
                // Element already removed, ignore
            }
        }, 5000);
    }
    
    start() {
        if (this.images.length <= 1) return;
        
        this.isPlaying = true;
        this.isPaused = false;
        this.scheduleNext();
    }
    
    pause() {
        this.isPaused = true;
        if (this.timer) {
            clearTimeout(this.timer);
            this.timer = null;
        }
    }
    
    resume() {
        if (this.isPlaying && this.isPaused) {
            this.isPaused = false;
            this.scheduleNext();
        }
    }
    
    stop() {
        this.isPlaying = false;
        this.isPaused = false;
        if (this.timer) {
            clearTimeout(this.timer);
            this.timer = null;
        }
    }
    
    scheduleNext() {
        if (!this.isPlaying || this.isPaused) return;
        
        this.timer = setTimeout(() => {
            this.next();
        }, this.imageDuration);
    }
    
    next() {
        if (this.images.length <= 1) {
            this.onComplete();
            return;
        }
        
        this.currentIndex = (this.currentIndex + 1) % this.images.length;
        
        // If we've completed the cycle, notify parent
        if (this.currentIndex === 0) {
            this.stop();
            this.onComplete();
            return;
        }
        
        this.updateImage();
        this.updateIndicators();
        this.scheduleNext();
    }
    
    previous() {
        if (this.images.length <= 1) return;
        
        this.currentIndex = this.currentIndex === 0 ? this.images.length - 1 : this.currentIndex - 1;
        this.updateImage();
        this.updateIndicators();
    }
    
    goToIndex(index) {
        if (index < 0 || index >= this.images.length || index === this.currentIndex) return;
        
        // Pause auto-advance when user manually navigates
        this.pause();
        
        // Smooth transition to new index
        this.transitionToIndex(index);
        
        // Resume after a brief delay
        setTimeout(() => {
            this.resume();
        }, 2000);
    }
    
    async transitionToIndex(index) {
        // Add momentum-based easing for smoother user navigation
        const distance = Math.abs(index - this.currentIndex);
        const transitionDelay = Math.min(distance * 100, 300); // Max 300ms delay
        
        // Fade out current image slightly
        const elements = [this.mainImageEl, this.mobileImageEl].filter(el => el);
        elements.forEach(el => {
            if (el) {
                el.style.opacity = '0.7';
                el.style.transition = 'opacity 0.3s ease-out';
            }
        });
        
        // Wait for transition
        await new Promise(resolve => setTimeout(resolve, transitionDelay));
        
        // Update to new index
        this.currentIndex = index;
        await this.updateImage();
        this.updateIndicators();
        
        // Fade back in
        setTimeout(() => {
            elements.forEach(el => {
                if (el) {
                    el.style.opacity = '1';
                    el.style.transition = 'opacity 0.5s ease-in';
                }
            });
        }, 100);
    }
    
    destroy() {
        this.stop();
        this.hideIndicators();
        this.clearKenBurnsAnimations();
        this.removeTouchHandlers();
    }
    
    removeTouchHandlers() {
        // Touch handlers are automatically cleaned up when elements are replaced
        // This is a placeholder for explicit cleanup if needed
    }
}

/**
 * Performance Logger for tracking timing and debugging load issues
 *
 * USAGE FROM BROWSER CONSOLE:
 *
 * View statistics:
 *   perfLogger.getStats()
 *
 * Export logs to JSON file:
 *   perfLogger.exportLogs()
 *
 * View raw events:
 *   perfLogger.events
 *
 * Clear logs:
 *   localStorage.removeItem('perf_log')
 *
 * Disable logging:
 *   perfLogger.enabled = false
 */
class PerformanceLogger {
    constructor() {
        this.sessionId = this.getOrCreateSessionId();
        this.events = [];
        this.startTime = performance.now();
        this.enabled = true; // Set to false to disable logging

        // Server logging configuration
        this.serverLoggingEnabled = true; // Set to false for localStorage only
        this.logEndpoint = window.location.hostname === 'localhost'
            ? 'http://localhost:8000/log.php'  // Local testing
            : 'https://rennie.org/log.php';     // Production
        this.batchSize = 5; // Send logs in batches
        this.batchBuffer = [];
        this.batchTimeout = null;
        this.batchDelay = 2000; // Send batch after 2 seconds of inactivity

        // Log initial page load metrics
        this.logPageLoadMetrics();

        // Flush logs on page unload
        this.setupUnloadHandler();
    }

    getOrCreateSessionId() {
        let sessionId = sessionStorage.getItem('perf_session_id');
        if (!sessionId) {
            sessionId = `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
            sessionStorage.setItem('perf_session_id', sessionId);
        }
        return sessionId;
    }

    detectCacheStatus() {
        // Check if this is likely a cached vs fresh load
        const perfData = performance.getEntriesByType('navigation')[0];
        if (perfData && perfData.transferSize !== undefined) {
            // transferSize of 0 typically means cached
            return perfData.transferSize === 0 ? 'cached' : 'network';
        }
        return 'unknown';
    }

    logPageLoadMetrics() {
        if (!this.enabled) return;

        const perfData = performance.getEntriesByType('navigation')[0];
        if (perfData) {
            this.log('page_load_metrics', {
                dns: Math.round(perfData.domainLookupEnd - perfData.domainLookupStart),
                tcp: Math.round(perfData.connectEnd - perfData.connectStart),
                request: Math.round(perfData.responseStart - perfData.requestStart),
                response: Math.round(perfData.responseEnd - perfData.responseStart),
                domLoad: Math.round(perfData.domContentLoadedEventEnd - perfData.domContentLoadedEventStart),
                totalLoad: Math.round(perfData.loadEventEnd - perfData.fetchStart),
                transferSize: perfData.transferSize
            });
        }
    }

    log(eventName, metadata = {}) {
        if (!this.enabled) return;

        const now = performance.now();
        const event = {
            sessionId: this.sessionId,
            timestamp: new Date().toISOString(),
            relativeTime: Math.round(now - this.startTime),
            event: eventName,
            cacheStatus: this.detectCacheStatus(),
            ...metadata
        };

        this.events.push(event);

        // Console output with color coding
        const color = this.getEventColor(eventName);
        console.log(`%c[PERF ${event.relativeTime}ms] ${eventName}`, `color: ${color}; font-weight: bold`, metadata);

        // Persist to localStorage (keep last 100 events)
        this.persist(event);
    }

    getEventColor(eventName) {
        if (eventName.includes('_start')) return '#3498db';
        if (eventName.includes('_complete') || eventName.includes('_loaded')) return '#2ecc71';
        if (eventName.includes('_error') || eventName.includes('_failed')) return '#e74c3c';
        if (eventName.includes('transition') || eventName.includes('fade')) return '#9b59b6';
        return '#95a5a6';
    }

    persist(event) {
        try {
            // Save to localStorage as backup
            const storageKey = 'perf_log';
            let logs = JSON.parse(localStorage.getItem(storageKey) || '[]');
            logs.push(event);

            // Keep only last 100 events to avoid storage bloat
            if (logs.length > 100) {
                logs = logs.slice(-100);
            }

            localStorage.setItem(storageKey, JSON.stringify(logs));

            // Send to server if enabled
            if (this.serverLoggingEnabled) {
                this.sendToServer(event);
            }
        } catch (e) {
            console.warn('Failed to persist performance log:', e);
        }
    }

    sendToServer(event) {
        // Add to batch buffer
        this.batchBuffer.push(event);

        // Clear existing timeout
        if (this.batchTimeout) {
            clearTimeout(this.batchTimeout);
        }

        // Send immediately if batch is full
        if (this.batchBuffer.length >= this.batchSize) {
            this.flushBatch();
        } else {
            // Otherwise, schedule a flush after delay
            this.batchTimeout = setTimeout(() => {
                this.flushBatch();
            }, this.batchDelay);
        }
    }

    flushBatch() {
        if (this.batchBuffer.length === 0) return;

        const batch = [...this.batchBuffer];
        this.batchBuffer = [];

        // Send each event individually (simpler server-side processing)
        batch.forEach(event => {
            fetch(this.logEndpoint, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(event),
                keepalive: true // Ensures logs send even if user navigates away
            }).catch(err => {
                // Silently fail - logs are already in localStorage as backup
                if (this.enabled) {
                    console.warn('Failed to send log to server:', err);
                }
            });
        });
    }

    setupUnloadHandler() {
        // Flush any remaining logs when page unloads
        window.addEventListener('beforeunload', () => {
            this.flushBatch();
        });

        // Also flush on visibility change (mobile/tab switches)
        document.addEventListener('visibilitychange', () => {
            if (document.hidden) {
                this.flushBatch();
            }
        });
    }

    getStats() {
        // Analyze timing statistics
        const imageLoads = this.events.filter(e => e.event === 'image_loaded');
        const transitions = this.events.filter(e => e.event.includes('transition'));

        return {
            totalEvents: this.events.length,
            sessionId: this.sessionId,
            sessionDuration: Math.round(performance.now() - this.startTime),
            imageLoads: {
                count: imageLoads.length,
                avgDuration: imageLoads.length > 0
                    ? Math.round(imageLoads.reduce((sum, e) => sum + (e.duration || 0), 0) / imageLoads.length)
                    : 0,
                slowest: imageLoads.length > 0
                    ? Math.max(...imageLoads.map(e => e.duration || 0))
                    : 0
            },
            transitions: {
                count: transitions.length
            },
            events: this.events
        };
    }

    exportLogs() {
        // Export logs as JSON for analysis
        const logs = JSON.parse(localStorage.getItem('perf_log') || '[]');
        const dataStr = JSON.stringify(logs, null, 2);
        const dataBlob = new Blob([dataStr], { type: 'application/json' });
        const url = URL.createObjectURL(dataBlob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `perf_logs_${this.sessionId}.json`;
        link.click();
    }
}

// Global performance logger instance
const perfLogger = new PerformanceLogger();

// Expose to window for debugging
window.perfLogger = perfLogger;

/**
 * Smooth Image Carousel for seamless Ken Burns transitions
 */
class SimpleImageCarousel {
    constructor(images, options = {}) {
        this.images = images || [];
        this.currentIndex = 0;
        this.timer = null;
        this.isPlaying = false;
        this.isPaused = false;
        this.transitionInProgress = false;
        this.generation = 0; // Cancels zombie transitions on destroy

        this.imageDuration = options.imageDuration || 10000;
        this.transitionDuration = options.transitionDuration || 400; // fade duration ms
        this.kenBurnsEnabled = options.kenBurnsEnabled !== false;

        // Pause/resume timing
        this.pauseTime = null;
        this.remainingTime = null;

        // Callbacks
        this.onImageChange = options.onImageChange || (() => {});
        this.onComplete = options.onComplete || (() => {});

        // DOM references (looked up fresh each init)
        this.imagePanel = null;
        this.mobileImageSection = null;
        this.indicatorsEl = null;
        this.mobileIndicatorsEl = null;

        // Single image elements (created per init, removed on destroy)
        this.desktopImg = null;
        this.mobileImg = null;
        this.desktopStack = null;
        this.mobileStack = null;

        // Ken Burns
        this.kenBurnsAnimations = ['ken-burns-in', 'ken-burns-out', 'ken-burns-pan-left', 'ken-burns-pan-right'];

        // Reduced motion
        this.prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
        if (this.prefersReducedMotion) this.kenBurnsEnabled = false;

        // Touch state
        this.touchStartX = 0;
        this.touchStartY = 0;
        this.touchStartTime = 0;
        this.isTouchSwiping = false;
        this.minSwipeDistance = 50;
        this.maxSwipeTime = 300;

        // Keyboard debouncing
        this.lastKeyPress = 0;
        this.keyDebounceTime = 100;

        // Stored event listeners for cleanup
        this._listeners = [];
    }

    async init() {
        perfLogger.log('carousel_init_start', { imageCount: this.images.length });
        this.generation++;

        // Look up DOM each time — fresh references
        this.imagePanel = document.getElementById('image-panel');
        this.mobileImageSection = document.querySelector('.mobile-image-section');
        this.indicatorsEl = document.getElementById('carousel-indicators');
        this.mobileIndicatorsEl = document.getElementById('mobile-carousel-indicators');

        this.setupImageElements();

        if (this.images.length <= 1) {
            this.hideIndicators();
            if (this.images.length === 1) {
                await this.showInitialImage();
            }
            perfLogger.log('carousel_init_complete', { mode: 'single_image' });
            return;
        }

        this.createIndicators();
        this.showIndicators();
        this.updateIndicators();
        this.setupTouchHandlers();
        await this.showInitialImage();

        perfLogger.log('carousel_init_complete', { mode: 'multi_image' });
    }

    setupImageElements() {
        // Desktop: create stack + single img
        if (this.imagePanel) {
            const existingImg = this.imagePanel.querySelector('#main-image');
            const container = this.imagePanel.querySelector('.image-container');

            let stack = this.imagePanel.querySelector('.carousel-image-stack');
            if (!stack) {
                stack = document.createElement('div');
                stack.className = 'carousel-image-stack';
                if (container && existingImg) {
                    container.insertBefore(stack, existingImg);
                    existingImg.remove();
                } else if (container) {
                    container.appendChild(stack);
                } else {
                    this.imagePanel.appendChild(stack);
                }
            } else {
                stack.innerHTML = '';
            }

            const img = document.createElement('img');
            img.className = 'carousel-image';
            img.alt = 'Inspirational artwork';
            stack.appendChild(img);
            this.desktopImg = img;
            this.desktopStack = stack;
        }

        // Mobile: create stack + single img
        if (this.mobileImageSection) {
            const existingImg = this.mobileImageSection.querySelector('#mobile-image');

            let mobileStack = this.mobileImageSection.querySelector('.carousel-image-stack-mobile');
            if (!mobileStack) {
                mobileStack = document.createElement('div');
                mobileStack.className = 'carousel-image-stack carousel-image-stack-mobile';
                if (existingImg) {
                    existingImg.parentNode.insertBefore(mobileStack, existingImg);
                    existingImg.remove();
                } else {
                    this.mobileImageSection.appendChild(mobileStack);
                }
            } else {
                mobileStack.innerHTML = '';
            }

            const img = document.createElement('img');
            img.className = 'carousel-image';
            img.alt = 'Inspirational artwork';
            mobileStack.appendChild(img);
            this.mobileImg = img;
            this.mobileStack = mobileStack;
        }
    }

    async showInitialImage() {
        if (this.images.length === 0) return;

        const gen = this.generation;
        const firstImage = this.images[0];

        perfLogger.log('carousel_initial_image_start', { imageCount: this.images.length });

        await this.waitForImageLoad(firstImage.path);
        if (this.generation !== gen) return;

        perfLogger.log('carousel_initial_image_loaded', { path: firstImage.path });

        [this.desktopImg, this.mobileImg].forEach(img => {
            if (!img) return;
            img.src = firstImage.path;
            img.style.opacity = '1';
            this.applyKenBurns(img);
        });

        this.currentIndex = 0;
        this.updateIndicators();
        this.onImageChange(0, firstImage);

        // Preload next
        if (this.images.length > 1) this.preloadNextImages();

        perfLogger.log('carousel_initial_image_complete');
    }

    waitForImageLoad(imagePath) {
        return new Promise((resolve) => {
            const img = new Image();
            img.onload = () => resolve();
            img.onerror = () => {
                console.warn('Failed to load image:', imagePath);
                resolve();
            };
            img.src = imagePath;
            setTimeout(() => resolve(), 5000);
        });
    }

    createIndicators() {
        const createDots = (container) => {
            if (!container) return;
            container.innerHTML = '';
            this.images.forEach((_, index) => {
                const dot = document.createElement('button');
                dot.className = 'carousel-dot';
                dot.setAttribute('aria-label', `View variation ${index + 1}`);
                const handler = (e) => { e.stopPropagation(); this.goToIndex(index); };
                dot.addEventListener('click', handler);
                this._listeners.push({ el: dot, type: 'click', fn: handler });
                container.appendChild(dot);
            });
        };
        createDots(this.indicatorsEl);
        createDots(this.mobileIndicatorsEl);
    }

    updateIndicators() {
        const updateDots = (container) => {
            if (!container) return;
            const dots = container.querySelectorAll('.carousel-dot');
            dots.forEach((dot, index) => {
                dot.classList.toggle('active', index === this.currentIndex);
            });
        };
        updateDots(this.indicatorsEl);
        updateDots(this.mobileIndicatorsEl);
    }

    _addListener(el, type, fn, opts) {
        el.addEventListener(type, fn, opts);
        this._listeners.push({ el, type, fn, opts });
    }

    setupTouchHandlers() {
        const targets = [this.desktopStack, this.mobileStack].filter(Boolean);

        targets.forEach(element => {
            this._addListener(element, 'mouseenter', () => {
                if (this.isPlaying && !this.isPaused) this.pause();
            });
            this._addListener(element, 'mouseleave', () => {
                if (this.isPaused) this.resume();
            });

            this._addListener(element, 'touchstart', (e) => {
                const touch = e.touches[0];
                this.touchStartX = touch.clientX;
                this.touchStartY = touch.clientY;
                this.touchStartTime = Date.now();
                this.isTouchSwiping = false;
            }, { passive: true });

            this._addListener(element, 'touchmove', (e) => {
                if (e.touches.length !== 1) return;
                const touch = e.touches[0];
                const deltaX = Math.abs(touch.clientX - this.touchStartX);
                const deltaY = Math.abs(touch.clientY - this.touchStartY);
                if (deltaX > deltaY && deltaX > 10) {
                    this.isTouchSwiping = true;
                    e.preventDefault();
                }
            });

            this._addListener(element, 'touchend', (e) => {
                if (!this.isTouchSwiping || e.changedTouches.length !== 1) return;
                const touch = e.changedTouches[0];
                const deltaX = touch.clientX - this.touchStartX;
                const deltaY = Math.abs(touch.clientY - this.touchStartY);
                const deltaTime = Date.now() - this.touchStartTime;

                if (Math.abs(deltaX) >= this.minSwipeDistance &&
                    deltaTime <= this.maxSwipeTime &&
                    deltaY <= Math.abs(deltaX) / 2) {
                    e.preventDefault();
                    if (deltaX > 0) { this.previous(); } else { this.next(); }
                }
                this.isTouchSwiping = false;
            }, { passive: false });
        });
    }

    showIndicators() {
        if (this.indicatorsEl) this.indicatorsEl.classList.remove('hidden');
        if (this.mobileIndicatorsEl) this.mobileIndicatorsEl.classList.remove('hidden');
    }

    hideIndicators() {
        if (this.indicatorsEl) this.indicatorsEl.classList.add('hidden');
        if (this.mobileIndicatorsEl) this.mobileIndicatorsEl.classList.add('hidden');
    }

    async transitionToImage(index) {
        if (this.transitionInProgress || index === this.currentIndex) return;
        if (index < 0 || index >= this.images.length) return;

        this.transitionInProgress = true;
        const gen = this.generation;
        const nextImage = this.images[index];

        perfLogger.log('carousel_transition_start', {
            fromIndex: this.currentIndex, toIndex: index, imagePath: nextImage.path
        });

        // Preload image
        await this.waitForImageLoad(nextImage.path);
        if (this.generation !== gen) return;

        // Fade out
        [this.desktopImg, this.mobileImg].forEach(img => {
            if (img) img.style.opacity = '0';
        });

        await this.wait(this.transitionDuration);
        if (this.generation !== gen) return;

        // Swap src while invisible
        [this.desktopImg, this.mobileImg].forEach(img => {
            if (!img) return;
            const styleName = nextImage.style?.name || 'artistic';
            img.src = nextImage.path;
            img.alt = `Artwork in ${styleName} style`;
            this.applyKenBurns(img);
        });

        // One frame for src + animation to apply
        await new Promise(resolve => requestAnimationFrame(resolve));
        if (this.generation !== gen) return;

        // Fade in
        [this.desktopImg, this.mobileImg].forEach(img => {
            if (img) img.style.opacity = '1';
        });

        this.currentIndex = index;
        this.updateIndicators();
        this.onImageChange(index, nextImage);

        await this.wait(this.transitionDuration);
        if (this.generation !== gen) return;

        this.transitionInProgress = false;
        perfLogger.log('carousel_transition_complete', { index });

        this.preloadNextImages();
    }

    applyKenBurns(img) {
        if (!img || !this.kenBurnsEnabled) return;
        this.kenBurnsAnimations.forEach(a => img.classList.remove(a));
        requestAnimationFrame(() => {
            const cls = this.kenBurnsAnimations[Math.floor(Math.random() * this.kenBurnsAnimations.length)];
            img.classList.add(cls);
        });
    }

    preloadNextImages() {
        if (this.images.length <= 1) return;
        const next = (this.currentIndex + 1) % this.images.length;
        this.waitForImageLoad(this.images[next].path);
        if (this.images.length > 2) {
            const next2 = (this.currentIndex + 2) % this.images.length;
            this.waitForImageLoad(this.images[next2].path);
        }
    }

    wait(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    async next(isAutomatic = false) {
        if (!isAutomatic) {
            const now = Date.now();
            if (now - this.lastKeyPress < this.keyDebounceTime) return;
            this.lastKeyPress = now;
        }
        const nextIndex = (this.currentIndex + 1) % this.images.length;
        await this.transitionToImage(nextIndex);
    }

    async previous(isAutomatic = false) {
        if (!isAutomatic) {
            const now = Date.now();
            if (now - this.lastKeyPress < this.keyDebounceTime) return;
            this.lastKeyPress = now;
        }
        const prevIndex = (this.currentIndex - 1 + this.images.length) % this.images.length;
        await this.transitionToImage(prevIndex);
    }

    async goToIndex(index) {
        await this.transitionToImage(index);
    }

    start() {
        if (this.images.length <= 1) return;
        if (this.isPlaying) return;
        this.isPlaying = true;
        this.scheduleNextTransition();
    }

    scheduleNextTransition(duration = null) {
        if (!this.isPlaying || this.isPaused) return;

        const timerDuration = duration || this.imageDuration;
        this.timerStartTime = Date.now();
        this.timerDuration = timerDuration;

        const nextIndex = (this.currentIndex + 1) % this.images.length;
        if (nextIndex === 0) {
            this.timer = setTimeout(() => {
                this.timerStartTime = null;
                this.timerDuration = null;
                this.onComplete();
            }, timerDuration);
        } else {
            this.timer = setTimeout(() => {
                this.timerStartTime = null;
                this.timerDuration = null;
                this.next(true).then(() => this.scheduleNextTransition());
            }, timerDuration);
        }
    }

    pause() {
        this.isPaused = true;
        if (this.timer) {
            clearTimeout(this.timer);
            this.timer = null;
            if (this.timerStartTime && this.timerDuration) {
                const elapsed = Date.now() - this.timerStartTime;
                this.remainingTime = Math.max(0, this.timerDuration - elapsed);
            }
        }
        this.pauseTime = Date.now();
    }

    resume() {
        if (!this.isPaused) return;
        this.isPaused = false;
        if (this.isPlaying) {
            if (this.remainingTime !== null && this.remainingTime > 0) {
                const timeToUse = this.remainingTime;
                this.remainingTime = null;
                this.scheduleNextTransition(timeToUse);
            } else {
                this.scheduleNextTransition();
            }
        }
        this.pauseTime = null;
    }

    destroy() {
        this.generation++; // Cancel any in-flight transitions
        this.pause();
        this.isPlaying = false;

        // Hide indicators immediately to prevent stale dots showing
        this.hideIndicators();

        // Remove all stored event listeners
        this._listeners.forEach(({ el, type, fn, opts }) => {
            el.removeEventListener(type, fn, opts);
        });
        this._listeners = [];

        // Remove created image elements entirely
        if (this.desktopImg) { this.desktopImg.remove(); this.desktopImg = null; }
        if (this.mobileImg) { this.mobileImg.remove(); this.mobileImg = null; }

        this.desktopStack = null;
        this.mobileStack = null;
    }
}

class InspirationApp {
    constructor() {
        this.contentData = [];
        this.currentIndex = 0;
        this.isBreathingActive = true;
        this.breathingTimer = null;
        this.isTransitioning = false;
        this.carousel = null;
        
        // Configuration - will be loaded dynamically
        this.breathingInterval = 15000; // Default 15 seconds
        this.transitionDuration = 1500; // 1.5 seconds
        this.imageDuration = 5000; // 5 seconds per image
        this.quoteDuration = 15000; // 15 seconds per quote (3 images)
        
        // Initialize
        this.init();
    }
    
    async init() {
        try {
            perfLogger.log('app_init_start');

            await this.loadContent();
            perfLogger.log('app_content_loaded', { contentCount: this.contentData.length });

            this.setupEventListeners();
            perfLogger.log('app_listeners_setup');

            await this.displayCurrentContent();
            perfLogger.log('app_initial_content_displayed');

            this.startBreathing();
            this.hideLoading();

            perfLogger.log('app_init_complete');
        } catch (error) {
            console.error('Failed to initialize app:', error);
            perfLogger.log('app_init_error', { error: error.message });
            this.showError('Failed to load inspiration content');
        }
    }
    
    async loadContent() {
        perfLogger.log('content_fetch_start');
        const fetchStart = performance.now();

        const response = await fetch('content.json');
        if (!response.ok) {
            throw new Error('Failed to load content');
        }

        const fetchDuration = Math.round(performance.now() - fetchStart);
        perfLogger.log('content_fetch_response', { duration: fetchDuration });

        this.contentData = await response.json();

        if (!this.contentData || this.contentData.length === 0) {
            throw new Error('No content available');
        }

        perfLogger.log('content_fetch_complete', {
            duration: Math.round(performance.now() - fetchStart),
            count: this.contentData.length
        });
    }
    
    setupEventListeners() {
        // Keyboard controls
        document.addEventListener('keydown', (e) => {
            if (e.code === 'Space') {
                e.preventDefault();
                this.nextContent();
            } else if (e.code === 'ArrowLeft') {
                e.preventDefault();
                // Navigate to previous image in carousel
                if (this.carousel && this.carousel.images.length > 1) {
                    this.carousel.previous();
                }
            } else if (e.code === 'ArrowRight') {
                e.preventDefault();
                // Navigate to next image in carousel
                if (this.carousel && this.carousel.images.length > 1) {
                    this.carousel.next();
                }
            } else if (e.code === 'ArrowUp') {
                e.preventDefault();
                // Jump to first variation
                if (this.carousel && this.carousel.images.length > 1) {
                    this.carousel.goToIndex(0);
                }
            } else if (e.code === 'ArrowDown') {
                e.preventDefault();
                // Jump to last variation
                if (this.carousel && this.carousel.images.length > 1) {
                    this.carousel.goToIndex(this.carousel.images.length - 1);
                }
            }
        });
        
        // Click controls
        document.addEventListener('click', (e) => {
            // Don't trigger on footer buttons
            if (!e.target.closest('.footer-bar')) {
                this.nextContent();
            }
        });
        
        // New inspiration button
        const newInspirationBtn = document.getElementById('new-inspiration-btn');
        if (newInspirationBtn) {
            newInspirationBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                this.nextContent();
            });
        }
        
        // Window focus/blur for breathing control
        window.addEventListener('focus', () => {
            if (!this.isBreathingActive) {
                this.startBreathing();
            }
        });
        
        window.addEventListener('blur', () => {
            this.pauseBreathing();
        });
        
        // Generation details modal
        const contentInfo = document.getElementById('content-info');
        const modal = document.getElementById('generation-modal');
        const modalClose = document.getElementById('modal-close');
        const modalBody = document.getElementById('modal-body');
        
        if (contentInfo && modal) {
            contentInfo.addEventListener('click', (e) => {
                e.stopPropagation();
                const content = JSON.parse(contentInfo.dataset.content || '{}');
                // Get the current image index from the dataset (default to 0)
                const currentImageIndex = parseInt(contentInfo.dataset.currentImageIndex || '0', 10);

                if (content.images && content.images[currentImageIndex]) {
                    const image = content.images[currentImageIndex];
                    const generation = image.generation || {};
                    const style = image.style || {};
                    
                    // Format prompt (summarize if too long)
                    let promptDisplay = generation.prompt || 'Not available';
                    const promptLength = promptDisplay.length;
                    if (promptLength > 500) {
                        promptDisplay = promptDisplay.substring(0, 200) + '\n\n[...prompt continues...]\n\n' + promptDisplay.substring(promptLength - 150);
                    }
                    
                    const modalContent = `
                        <div class="generation-details">
                            <p><strong>Style:</strong> ${style.name || content.style_name || 'Unknown'} (${style.approach || 'artistic'})</p>
                            <p><strong>Model:</strong> ${generation.model || 'Unknown'}</p>
                            <p><strong>Generated:</strong> ${generation.timestamp ? new Date(generation.timestamp).toLocaleDateString() : 'Unknown'}</p>
                            <p><strong>Dimensions:</strong> ${generation.dimensions || '1024x1024'}</p>
                            <div class="prompt-section">
                                <p><strong>Prompt (${promptLength} chars):</strong></p>
                                <div class="prompt-text">${promptDisplay}</div>
                            </div>
                        </div>
                    `;
                    
                    modalBody.innerHTML = modalContent;
                    modal.classList.remove('hidden');
                    // Pause breathing and carousel while modal is open
                    this.pauseBreathing();
                    if (this.carousel) {
                        this.carousel.pause();
                    }
                }
            });
        }
        
        if (modalClose && modal) {
            modalClose.addEventListener('click', () => {
                modal.classList.add('hidden');
                // Resume breathing and carousel when modal is closed
                this.startBreathing();
                if (this.carousel) {
                    this.carousel.resume();
                    // Refresh style info to match current carousel state
                    this.refreshCurrentStyleInfo();
                }
            });
        }
        
        if (modal) {
            modal.addEventListener('click', (e) => {
                if (e.target === modal) {
                    modal.classList.add('hidden');
                    // Resume breathing and carousel when modal is closed by clicking background
                    this.startBreathing();
                    if (this.carousel) {
                        this.carousel.resume();
                        // Refresh style info to match current carousel state
                        this.refreshCurrentStyleInfo();
                    }
                }
            });
        }

        // Escape key closes modal
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && modal && !modal.classList.contains('hidden')) {
                modal.classList.add('hidden');
                // Resume breathing and carousel when modal is closed
                this.startBreathing();
                if (this.carousel) {
                    this.carousel.resume();
                    this.refreshCurrentStyleInfo();
                }
            }
        });
    }
    
    hideLoading() {
        const loading = document.getElementById('loading');
        const mainContent = document.getElementById('main-content');
        
        if (loading) loading.classList.add('hidden');
        if (mainContent) mainContent.classList.remove('hidden');
    }
    
    showError(message) {
        const loading = document.getElementById('loading');
        if (loading) {
            loading.innerHTML = `
                <div style="color: #e74c3c; text-align: center;">
                    <h2>Error</h2>
                    <p>${message}</p>
                    <button onclick="location.reload()" 
                            style="margin-top: 1rem; padding: 0.5rem 1rem; 
                                   background: #e74c3c; color: white; border: none; 
                                   border-radius: 4px; cursor: pointer;">
                        Retry
                    </button>
                </div>
            `;
        }
    }
    
    async displayCurrentContent() {
        if (this.isTransitioning) return;
        this.isTransitioning = true;

        const content = this.contentData[this.currentIndex];

        perfLogger.log('quote_transition_start', {
            index: this.currentIndex,
            title: content.title,
            imageCount: content.images?.length || 0
        });

        // Fade out current content
        perfLogger.log('quote_fade_out_start');
        await this.fadeOut();
        perfLogger.log('quote_fade_out_complete');

        // Update content
        this.updateTextContent(content);

        // Update image content and wait for carousel to initialize
        perfLogger.log('quote_image_update_start');
        await this.updateImageContent(content);
        perfLogger.log('quote_image_update_complete');

        this.updateFooterContent(content);

        // Analyze image and adapt colors
        perfLogger.log('quote_color_analysis_start');
        await this.adaptColors(content);
        perfLogger.log('quote_color_analysis_complete');

        // Fade in new content
        perfLogger.log('quote_fade_in_start');
        await this.fadeIn();
        perfLogger.log('quote_fade_in_complete');

        this.isTransitioning = false;

        perfLogger.log('quote_transition_complete', { index: this.currentIndex });
    }
    
    updateTextContent(content) {
        // Desktop elements
        const quoteText = document.getElementById('quote-text');
        const quoteAuthor = document.getElementById('quote-author');
        const quoteContext = document.getElementById('quote-context');
        
        // Mobile elements
        const mobileQuoteText = document.getElementById('mobile-quote-text');
        const mobileQuoteAuthor = document.getElementById('mobile-quote-author');
        const mobileQuoteContext = document.getElementById('mobile-quote-context');
        
        const text = content.quote_text || content.title;
        const author = content.author;
        const context = content.metadata?.why_i_like_it || '';
        
        // Check if content has HTML formatting
        const hasFormattedContent = content.formatted_content && content.formatted_content.html;
        
        if (hasFormattedContent) {
            // Use formatted HTML content
            const htmlContent = content.formatted_content.html;
            
            // Update desktop with HTML
            if (quoteText) {
                quoteText.innerHTML = htmlContent;
                quoteText.classList.add('formatted-content');
            }
            
            // Update mobile with HTML
            if (mobileQuoteText) {
                mobileQuoteText.innerHTML = htmlContent;
                mobileQuoteText.classList.add('formatted-content', 'mobile-quote-text');
            }
        } else {
            // Fall back to plain text with dynamic font sizing
            const fontSize = this.calculateFontSize(text);
            
            // Update desktop
            if (quoteText) {
                quoteText.textContent = text;
                quoteText.style.fontSize = fontSize.desktop;
                quoteText.classList.remove('formatted-content');
            }
            
            // Update mobile
            if (mobileQuoteText) {
                mobileQuoteText.textContent = text;
                mobileQuoteText.style.fontSize = fontSize.mobile;
                mobileQuoteText.classList.remove('formatted-content', 'mobile-quote-text');
            }
        }
        
        // Update author and context (always plain text)
        if (quoteAuthor) quoteAuthor.textContent = author;
        if (quoteContext) quoteContext.innerHTML = this._formatContext(context);
        if (mobileQuoteAuthor) mobileQuoteAuthor.textContent = author;
        if (mobileQuoteContext) mobileQuoteContext.innerHTML = this._formatContext(context);
    }
    
    _formatContext(text) {
        // Split into paragraphs and apply progressive sizing
        const paragraphs = text.split('\n\n');
        return paragraphs.map((p, index) => {
            const className = index === 0 ? 'context-primary' : 'context-secondary';
            return `<p class="${className}">${p}</p>`;
        }).join('');
    }
    
    calculateFontSize(text) {
        const length = text.length;
        
        // Define size tiers based on character count
        // Short quotes (< 50 chars): Large font
        // Medium quotes (50-150 chars): Medium font  
        // Long quotes (150-300 chars): Small font
        // Very long quotes (> 300 chars): Extra small font
        
        let desktopSize, mobileSize;
        
        if (length < 50) {
            // Short quotes - largest size
            desktopSize = '1.8rem';
            mobileSize = '1.4rem';
        } else if (length < 150) {
            // Medium quotes - default size
            desktopSize = '1.5rem';
            mobileSize = '1.2rem';
        } else if (length < 300) {
            // Long quotes - smaller size
            desktopSize = '1.2rem';
            mobileSize = '1rem';
        } else if (length < 500) {
            // Very long quotes - small size
            desktopSize = '1rem';
            mobileSize = '0.9rem';
        } else {
            // Extremely long quotes - extra small
            desktopSize = '0.9rem';
            mobileSize = '0.8rem';
        }
        
        return {
            desktop: desktopSize,
            mobile: mobileSize
        };
    }
    
    async updateImageContent(content) {
        const mainImage = document.getElementById('main-image');
        const mobileImage = document.getElementById('mobile-image');

        // Destroy existing carousel
        if (this.carousel) {
            this.carousel.destroy();
            this.carousel = null;
        }

        // Check if we have multiple images available for carousel
        if (content.images && content.images.length > 0) {
            // Initialize smooth carousel for better transitions
            this.carousel = new SimpleImageCarousel(content.images, {
                imageDuration: this.imageDuration,
                transitionDuration: 400,
                kenBurnsEnabled: true,
                onImageChange: (index, image) => {
                    // Update style info when image changes
                    this.updateStyleInfo(image, index);
                },
                onComplete: () => {
                    // When all images have been shown, move to next quote
                    this.nextContent();
                }
            });

            // Wait for carousel initialization (which waits for first image load)
            await this.carousel.init();

            // Start carousel if we have multiple images
            if (content.images.length > 1) {
                perfLogger.log('carousel_autoplay_start');
                this.carousel.start();
            }
        } else {
            // Fallback to single image without carousel
            let imagePath = this.getImagePath(content);

            try {
                perfLogger.log('single_image_load_start', { path: imagePath });
                const loadStart = performance.now();

                // Check if image exists
                const response = await fetch(imagePath);
                if (!response.ok) {
                    throw new Error('Image not found');
                }

                // Wait for image to actually load
                await this.waitForImageLoad(imagePath);
                const loadDuration = Math.round(performance.now() - loadStart);

                perfLogger.log('single_image_loaded', {
                    path: imagePath,
                    duration: loadDuration
                });

                // Update image sources
                if (mainImage) {
                    mainImage.src = imagePath;
                    mainImage.alt = `AI-generated artwork for "${content.title}" by ${content.author}`;
                }
                if (mobileImage) {
                    mobileImage.src = imagePath;
                    mobileImage.alt = `AI-generated artwork for "${content.title}" by ${content.author}`;
                }

            } catch (error) {
                console.warn('Image not found, using placeholder:', imagePath);
                perfLogger.log('single_image_load_error', { path: imagePath, error: error.message });

                // Use a placeholder or default image
                const placeholderSrc = this.createPlaceholder(content);
                if (mainImage) mainImage.src = placeholderSrc;
                if (mobileImage) mobileImage.src = placeholderSrc;
            }
        }
    }

    waitForImageLoad(imagePath) {
        return new Promise((resolve) => {
            const img = new Image();
            img.onload = () => resolve();
            img.onerror = () => {
                console.warn('Failed to load image:', imagePath);
                resolve(); // Resolve anyway to avoid blocking
            };
            img.src = imagePath;

            // Timeout after 5 seconds to avoid infinite waiting
            setTimeout(() => resolve(), 5000);
        });
    }
    
    updateFooterContent(content) {
        const sourceLink = document.getElementById('source-link');
        const contentInfo = document.getElementById('content-info');
        const modelBadge = document.getElementById('model-badge');
        
        if (sourceLink && content.metadata?.source) {
            sourceLink.href = content.metadata.source;
            sourceLink.style.display = 'inline';
        } else if (sourceLink) {
            sourceLink.style.display = 'none';
        }
        
        // Update style info
        if (contentInfo) {
            const style = content.style_name || 'unknown';
            // On mobile, show just the style name; on desktop, show "Style: name"
            const isMobile = window.innerWidth <= 768;
            contentInfo.textContent = isMobile ? style : `Style: ${style}`;

            // Store current content metadata for modal
            contentInfo.dataset.content = JSON.stringify(content);
        }
        
        // Update model badge if we have generation metadata
        if (modelBadge && content.images && content.images[0]) {
            const generation = content.images[0].generation;
            if (generation && generation.model_display) {
                modelBadge.textContent = generation.model_display;
            }
        }
    }
    
    getImagePath(content) {
        // Generate expected image path based on content file (matches backend naming)
        if (content.content_file && content.content_file.startsWith('content/inspiration/')) {
            const baseFilename = content.content_file.replace('content/inspiration/', '').replace('.md', '');
            return `images/${baseFilename}_v1.png`;
        } else {
            // Fallback for unexpected paths
            const filename = content.content_file ? content.content_file.split('/').pop().replace('.md', '') : 'unknown';
            return `images/${filename}_v1.png`;
        }
    }
    
    createPlaceholder(content) {
        // Create a simple SVG placeholder
        const colors = content.style_data?.color_palette || ['#3498db', '#e74c3c', '#2ecc71'];
        const color = colors[0] || '#3498db';
        
        const svg = `
            <svg width="400" height="400" xmlns="http://www.w3.org/2000/svg">
                <rect width="400" height="400" fill="${color}" opacity="0.1"/>
                <text x="200" y="180" text-anchor="middle" font-family="Georgia, serif" 
                      font-size="24" fill="${color}" opacity="0.6">
                    Inspiration
                </text>
                <text x="200" y="220" text-anchor="middle" font-family="Georgia, serif" 
                      font-size="16" fill="${color}" opacity="0.4">
                    Image generating...
                </text>
            </svg>
        `;
        return `data:image/svg+xml;base64,${btoa(svg)}`;
    }
    
    async adaptColors(content) {
        try {
            const analysisStart = performance.now();

            // Get the current image element from the carousel or fallback
            const mainImage = (this.carousel && this.carousel.desktopImg) || document.getElementById('main-image');
            if (!mainImage) return;

            // Analyze image brightness
            const brightness = await this.analyzeImageBrightness(mainImage);
            const analysisDuration = Math.round(performance.now() - analysisStart);

            perfLogger.log('color_analysis_complete', {
                brightness: brightness.toFixed(2),
                duration: analysisDuration
            });

            // Determine color scheme
            const colorScheme = this.getColorScheme(brightness, content);

            // Apply colors to CSS variables
            document.documentElement.style.setProperty('--text-color', colorScheme.textColor);
            document.documentElement.style.setProperty('--background-color', colorScheme.backgroundColor);
            document.documentElement.style.setProperty('--accent-color', colorScheme.accentColor);
            document.documentElement.style.setProperty('--overlay-color', colorScheme.overlayColor);

        } catch (error) {
            console.warn('Color adaptation failed, using defaults:', error);
            perfLogger.log('color_analysis_error', { error: error.message });
        }
    }
    
    analyzeImageBrightness(imgElement) {
        return new Promise((resolve) => {
            const canvas = document.createElement('canvas');
            const ctx = canvas.getContext('2d');
            
            canvas.width = imgElement.naturalWidth || 400;
            canvas.height = imgElement.naturalHeight || 400;
            
            try {
                ctx.drawImage(imgElement, 0, 0);
                const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
                const data = imageData.data;
                
                let totalBrightness = 0;
                for (let i = 0; i < data.length; i += 4) {
                    // Calculate luminance using standard formula
                    const brightness = (data[i] * 0.299 + data[i + 1] * 0.587 + data[i + 2] * 0.114) / 255;
                    totalBrightness += brightness;
                }
                
                const avgBrightness = totalBrightness / (data.length / 4);
                resolve(avgBrightness);
                
            } catch (error) {
                // CORS or other canvas error, use default
                resolve(0.5);
            }
        });
    }
    
    getColorScheme(brightness, content) {
        const isLight = brightness > 0.5;
        
        if (isLight) {
            return {
                textColor: '#2c3e50',
                backgroundColor: '#f8f9fa',
                accentColor: '#3498db',
                overlayColor: 'rgba(248, 249, 250, 0.7)'
            };
        } else {
            return {
                textColor: '#ecf0f1',
                backgroundColor: '#34495e',
                accentColor: '#e74c3c',
                overlayColor: 'rgba(52, 73, 94, 0.7)'
            };
        }
    }
    
    async fadeOut() {
        const elements = [
            document.getElementById('quote-panel'),
            document.getElementById('image-panel'),
            document.getElementById('mobile-quote-panel'),
            document.querySelector('.mobile-image-section')
        ].filter(el => el);
        
        elements.forEach(el => el.classList.add('fade-out'));
        
        return new Promise(resolve => {
            setTimeout(resolve, this.transitionDuration / 2);
        });
    }
    
    async fadeIn() {
        const elements = [
            document.getElementById('quote-panel'),
            document.getElementById('image-panel'),
            document.getElementById('mobile-quote-panel'),
            document.querySelector('.mobile-image-section')
        ].filter(el => el);
        
        elements.forEach(el => {
            el.classList.remove('fade-out');
            el.classList.add('fade-in');
        });
        
        return new Promise(resolve => {
            setTimeout(() => {
                elements.forEach(el => el.classList.remove('fade-in'));
                resolve();
            }, this.transitionDuration / 2);
        });
    }
    
    nextContent() {
        if (this.isTransitioning || this.contentData.length === 0) return;
        
        this.currentIndex = (this.currentIndex + 1) % this.contentData.length;
        this.displayCurrentContent();
        this.resetBreathing();
    }
    
    startBreathing() {
        this.isBreathingActive = true;
        // Use longer interval when carousel is active (3 images × 10 seconds each)
        const interval = this.carousel && this.carousel.images.length > 1 
            ? this.quoteDuration 
            : this.breathingInterval;
        
        this.breathingTimer = setInterval(() => {
            if (this.isBreathingActive && !this.carousel) {
                // Only auto-advance if carousel is not handling it
                this.nextContent();
            }
        }, interval);
    }
    
    updateStyleInfo(image, index = 0) {
        const styleInfo = document.getElementById('content-info');
        if (styleInfo && image && image.style) {
            const styleName = image.style.name || image.style;
            const isMobile = window.innerWidth <= 768;
            styleInfo.textContent = isMobile ? styleName : `Style: ${styleName}`;
            styleInfo.dataset.currentImageIndex = index.toString();
        }
    }

    refreshCurrentStyleInfo() {
        // Refresh style info to match current carousel state
        if (this.carousel && this.carousel.images && this.carousel.currentIndex >= 0) {
            const currentImage = this.carousel.images[this.carousel.currentIndex];
            if (currentImage) {
                this.updateStyleInfo(currentImage, this.carousel.currentIndex);
            }
        }
    }
    
    pauseBreathing() {
        this.isBreathingActive = false;
        if (this.breathingTimer) {
            clearInterval(this.breathingTimer);
            this.breathingTimer = null;
        }
    }
    
    resetBreathing() {
        this.pauseBreathing();
        this.startBreathing();
    }
}

// Initialize the app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    new InspirationApp();
});

// Handle service worker for offline support (future enhancement)
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        navigator.serviceWorker.register('/sw.js').catch(() => {
            // Service worker not available, that's fine
        });
    });
}
