#!/usr/bin/env python3
"""
Site Builder for rennie.org Inspiration Platform

Generates a static single-page application that displays inspiring quotes
with AI-generated artwork in a breathing, meditative interface.

Features:
- Responsive design (desktop: 25% quote + 75% image, mobile: stacked)
- Dynamic color adaptation based on image brightness
- Breathing animation with 10-20 second auto-advance
- Manual controls (click/spacebar)
- Smooth fade transitions
- Image background treatment for square images
"""

import json
import os
import shutil
import base64
from pathlib import Path
from typing import Dict, List, Any
from PIL import Image
import numpy as np


def load_parsed_content() -> List[Dict[str, Any]]:
    """Load parsed content data from generated/parsed_content.json"""
    content_file = Path("generated/parsed_content.json")
    
    if not content_file.exists():
        raise FileNotFoundError(f"Parsed content not found at {content_file}")
    
    with open(content_file, 'r') as f:
        content = json.load(f)
    
    # Convert single content item to list format
    if isinstance(content, dict):
        return [content]
    return content


def get_image_path(content_item: Dict[str, Any]) -> str:
    """Generate expected image filename from content metadata"""
    title = content_item.get('title', 'untitled')
    author = content_item.get('author', 'unknown')
    
    # Create filename using same logic as image generator
    filename = f"{author.lower().replace(' ', '_')}_{title.lower().replace(' ', '_').replace('?', '').replace('!', '').replace(',', '').replace('.', '')}.png"
    
    return f"generated/images/{filename}"


def analyze_image_brightness(image_path: str) -> Dict[str, Any]:
    """Analyze image brightness to determine optimal text panel colors"""
    try:
        image = Image.open(image_path)
        image = image.convert('RGB')
        
        # Convert to numpy array and calculate average brightness
        img_array = np.array(image)
        
        # Calculate weighted brightness (luminance formula)
        brightness = np.mean(img_array[:,:,0] * 0.299 + 
                           img_array[:,:,1] * 0.587 + 
                           img_array[:,:,2] * 0.114)
        
        # Normalize to 0-1 range
        brightness_normalized = brightness / 255.0
        
        # Determine if image is predominantly light or dark
        is_light = brightness_normalized > 0.5
        
        return {
            "brightness": round(brightness_normalized, 3),
            "is_light": is_light,
            "text_color": "#2c3e50" if is_light else "#ecf0f1",
            "background_color": "#f8f9fa" if is_light else "#34495e",
            "accent_color": "#3498db" if is_light else "#e74c3c"
        }
        
    except Exception as e:
        print(f"Warning: Could not analyze image brightness for {image_path}: {e}")
        # Default to dark theme
        return {
            "brightness": 0.5,
            "is_light": False,
            "text_color": "#ecf0f1",
            "background_color": "#34495e", 
            "accent_color": "#e74c3c"
        }


def create_html_template() -> str:
    """Generate the main HTML template"""
    return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Inspiration | rennie.org</title>
    <meta name="description" content="A breathing collection of inspiring quotes with AI-generated artwork">
    
    <!-- Preload critical CSS -->
    <link rel="preload" href="style.css" as="style">
    <link rel="stylesheet" href="style.css">
    
    <!-- Favicon -->
    <link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>✨</text></svg>">
</head>
<body>
    <div id="app" class="app">
        <!-- Loading State -->
        <div id="loading" class="loading">
            <div class="loading-spinner"></div>
            <p>Loading inspiration...</p>
        </div>
        
        <!-- Main Content -->
        <div id="main-content" class="main-content hidden">
            <!-- Desktop Layout -->
            <div class="desktop-layout">
                <!-- Quote Panel (25% left) -->
                <div class="quote-panel" id="quote-panel">
                    <div class="quote-content">
                        <blockquote id="quote-text" class="quote-text">
                            <!-- Quote content loaded here -->
                        </blockquote>
                        <cite id="quote-author" class="quote-author">
                            <!-- Author loaded here -->
                        </cite>
                        <div id="quote-context" class="quote-context">
                            <!-- Personal context loaded here -->
                        </div>
                    </div>
                </div>
                
                <!-- Image Panel (75% right) -->
                <div class="image-panel" id="image-panel">
                    <div class="image-container">
                        <img id="main-image" class="main-image" alt="AI-generated inspiration artwork" />
                        <div class="image-overlay"></div>
                    </div>
                </div>
            </div>
            
            <!-- Mobile Layout -->
            <div class="mobile-layout">
                <div class="mobile-image-section">
                    <img id="mobile-image" class="mobile-image" alt="AI-generated inspiration artwork" />
                </div>
                <div class="mobile-quote-section" id="mobile-quote-panel">
                    <div class="mobile-quote-content">
                        <blockquote id="mobile-quote-text" class="mobile-quote-text">
                            <!-- Quote content loaded here -->
                        </blockquote>
                        <cite id="mobile-quote-author" class="mobile-quote-author">
                            <!-- Author loaded here -->
                        </cite>
                        <div id="mobile-quote-context" class="mobile-quote-context">
                            <!-- Personal context loaded here -->
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Footer Bar -->
        <div id="footer-bar" class="footer-bar">
            <div class="footer-content">
                <div class="footer-left">
                    <a id="source-link" href="#" target="_blank" class="source-link">Source</a>
                    <span class="separator">•</span>
                    <button id="new-inspiration-btn" class="new-inspiration-btn">New Inspiration</button>
                </div>
                <div class="footer-right">
                    <span id="breathing-indicator" class="breathing-indicator">●</span>
                    <span id="content-info" class="content-info">Style: essence-of-desire</span>
                </div>
            </div>
        </div>
        
        <!-- Controls Hint -->
        <div id="controls-hint" class="controls-hint">
            Press <kbd>Space</kbd> or click for new inspiration
        </div>
    </div>
    
    <!-- JavaScript -->
    <script src="script.js"></script>
