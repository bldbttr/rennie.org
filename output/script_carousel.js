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
        
        const nextIndex = (this.currentIndex + 1) % this.images.length;
        const nextImagePath = this.images[nextIndex].path;
        
        if (!this.preloadedImages.has(nextImagePath)) {
            const img = new Image();
            img.onload = () => {
                this.preloadedImages.set(nextImagePath, true);
            };
            img.onerror = () => {
                console.warn('Failed to preload image:', nextImagePath);
            };
            img.src = nextImagePath;
        }
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
        
        // Clear preloaded images
        this.preloadedImages.clear();
        
        // Reset image styles
        const elements = [this.mainImageEl, this.mobileImageEl].filter(el => el);
        elements.forEach(el => {
            if (el) {
                el.style.opacity = '';
                el.style.transition = '';
                el.classList.remove('carousel-image-transition');
            }
        });
    }
}

class InspirationApp {
    constructor() {
        this.contentData = [];
        this.currentIndex = 0;
        this.currentImageIndex = 0; // Track which image variation is currently displayed
        this.isBreathingActive = true;
        this.breathingTimer = null;
        this.isTransitioning = false;
        this.carousel = null;
        
        // Configuration - will be loaded dynamically
        this.breathingInterval = 30000; // 30 seconds (3 images × 10 seconds)
        this.transitionDuration = 1500; // 1.5 seconds
        this.imageDuration = 10000; // 10 seconds per image
        
        // Initialize
        this.init();
    }
    
    async init() {
        try {
            await this.loadContent();
            this.setupEventListeners();
            this.displayCurrentContent();
            this.startBreathing();
            this.hideLoading();
        } catch (error) {
            console.error('Failed to initialize app:', error);
            this.showError('Failed to load inspiration content');
        }
    }
    
    async loadContent() {
        const response = await fetch('content.json');
        if (!response.ok) {
            throw new Error('Failed to load content');
        }
        this.contentData = await response.json();
        
        if (!this.contentData || this.contentData.length === 0) {
            throw new Error('No content available');
        }
    }
    
