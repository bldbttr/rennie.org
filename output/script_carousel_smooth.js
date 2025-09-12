/**
 * Smooth Carousel Transitions Implementation
 * Enhanced ImageCarousel with dual-layer cross-fade system
 */

class SmoothImageCarousel {
    constructor(images, options = {}) {
        this.images = images || [];
        this.currentIndex = 0;
        this.timer = null;
        this.isPlaying = false;
        this.isPaused = false;
        this.transitionInProgress = false;
        
        // Configuration from options or defaults
        this.imageDuration = options.imageDuration || 10000; // 10 seconds
        this.transitionDuration = options.transitionDuration || 1500; // 1.5 seconds
        this.crossFadeDuration = options.crossFadeDuration || 2000; // 2 seconds for smooth cross-fade
        this.kenBurnsEnabled = options.kenBurnsEnabled !== false; // Default enabled
        
        // Callback functions
        this.onImageChange = options.onImageChange || (() => {});
        this.onComplete = options.onComplete || (() => {});
        
        // DOM elements - we'll create/manage dual layers
        this.imagePanel = document.getElementById('image-panel');
        this.mobileImageSection = document.querySelector('.mobile-image-section');
        this.indicatorsEl = document.getElementById('carousel-indicators');
        this.mobileIndicatorsEl = document.getElementById('mobile-carousel-indicators');
        
        // Dual layer management
        this.activeLayerIndex = 0;
        this.desktopLayers = [];
        this.mobileLayers = [];
        
        // Ken Burns state
        this.kenBurnsAnimations = ['ken-burns-in', 'ken-burns-out', 'ken-burns-pan-left', 'ken-burns-pan-right'];
        
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
        
        // Keyboard navigation debouncing
        this.lastKeyPress = 0;
        this.keyDebounceTime = 100;
        
        this.init();
    }
    
    init() {
        this.setupDualLayers();
        
        if (this.images.length <= 1) {
            this.hideIndicators();
            // Still set up the first image
            if (this.images.length === 1) {
                this.showInitialImage();
            }
            return;
        }
        
        this.createIndicators();
        this.showIndicators();
        this.updateIndicators();
        this.setupTouchHandlers();
        this.showInitialImage();
    }
    
    setupDualLayers() {
        // Create dual-layer structure for desktop
        if (this.imagePanel) {
            const existingImg = this.imagePanel.querySelector('#main-image');
            
            // Create stack container if it doesn't exist
            let stack = this.imagePanel.querySelector('.carousel-image-stack');
            if (!stack) {
                stack = document.createElement('div');
                stack.className = 'carousel-image-stack';
                
                // Move existing image into stack as first layer
                if (existingImg) {
                    existingImg.parentNode.insertBefore(stack, existingImg);
                    existingImg.remove();
                } else {
                    const container = this.imagePanel.querySelector('.image-container');
                    if (container) {
                        container.appendChild(stack);
                    } else {
                        this.imagePanel.appendChild(stack);
                    }
                }
            }
            
            // Create two image layers for desktop
            for (let i = 0; i < 2; i++) {
                const layer = document.createElement('img');
                layer.className = `carousel-image-layer layer-${i}`;
                layer.alt = 'AI-generated inspiration artwork';
                stack.appendChild(layer);
                this.desktopLayers[i] = layer;
            }
        }
        
        // Create dual-layer structure for mobile
        if (this.mobileImageSection) {
            const existingImg = this.mobileImageSection.querySelector('#mobile-image');
            
            // Create stack container if it doesn't exist
            let mobileStack = this.mobileImageSection.querySelector('.carousel-image-stack-mobile');
            if (!mobileStack) {
                mobileStack = document.createElement('div');
                mobileStack.className = 'carousel-image-stack carousel-image-stack-mobile';
                
                // Move existing image into stack
                if (existingImg) {
                    existingImg.parentNode.insertBefore(mobileStack, existingImg);
                    existingImg.remove();
                } else {
                    this.mobileImageSection.appendChild(mobileStack);
                }
            }
            
            // Create two image layers for mobile
            for (let i = 0; i < 2; i++) {
                const layer = document.createElement('img');
                layer.className = `carousel-image-layer mobile-layer-${i}`;
                layer.alt = 'AI-generated inspiration artwork';
                mobileStack.appendChild(layer);
                this.mobileLayers[i] = layer;
            }
        }
    }
    