</body>
</html>"""


def create_css_styles() -> str:
    """Generate the CSS stylesheet with animations and responsive design"""
    return """/* Reset and Base Styles */
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

:root {
    /* Color Variables - Updated dynamically by JavaScript */
    --text-color: #ecf0f1;
    --background-color: #34495e;
    --accent-color: #e74c3c;
    --overlay-color: rgba(52, 73, 94, 0.7);
    
    /* Animation Variables */
    --breathing-duration: 15s;
    --transition-duration: 1.5s;
    
    /* Layout Variables */
    --quote-panel-width: 25%;
    --image-panel-width: 75%;
}

body {
    font-family: 'Georgia', serif;
    background: var(--background-color);
    color: var(--text-color);
    overflow: hidden;
    height: 100vh;
    transition: background-color var(--transition-duration) ease;
}

/* App Container */
.app {
    width: 100vw;
    height: 100vh;
    position: relative;
}

/* Loading State */
.loading {
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    height: 100vh;
    background: var(--background-color);
}

.loading-spinner {
    width: 40px;
    height: 40px;
    border: 3px solid var(--background-color);
    border-top: 3px solid var(--accent-color);
    border-radius: 50%;
    animation: spin 1s linear infinite;
    margin-bottom: 1rem;
}

@keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}

.hidden {
    display: none !important;
}

/* Desktop Layout */
.desktop-layout {
    display: flex;
    height: 100vh;
}

/* Quote Panel (25% left) */
.quote-panel {
    width: var(--quote-panel-width);
    background: var(--background-color);
    padding: 3rem 2rem;
    display: flex;
    align-items: center;
    transition: background-color var(--transition-duration) ease,
                color var(--transition-duration) ease;
    position: relative;
    overflow-y: auto;
}

.quote-content {
    max-width: 100%;
    animation: breathe var(--breathing-duration) ease-in-out infinite;
}

.quote-text {
    font-size: 1.8rem;
    line-height: 1.4;
    margin-bottom: 1.5rem;
    font-style: italic;
    color: var(--text-color);
    transition: color var(--transition-duration) ease;
}

.quote-author {
    font-size: 1.1rem;
    font-weight: bold;
    color: var(--accent-color);
    display: block;
    margin-bottom: 1rem;
    transition: color var(--transition-duration) ease;
}

.quote-author::before {
    content: "— ";
}

.quote-context {
    font-size: 0.95rem;
    line-height: 1.5;
    opacity: 0.8;
    font-style: normal;
    color: var(--text-color);
    transition: color var(--transition-duration) ease;
}

/* Image Panel (75% right) */
.image-panel {
    width: var(--image-panel-width);
    position: relative;
    overflow: hidden;
}

.image-container {
    width: 100%;
    height: 100vh;
    position: relative;
}

.main-image {
    width: 100%;
    height: 100%;
    object-fit: cover;
    object-position: center;
    transition: opacity var(--transition-duration) ease,
                transform var(--breathing-duration) ease-in-out;
    animation: breathe-image var(--breathing-duration) ease-in-out infinite;
}

.image-overlay {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: linear-gradient(135deg, 
                var(--overlay-color) 0%,
                transparent 30%,
                transparent 70%,
                var(--overlay-color) 100%);
    opacity: 0.1;
    transition: opacity var(--transition-duration) ease;
}

/* Mobile Layout */
.mobile-layout {
    display: none;
    flex-direction: column;
    height: 100vh;
}

