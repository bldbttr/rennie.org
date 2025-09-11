class ImageCarousel {
    constructor(images, options = {}) {
        this.images = images || [];
        this.currentIndex = 0;
        this.timer = null;
        this.isPlaying = false;
        this.isPaused = false;
        
        // Configuration from options or defaults
        this.imageDuration = options.imageDuration || 10000; // 10 seconds
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