    showInitialImage() {
        if (this.images.length === 0) return;
        
        const firstImage = this.images[0];
        const activeDesktopLayer = this.desktopLayers[0];
        const activeMobileLayer = this.mobileLayers[0];
        
        if (activeDesktopLayer) {
            activeDesktopLayer.src = firstImage.path;
            activeDesktopLayer.classList.add('active');
            this.applyKenBurnsToLayer(activeDesktopLayer);
        }
        
        if (activeMobileLayer) {
            activeMobileLayer.src = firstImage.path;
            activeMobileLayer.classList.add('active');
            this.applyKenBurnsToLayer(activeMobileLayer);
        }
        
        // Preload next image
        if (this.images.length > 1) {
            this.preloadNextImages();
        }
        
        // Notify parent of initial image
        this.onImageChange(0, firstImage);
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
        // Set up touch events on both desktop and mobile stacks
        const stacks = [
            this.imagePanel?.querySelector('.carousel-image-stack'),
            this.mobileImageSection?.querySelector('.carousel-image-stack-mobile')
        ].filter(el => el);
        
        stacks.forEach(element => {
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
                
                // Check if it's a valid swipe
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
    
    async transitionToImage(index) {
        if (this.transitionInProgress || index === this.currentIndex) return;
        if (index < 0 || index >= this.images.length) return;
        
        this.transitionInProgress = true;
        
        const nextImage = this.images[index];
        const currentLayerIndex = this.activeLayerIndex;
        const nextLayerIndex = 1 - currentLayerIndex;
        
        const currentDesktopLayer = this.desktopLayers[currentLayerIndex];
        const nextDesktopLayer = this.desktopLayers[nextLayerIndex];
        const currentMobileLayer = this.mobileLayers[currentLayerIndex];
        const nextMobileLayer = this.mobileLayers[nextLayerIndex];
        
        // Preload the next image if not already loaded
        if (!this.preloadedImages.has(nextImage.path)) {
            await this.immediatePreloadImage(nextImage.path, true);
        }
        
        // Set up next layers with new image
        if (nextDesktopLayer) {
            nextDesktopLayer.src = nextImage.path;
            // Apply Ken Burns to next layer while it's still invisible
            this.applyKenBurnsToLayer(nextDesktopLayer);
        }
        
        if (nextMobileLayer) {
            nextMobileLayer.src = nextImage.path;
            this.applyKenBurnsToLayer(nextMobileLayer);
        }
        
        // Small delay to ensure image is loaded and Ken Burns is applied
        await this.waitForFrame();
        
        // Start cross-fade transition
        requestAnimationFrame(() => {
            // Fade out current layer
            if (currentDesktopLayer) currentDesktopLayer.classList.remove('active');
            if (currentMobileLayer) currentMobileLayer.classList.remove('active');
            
            // Fade in next layer
            if (nextDesktopLayer) nextDesktopLayer.classList.add('active');
            if (nextMobileLayer) nextMobileLayer.classList.add('active');
        });
        
        // Wait for cross-fade to complete
        await this.waitForTransition(this.crossFadeDuration);
        
        // Update state
        this.activeLayerIndex = nextLayerIndex;
        this.currentIndex = index;
        this.transitionInProgress = false;
        
        // Update indicators and notify callbacks
        this.updateIndicators();
        this.onImageChange(index, nextImage);
        
        // Preload next images for smooth navigation
        this.preloadNextImages();
    }
    
    applyKenBurnsToLayer(layer) {
        if (!layer || !this.kenBurnsEnabled) return;
        
        // Clear any existing Ken Burns animations
        this.kenBurnsAnimations.forEach(anim => {
            layer.classList.remove(anim);
        });
        
        // Apply new random Ken Burns after a frame
        requestAnimationFrame(() => {
            const animationIndex = Math.floor(Math.random() * this.kenBurnsAnimations.length);
            const animationClass = this.kenBurnsAnimations[animationIndex];
            layer.classList.add(animationClass);
        });
    }
    
    preloadNextImages() {
        if (this.images.length <= 1) return;
        
        // Preload the next 2 images for smoother navigation
        const nextIndex = (this.currentIndex + 1) % this.images.length;
        const nextNextIndex = (this.currentIndex + 2) % this.images.length;
        
        this.immediatePreloadImage(this.images[nextIndex].path, true); // High priority
        
        // Only preload the second next image if we have more than 2 images
        if (this.images.length > 2) {
            this.immediatePreloadImage(this.images[nextNextIndex].path, false); // Low priority
        }
    }
    
    immediatePreloadImage(imagePath, highPriority = false) {
        return new Promise((resolve) => {
            if (this.preloadedImages.has(imagePath)) {
                resolve();
                return;
            }
            
            const img = new Image();
            img.onload = () => {
                this.preloadedImages.set(imagePath, true);
                resolve();
            };
            img.onerror = () => {
                console.warn('Failed to preload image:', imagePath);
                this.preloadedImages.set(imagePath, false);
                resolve();
            };
            
            // Use fetchpriority if supported (modern browsers)
            if ('fetchPriority' in img && highPriority) {
                img.fetchPriority = 'high';
            }
            
            img.src = imagePath;
        });
    }
    
    waitForTransition(duration) {
        return new Promise(resolve => setTimeout(resolve, duration));
    }
    
    waitForFrame() {
        return new Promise(resolve => requestAnimationFrame(resolve));
    }
    
    // Public methods for navigation
    async next() {
        const now = Date.now();
        if (now - this.lastKeyPress < this.keyDebounceTime) return;
        this.lastKeyPress = now;
        
        const nextIndex = (this.currentIndex + 1) % this.images.length;
        await this.transitionToImage(nextIndex);
    }
    
    async previous() {
        const now = Date.now();
        if (now - this.lastKeyPress < this.keyDebounceTime) return;
        this.lastKeyPress = now;
        
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
    
    scheduleNextTransition() {
        if (!this.isPlaying || this.isPaused) return;
        
        this.timer = setTimeout(() => {
            this.next().then(() => {
                // Check if we've completed a full cycle
                if (this.currentIndex === 0) {
                    this.onComplete();
                } else {
                    this.scheduleNextTransition();
                }
            });
        }, this.imageDuration);
    }
    
    pause() {
        this.isPaused = true;
        if (this.timer) {
            clearTimeout(this.timer);
            this.timer = null;
        }
    }
    
    resume() {
        if (!this.isPaused) return;
        this.isPaused = false;
        if (this.isPlaying) {
            this.scheduleNextTransition();
        }
    }
    
    destroy() {
        this.pause();
        this.isPlaying = false;
        
        // Clear all Ken Burns animations
        [...this.desktopLayers, ...this.mobileLayers].forEach(layer => {
            if (layer) {
                this.kenBurnsAnimations.forEach(anim => {
                    layer.classList.remove(anim);
                });
            }
        });
        
        // Clear preloaded images
        this.preloadedImages.clear();
    }
}

// Export for use in main app
window.SmoothImageCarousel = SmoothImageCarousel;