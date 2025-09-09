/**
 * Breathing Inspiration Experience
 * JavaScript for dynamic color adaptation, content rotation, and smooth transitions
 */

class InspirationApp {
    constructor() {
        this.contentData = [];
        this.currentIndex = 0;
        this.isBreathingActive = true;
        this.breathingTimer = null;
        this.isTransitioning = false;
        
        // Configuration
        this.breathingInterval = 15000; // 15 seconds
        this.transitionDuration = 1500; // 1.5 seconds
        
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
        // Keyboard controls
        document.addEventListener('keydown', (e) => {
            if (e.code === 'Space') {
                e.preventDefault();
                this.nextContent();
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
        
        // Fade out current content
        await this.fadeOut();
        
        // Update content
        this.updateTextContent(content);
        await this.updateImageContent(content);
        this.updateFooterContent(content);
        
        // Analyze image and adapt colors
        await this.adaptColors(content);
        
        // Fade in new content
        await this.fadeIn();
        
        this.isTransitioning = false;
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
        
        // Update desktop
        if (quoteText) quoteText.textContent = text;
        if (quoteAuthor) quoteAuthor.textContent = author;
        if (quoteContext) quoteContext.textContent = context;
        
        // Update mobile
        if (mobileQuoteText) mobileQuoteText.textContent = text;
        if (mobileQuoteAuthor) mobileQuoteAuthor.textContent = author;
        if (mobileQuoteContext) mobileQuoteContext.textContent = context;
    }
    
    async updateImageContent(content) {
        const mainImage = document.getElementById('main-image');
        const mobileImage = document.getElementById('mobile-image');
        
        let imagePath;
        
        // Check if we have multiple images available
        if (content.images && content.images.length > 0) {
            // Randomly select one of the available images
            const randomIndex = Math.floor(Math.random() * content.images.length);
            imagePath = content.images[randomIndex].path;
        } else {
            // Fallback to old method
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
        }
    }
    
    updateFooterContent(content) {
        const sourceLink = document.getElementById('source-link');
        const contentInfo = document.getElementById('content-info');
        
        if (sourceLink && content.metadata?.source) {
            sourceLink.href = content.metadata.source;
            sourceLink.style.display = 'inline';
        } else if (sourceLink) {
            sourceLink.style.display = 'none';
        }
        
        if (contentInfo) {
            const style = content.style_name || 'unknown';
            contentInfo.textContent = `Style: ${style}`;
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
        this.breathingTimer = setInterval(() => {
            if (this.isBreathingActive) {
                this.nextContent();
            }
        }, this.breathingInterval);
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
