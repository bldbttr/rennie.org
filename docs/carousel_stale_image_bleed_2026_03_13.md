# Carousel Stale Image Bleed-Through Bug

**Date**: March 13, 2026
**Status**: RESOLVED
**Commit**: 657b489

## Problem

Images from one content item's carousel were appearing during another content item's carousel. For example, Marc Andreessen's Arcane-style images would appear while viewing Paul Graham's quote, with the footer correctly showing Paul Graham's style label ("ghibli-composition") — creating a visible mismatch.

## Root Cause: DOM Layer Reuse Without Cleanup

The `SmoothImageCarousel` uses a dual-layer cross-fade system with two `<img>` elements (`layer-0` and `layer-1`) that alternate as active/inactive during transitions. These DOM elements are **reused across content items** via `setupDualLayers()`, which only creates layers if they don't already exist.

The `destroy()` method cleared Ken Burns animation classes and preloaded image cache, but **did not**:
- Remove the `active` CSS class from layers
- Clear the `src` attribute from layers
- Reset `activeLayerIndex`

### Failure Sequence

1. pmarca carousel plays: `layer-1` ends up with `pmarca-pmf_v2.png` (Arcane style)
2. Content transition fires, `destroy()` called — layers retain old state
3. Paul Graham carousel created, `setupDualLayers()` reuses existing layers
4. `showInitialImage()` sets `layer-0` to paul-graham_v1 — but `layer-1` still has pmarca's Arcane image
5. When carousel transitions to paul-graham image 2 using `layer-1`, the old Arcane image can flash during cross-fade before the new src loads

## Fix

Updated `destroy()` in `SmoothImageCarousel` to fully reset layer state:

```javascript
destroy() {
    this.pause();
    this.isPlaying = false;

    [...this.desktopLayers, ...this.mobileLayers].forEach(layer => {
        if (layer) {
            this.kenBurnsAnimations.forEach(anim => {
                layer.classList.remove(anim);
            });
            // Clear image source and active state to prevent
            // stale images from previous content bleeding through
            layer.classList.remove('active');
            layer.removeAttribute('src');
        }
    });

    // Reset layer index so next carousel starts clean
    this.activeLayerIndex = 0;

    this.preloadedImages.clear();
}
```

**File modified**: `/scripts/templates/app.js`

## History of Carousel Style/Image Mismatch Bugs

This is the **fourth** round of carousel synchronization issues on this project:

| Date | Issue | Root Cause | Doc |
|------|-------|------------|-----|
| Sept 10, 2025 | Random style assignment instability | `random.choice()` without persistence | `random-style-stability-issue.md` |
| Sept 12, 2025 | Dots one step behind images | Event bubbling to global click handler | `carousel_dot_advancement_bug_status.md` |
| Sept 12, 2025 | Style info updates 2s late | `onImageChange` called after cross-fade instead of at start | `smooth_carousel_transitions_implementation_timing_issues.md` |
| Sept 26, 2025 | Style labels wrong on production | Browser caching old images (30-day TTL) | `image_style_deployment_mismatch_2025_09_26.md` |
| Sept 26, 2025 | Modal shows wrong style after resume | `resume()` didn't refresh UI state | `carousel_fixes_session_2025_09_26.md` |
| **Mar 13, 2026** | **Wrong content's images shown** | **DOM layers reused without clearing src/active** | **This document** |

## Pattern Analysis

The recurring theme is **shared mutable state** in the carousel:
- DOM elements reused across content items without full reset
- Global event handlers conflicting with component handlers
- Timing assumptions in async transitions
- Cache/stale state at multiple levels (browser, DOM, JS objects)

See architectural review for recommendations on reducing brittleness.