.mobile-image-section {
    flex: 1;
    position: relative;
    overflow: hidden;
}

.mobile-image {
    width: 100%;
    height: 100%;
    object-fit: cover;
    object-position: center;
    animation: breathe-image var(--breathing-duration) ease-in-out infinite;
}

.mobile-quote-section {
    background: var(--background-color);
    padding: 2rem 1.5rem;
    transition: background-color var(--transition-duration) ease;
}

.mobile-quote-content {
    animation: breathe var(--breathing-duration) ease-in-out infinite;
}

.mobile-quote-text {
    font-size: 1.4rem;
    line-height: 1.4;
    margin-bottom: 1rem;
    font-style: italic;
    color: var(--text-color);
}

.mobile-quote-author {
    font-size: 1rem;
    font-weight: bold;
    color: var(--accent-color);
    display: block;
    margin-bottom: 0.8rem;
}

.mobile-quote-author::before {
    content: "— ";
}

.mobile-quote-context {
    font-size: 0.85rem;
    line-height: 1.4;
    opacity: 0.8;
    color: var(--text-color);
}

/* Footer Bar */
.footer-bar {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    background: rgba(0, 0, 0, 0.8);
    backdrop-filter: blur(10px);
    padding: 0.8rem 1.5rem;
    z-index: 1000;
    transition: transform 0.3s ease;
}

.footer-content {
    display: flex;
    justify-content: space-between;
    align-items: center;
    max-width: 100%;
    color: #ffffff;
}

.footer-left {
    display: flex;
    align-items: center;
    gap: 0.8rem;
}

.source-link {
    color: #ffffff;
    text-decoration: none;
    font-size: 0.9rem;
    opacity: 0.8;
    transition: opacity 0.2s ease;
}

.source-link:hover {
    opacity: 1;
}

.separator {
    opacity: 0.5;
}

.new-inspiration-btn {
    background: none;
    border: 1px solid rgba(255, 255, 255, 0.3);
    color: #ffffff;
    padding: 0.4rem 0.8rem;
    border-radius: 4px;
    font-size: 0.85rem;
    cursor: pointer;
    transition: all 0.2s ease;
}

.new-inspiration-btn:hover {
    background: rgba(255, 255, 255, 0.1);
    border-color: rgba(255, 255, 255, 0.5);
}

.footer-right {
    display: flex;
    align-items: center;
    gap: 0.8rem;
    font-size: 0.85rem;
    opacity: 0.7;
}

.breathing-indicator {
    animation: pulse 2s ease-in-out infinite;
    color: var(--accent-color);
}

/* Controls Hint */
.controls-hint {
    position: fixed;
    top: 1.5rem;
    right: 1.5rem;
    background: rgba(0, 0, 0, 0.7);
    color: #ffffff;
    padding: 0.8rem 1.2rem;
    border-radius: 8px;
    font-size: 0.85rem;
    opacity: 0.8;
    transition: opacity 0.3s ease;
    z-index: 1000;
    backdrop-filter: blur(5px);
}

.controls-hint kbd {
    background: rgba(255, 255, 255, 0.2);
    padding: 0.2rem 0.4rem;
    border-radius: 3px;
    font-family: monospace;
    font-size: 0.8rem;
}

/* Breathing Animations */
@keyframes breathe {
    0%, 100% { opacity: 1; transform: scale(1); }
    50% { opacity: 0.85; transform: scale(1.02); }
}

@keyframes breathe-image {
    0%, 100% { transform: scale(1); }
    50% { transform: scale(1.05); }
}

@keyframes pulse {
    0%, 100% { opacity: 0.7; transform: scale(1); }
    50% { opacity: 1; transform: scale(1.1); }
}

/* Fade Transitions */
.fade-out {
    opacity: 0 !important;
    transform: translateY(10px) !important;
}

.fade-in {
    opacity: 1 !important;
    transform: translateY(0) !important;
}

/* Responsive Design */
@media (max-width: 768px) {
    .desktop-layout {
        display: none;
    }
    
    .mobile-layout {
        display: flex;
    }
    
    .controls-hint {
        top: 1rem;
        right: 1rem;
        font-size: 0.8rem;
        padding: 0.6rem 1rem;
    }
    
    .footer-bar {
        padding: 0.6rem 1rem;
    }
    
    .footer-content {
        font-size: 0.8rem;
    }
    
    .footer-left {
        gap: 0.6rem;
    }
}

@media (max-width: 480px) {
    .mobile-quote-section {
        padding: 1.5rem 1rem;
    }
    
    .mobile-quote-text {
        font-size: 1.2rem;
    }
    
    .controls-hint {
        display: none; /* Hide on very small screens */
    }
}