    setupEventListeners() {
        // Enhanced keyboard controls with debouncing
        let keyboardDebounce = null;
        document.addEventListener('keydown', (e) => {
            // Clear previous debounce
            if (keyboardDebounce) {
                clearTimeout(keyboardDebounce);
            }
            
            // Debounce rapid key presses for smoother experience
            keyboardDebounce = setTimeout(() => {
                if (e.code === 'Space') {
                    e.preventDefault();
                    this.nextContent();
                } else if (e.code === 'ArrowLeft') {
                    e.preventDefault();
                    this.previousImage();
                } else if (e.code === 'ArrowRight') {
                    e.preventDefault();
                    this.nextImage();
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
            }, 100); // 100ms debounce
        });
        
        // Click controls
        document.addEventListener('click', (e) => {
            // Don't trigger on footer buttons or carousel dots
            if (!e.target.closest('.footer-bar') && !e.target.closest('.carousel-indicators')) {
                this.nextImage();
            }
        });
        
        // Window focus/blur for breathing control
        window.addEventListener('focus', () => {
            if (!this.isBreathingActive) {
                this.startBreathing();
            }
        });
        
        window.addEventListener('blur', () => {
            this.pauseBreathing();
        });
        
        // Generation details modal and tooltip
        const contentInfo = document.getElementById('content-info');
        const modal = document.getElementById('generation-modal');
        const modalClose = document.getElementById('modal-close');
        const modalBody = document.getElementById('modal-body');
        const tooltip = document.getElementById('generation-tooltip');
        const tooltipContent = document.querySelector('.tooltip-content');
        
        if (contentInfo && modal) {
            contentInfo.addEventListener('click', (e) => {
                e.stopPropagation();
                const content = JSON.parse(contentInfo.dataset.content || '{}');
                
                // Use the currently displayed image instead of always the first one (if not placeholder)
                if (this.currentImageIndex >= 0 && content.images && content.images[this.currentImageIndex]) {
                    const image = content.images[this.currentImageIndex];
                    const generation = image.generation || {};
                    const style = image.style || {};
                    
                    // Format prompt (summarize if too long)
                    let promptDisplay = generation.prompt || 'Not available';
                    const promptLength = promptDisplay.length;
                    if (promptLength > 300) {
                        promptDisplay = promptDisplay.substring(0, 150) + '...' + promptDisplay.substring(promptLength - 100);
                    }
                    
                    const modalContent = `
                        <div class="generation-details">
                            <p><strong>Style:</strong> ${style.name || content.style_name || 'Unknown'} (${style.approach || 'artistic'})</p>
                            <p><strong>Model:</strong> ${generation.model || 'Unknown'}</p>
                            <p><strong>Generated:</strong> ${generation.timestamp ? new Date(generation.timestamp).toLocaleDateString() : 'Unknown'}</p>
                            <p><strong>Dimensions:</strong> ${generation.dimensions || '1024x1024'}</p>
                            <p><strong>Image:</strong> ${image.filename || 'Unknown'} (variation ${this.currentImageIndex + 1} of ${content.images.length})</p>
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
        
        // Tooltip hover functionality
        if (contentInfo && tooltip && tooltipContent) {
            contentInfo.addEventListener('mouseenter', (e) => {
                const content = JSON.parse(contentInfo.dataset.content || '{}');
                
                // Use the currently displayed image (if not placeholder)
                if (this.currentImageIndex >= 0 && content.images && content.images[this.currentImageIndex]) {
                    const image = content.images[this.currentImageIndex];
                    const generation = image.generation || {};
                    const style = image.style || {};
                    
                    const tooltipHtml = `
                        <p><strong>Style:</strong> ${style.name || content.style_name || 'Unknown'}</p>
                        <p><strong>Model:</strong> ${generation.model_display || 'Unknown'}</p>
                        <p><strong>Image:</strong> variation ${this.currentImageIndex + 1} of ${content.images.length}</p>
                        <p><strong>Generated:</strong> ${generation.timestamp ? new Date(generation.timestamp).toLocaleDateString() : 'Unknown'}</p>
                    `;
                    
                    tooltipContent.innerHTML = tooltipHtml;
                    tooltip.classList.remove('hidden');
                }
            });
            
            contentInfo.addEventListener('mouseleave', () => {
                tooltip.classList.add('hidden');
            });
        }
        
        if (modalClose && modal) {
            modalClose.addEventListener('click', () => {
                modal.classList.add('hidden');
                
                // Resume breathing and carousel when modal is closed
                this.startBreathing();
                if (this.carousel) {
                    this.carousel.resume();
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
                    }
                }
            });
        }
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
        
        // Destroy existing carousel
        if (this.carousel) {
            this.carousel.destroy();
            this.carousel = null;
        }
        
        // Fade out current content
        await this.fadeOut();
        
        // Update content
        this.updateTextContent(content);
        await this.initializeCarousel(content);
        this.updateFooterContent(content);
        
        // Analyze image and adapt colors
        await this.adaptColors(content);
        
        // Fade in new content
        await this.fadeIn();
        
        this.isTransitioning = false;
    }
    
    async initializeCarousel(content) {
        // Check if we have multiple images available
        if (content.images && content.images.length > 0) {
            // Initialize carousel
            this.carousel = new ImageCarousel(content.images, {
                imageDuration: this.imageDuration,
                transitionDuration: this.transitionDuration,
                onImageChange: (index, image) => {
                    this.currentImageIndex = index;
                    this.updateFooterContent(content);
                    this.adaptColors(content);
                },
                onComplete: () => {
                    // Carousel completed full cycle, move to next content
                    this.nextContent();
                }
            });
            
            // Set first image and start carousel
            this.currentImageIndex = 0;
            await this.carousel.updateImage();
            
            // Start carousel if we have multiple images
            if (content.images.length > 1) {
                this.carousel.start();
            }
        } else {
            // Fallback to old method for single images
            this.currentImageIndex = 0;
            await this.updateImageContent(content);
        }
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
        
        // Calculate dynamic font size based on text length
        const fontSize = this.calculateFontSize(text);
        
        // Update desktop
        if (quoteText) {
            quoteText.textContent = text;
            quoteText.style.fontSize = fontSize.desktop;
        }
        if (quoteAuthor) quoteAuthor.textContent = author;
        if (quoteContext) quoteContext.textContent = context;
        
        // Update mobile
        if (mobileQuoteText) {
            mobileQuoteText.textContent = text;
            mobileQuoteText.style.fontSize = fontSize.mobile;
        }
        if (mobileQuoteAuthor) mobileQuoteAuthor.textContent = author;
        if (mobileQuoteContext) mobileQuoteContext.textContent = context;
    }
    
    calculateFontSize(text) {
        const length = text.length;
        
        let desktopSize, mobileSize;
        
        if (length < 50) {
            desktopSize = '1.8rem';
            mobileSize = '1.4rem';
        } else if (length < 150) {
            desktopSize = '1.5rem';
            mobileSize = '1.2rem';
        } else if (length < 300) {
            desktopSize = '1.2rem';
            mobileSize = '1rem';
        } else if (length < 500) {
            desktopSize = '1rem';
            mobileSize = '0.9rem';
        } else {
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
        
        let imagePath;
        
        // Check if we have multiple images available
        if (content.images && content.images.length > 0) {
            // Randomly select one of the available images
            this.currentImageIndex = Math.floor(Math.random() * content.images.length);
            imagePath = content.images[this.currentImageIndex].path;
        } else {
            // Fallback to old method
            this.currentImageIndex = 0;
            imagePath = this.getImagePath(content);
        }
        
        try {
            // Check if image exists
            const response = await fetch(imagePath);
            if (!response.ok) {
                throw new Error('Image not found');
            }
            
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
            // Use a placeholder or default image
            const placeholderSrc = this.createPlaceholder(content);
            if (mainImage) mainImage.src = placeholderSrc;
            if (mobileImage) mobileImage.src = placeholderSrc;
            
            // Reset currentImageIndex to indicate we're using a placeholder, not a specific variation
            this.currentImageIndex = -1;
        }
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
        
        // Update style info - use the currently displayed image's style
        if (contentInfo) {
            let styleName = content.style_name || 'unknown';
            
            // If we have image data with style info, use that instead (but not for placeholders)
            if (this.currentImageIndex >= 0 && content.images && content.images[this.currentImageIndex] && content.images[this.currentImageIndex].style) {
                styleName = content.images[this.currentImageIndex].style.name || styleName;
            } else if (this.currentImageIndex === -1) {
                // Using placeholder - show that this is not a specific style variation
                styleName = `${content.style_name || 'unknown'} (placeholder)`;
            }
            
            contentInfo.textContent = `Style: ${styleName}`;
            
            // Store current content metadata for modal
            contentInfo.dataset.content = JSON.stringify(content);
        }
        
        // Update model badge if we have generation metadata from current image
        if (modelBadge && this.currentImageIndex >= 0 && content.images && content.images[this.currentImageIndex]) {
            const generation = content.images[this.currentImageIndex].generation;
            if (generation && generation.model_display) {
                modelBadge.textContent = generation.model_display;
            }
        } else if (modelBadge && this.currentImageIndex === -1) {
            // For placeholders, show generic model info
            modelBadge.textContent = 'Placeholder';
        }
    }
    
    getImagePath(content) {
        // Generate expected image path based on content
        const author = content.author.toLowerCase().replace(/\s+/g, '_').replace(/[^a-z0-9_]/g, '');
        const title = content.title.toLowerCase().replace(/\s+/g, '_').replace(/[^a-z0-9_]/g, '');
        return `images/${author}_${title}.png`;
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
            // Get the current image element
            const mainImage = document.getElementById('main-image');
            if (!mainImage) return;
            
            // Analyze image brightness
            const brightness = await this.analyzeImageBrightness(mainImage);
            
            // Determine color scheme
            const colorScheme = this.getColorScheme(brightness, content);
            
            // Apply colors to CSS variables
            document.documentElement.style.setProperty('--text-color', colorScheme.textColor);
            document.documentElement.style.setProperty('--background-color', colorScheme.backgroundColor);
            document.documentElement.style.setProperty('--accent-color', colorScheme.accentColor);
            document.documentElement.style.setProperty('--overlay-color', colorScheme.overlayColor);
            
        } catch (error) {
            console.warn('Color adaptation failed, using defaults:', error);
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
        // Don't start the breathing timer - let the carousel handle the timing
        // The carousel will call nextContent() when it completes its cycle
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
    
    nextImage() {
        if (this.carousel && this.carousel.images.length > 1) {
            this.carousel.next();
        } else {
            // No carousel or single image, go to next content
            this.nextContent();
        }
    }
    
    previousImage() {
        if (this.carousel && this.carousel.images.length > 1) {
            this.carousel.previous();
        }
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