/* Print Styles */
@media print {
    .footer-bar,
    .controls-hint {
        display: none;
    }
    
    .image-panel,
    .mobile-image-section {
        display: none;
    }
    
    .quote-panel {
        width: 100% !important;
        background: white !important;
        color: black !important;
    }
}
"""


def create_javascript() -> str:
    """Generate the JavaScript for dynamic functionality"""
    return """/**
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
        
        const imagePath = this.getImagePath(content);
        
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
        const author = content.author.toLowerCase().replace(/\\s+/g, '_').replace(/[^a-z0-9_]/g, '');
        const title = content.title.toLowerCase().replace(/\\s+/g, '_').replace(/[^a-z0-9_]/g, '');
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
"""


def build_site():
    """Main build function that generates the complete static site"""
    print("🏗️  Building rennie.org inspiration site...")
    
    # Create output directory
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    
    # Load parsed content
    try:
        content_items = load_parsed_content()
        print(f"✅ Loaded {len(content_items)} content items")
    except FileNotFoundError as e:
        print(f"❌ Error: {e}")
        print("   Run scripts/content_parser.py first to generate parsed content")
        return False
    
    # Process content and analyze images
    processed_content = []
    images_dir = output_dir / "images"
    images_dir.mkdir(exist_ok=True)
    
    for content in content_items:
        print(f"📝 Processing: {content['title']} by {content['author']}")
        
        # Get image path and analyze brightness
        image_path = get_image_path(content)
        if Path(image_path).exists():
            # Copy image to output directory
            image_filename = Path(image_path).name
            output_image_path = images_dir / image_filename
            shutil.copy2(image_path, output_image_path)
            
            # Analyze image brightness
            brightness_data = analyze_image_brightness(str(image_path))
            content['brightness_analysis'] = brightness_data
            
            print(f"   🖼️  Image: {image_filename} (brightness: {brightness_data['brightness']})")
        else:
            print(f"   ⚠️  Image not found: {image_path}")
            content['brightness_analysis'] = {
                "brightness": 0.5,
                "is_light": False,
                "text_color": "#ecf0f1",
                "background_color": "#34495e",
                "accent_color": "#e74c3c"
            }
        
        processed_content.append(content)
    
    # Generate HTML file
    html_content = create_html_template()
    (output_dir / "index.html").write_text(html_content, encoding='utf-8')
    print("✅ Generated index.html")
    
    # Generate CSS file
    css_content = create_css_styles()
    (output_dir / "style.css").write_text(css_content, encoding='utf-8')
    print("✅ Generated style.css")
    
    # Generate JavaScript file
    js_content = create_javascript()
    (output_dir / "script.js").write_text(js_content, encoding='utf-8')
    print("✅ Generated script.js")
    
    # Generate content JSON API (convert numpy types to native Python types)
    def convert_numpy_types(obj):
        if hasattr(obj, 'item'):  # numpy scalar
            return obj.item()
        elif isinstance(obj, dict):
            return {k: convert_numpy_types(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [convert_numpy_types(item) for item in obj]
        return obj
    
    serializable_content = convert_numpy_types(processed_content)
    content_json = json.dumps(serializable_content, indent=2, ensure_ascii=False)
    (output_dir / "content.json").write_text(content_json, encoding='utf-8')
    print("✅ Generated content.json API")
    
    # Generate metadata summary
    build_summary = {
        "build_timestamp": "2025-09-08T00:00:00Z",
        "content_count": len(processed_content),
        "images_included": sum(1 for c in processed_content if Path(get_image_path(c)).exists()),
        "total_size_mb": round(sum(f.stat().st_size for f in Path(output_dir).rglob("*") if f.is_file()) / (1024*1024), 2),
        "content_items": [
            {
                "title": c['title'],
                "author": c['author'],
                "style": c.get('style_name', 'unknown'),
                "has_image": Path(get_image_path(c)).exists(),
                "brightness": c['brightness_analysis']['brightness']
            }
            for c in processed_content
        ]
    }
    
    (output_dir / "build_summary.json").write_text(
        json.dumps(build_summary, indent=2, ensure_ascii=False), 
        encoding='utf-8'
    )
    
    print(f"\n🎉 Site build complete!")
    print(f"   📊 Content items: {build_summary['content_count']}")
    print(f"   🖼️  Images: {build_summary['images_included']}")
    print(f"   💾 Total size: {build_summary['total_size_mb']} MB")
    print(f"   📁 Output directory: {output_dir.absolute()}")
    print(f"\n🌐 Open {output_dir.absolute()}/index.html in your browser to preview")
    
    return True


if __name__ == "__main__":
    import sys
    
    # Change to project root directory
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)
    
    success = build_site()
    sys.exit(0 if success else 1)