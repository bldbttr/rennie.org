# Carousel Simplification Plan

**Date**: March 13, 2026
**Status**: COMPLETE — Implemented and deployed March 13, 2026
**Goal**: Replace 623-line dual-layer carousel with ~250-line single-element carousel
**Commits**: `4ffbcdc` (main simplification), `bd70eae` (review fixes)

## Context

Read these docs for full background:
- `docs/carousel_stale_image_bleed_2026_03_13.md` — Latest bug + history table of all 6 carousel bugs
- `docs/carousel_fixes_session_2025_09_26.md` — Previous fixes and state management notes

## Problem Summary

The `SmoothImageCarousel` class in `scripts/templates/app.js` (lines 240-856) uses a dual-layer cross-fade system (two `<img>` elements alternating active/inactive) to create seamless image transitions. This architecture has produced 6 synchronization bugs in 6 months because:

1. DOM layers are reused across content items without full cleanup
2. `activeLayerIndex` and `currentIndex` update at different times during transitions
3. Event listeners accumulate because they're never removed on destroy
4. Zombie transitions can write to destroyed carousel instances

Three independent architecture reviews all recommended the same thing: replace the dual-layer system with a single-element fade.

## Decision

**Level 2 simplification**: Single `<img>` element with CSS opacity transition. Keep carousel dots, Ken Burns, auto-advance, touch gestures, and pause/resume. Drop the dual-layer cross-fade (the source of all bugs).

**Visual difference**: Instead of two images seamlessly blending, there will be a brief (~0.5s) fade through the dark background between images. On the dark-themed site this is barely noticeable, and the Ken Burns zoom effect remains the dominant visual.

## Implementation Plan

### Step 1: Write the new SimpleImageCarousel class

**File**: `scripts/templates/app.js`
**Action**: Replace the `SmoothImageCarousel` class (lines 240-856) with a new class that:

**Same public API** (InspirationApp integration stays unchanged):
- Constructor: `new SimpleImageCarousel(images, options)` — same options object
- Methods: `init()`, `start()`, `pause()`, `resume()`, `destroy()`, `next()`, `previous()`, `goToIndex(index)`
- Properties: `images`, `currentIndex`, `isPlaying`, `isPaused`
- Callbacks: `onImageChange(index, image)`, `onComplete()`

**Key architectural changes**:
- ONE `<img>` element per viewport (desktop + mobile), not two
- `destroy()` removes DOM elements entirely (no reuse across content items)
- Fresh DOM created on each `init()` — eliminates all stale state bugs
- Generation counter pattern for cancelling zombie transitions
- Event listeners stored for proper cleanup on destroy
- No `activeLayerIndex` — no shadow state to diverge

**Transition approach**:
- Fade out current image (CSS `opacity: 0` transition, ~0.4s)
- Swap `src` while invisible
- Wait for new image to load
- Fade in (CSS `opacity: 1` transition, ~0.4s)
- Total transition: ~1s vs current 2s cross-fade

**Ken Burns**: Same 4 CSS animation classes, randomly applied per image. Clear and reapply on each transition. No changes to CSS keyframes needed.

**Dots**: Same creation/update logic, but click handlers stored for cleanup.

**Touch/hover**: Same swipe detection logic, but handlers stored and removed on destroy.

**Pause/resume**: Same remaining-time tracking, simplified without dual-layer concerns.

### Step 2: Update InspirationApp references

**File**: `scripts/templates/app.js`
**Action**: Minimal changes in InspirationApp (lines 858+):

- Line 1272-1285: Update constructor call from `SmoothImageCarousel` to `SimpleImageCarousel`
- Line 1268: `crossFadeDuration` option can be removed or ignored
- Lines 1583-1587: `refreshCurrentStyleInfo()` — same logic, reads `this.carousel.currentIndex`
- All other references (`pause()`, `resume()`, `next()`, `previous()`, `goToIndex()`, `destroy()`) stay the same

### Step 3: Clean up CSS

**File**: `scripts/templates/style.css`
**Action**: Simplify carousel CSS:

- Remove `.carousel-image-layer` dual-layer styles (opacity transition on layers)
- Add simple `.carousel-image` class with `opacity` transition (~0.4s)
- Keep `.carousel-image-stack` positioning (absolute, cover)
- Keep `.carousel-dot` styles unchanged
- Keep `.carousel-indicators` positioning unchanged
- Keep all Ken Burns keyframes and classes unchanged
- Keep `prefers-reduced-motion` handling unchanged

### Step 4: Remove stale debug logging

**File**: `scripts/templates/app.js`
**Action**: Remove `console.log('[DEBUG]...')` statements left from previous investigations:
- Line 479, 485, 489 in `updateIndicators()`
- Lines 1563-1565, 1570, 1577 in style info methods (verify line numbers, may have shifted)

### Step 5: Build and test

```bash
source ~/dev/.venv/bin/activate
python scripts/build_site.py
./bin/preview-local.sh
```

**Test checklist**:
- [ ] Images fade in/out smoothly (not instant swap)
- [ ] Ken Burns zoom effect active on each image
- [ ] Dots update correctly (1-2-3 sequence)
- [ ] Dot clicks navigate to correct image
- [ ] Style label in footer matches displayed image
- [ ] Content transitions: no image bleed between quotes
- [ ] Hover pauses, un-hover resumes
- [ ] Modal open pauses, close resumes with correct style shown
- [ ] Mobile: swipe left/right navigates images
- [ ] Reduced motion: Ken Burns disabled
- [ ] Cycle through all 5 quotes — verify clean transitions

### Step 6: Commit and deploy

```bash
git add scripts/templates/app.js scripts/templates/style.css output/script.js output/style.css
git commit -m "Replace dual-layer carousel with single-element fade

Eliminates the architectural source of 6 carousel synchronization bugs
over 6 months. Single <img> element with CSS opacity transition instead
of dual-layer cross-fade. Same visual features (Ken Burns, dots, touch
gestures, pause/resume) with ~200 lines instead of ~620.

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
git push
```

## Separate Follow-Up Tasks (Not Part of This Plan)

These are independent improvements identified during the architecture review:

### Fix "abstract artwork" prompt prefix
**File**: `scripts/generate_images.py` line 590
**Issue**: Every prompt starts with "Create a 1024x1024 abstract artwork:" which overrides style-specific directions (e.g., Ghibli, Arcane styles)
**Fix**: Make prefix style-category-aware: "abstract painting" for painting_technique, "illustration" for visual_storytelling

### Remove content-level style_name
**Files**: `scripts/build_site.py`, `scripts/templates/app.js` line ~1020
**Issue**: 14/15 images have mismatched `content.style_name` vs `image.style.name`. Frontend uses the correct one but the dual data model causes confusion.
**Fix**: Either remove `style_name` from content level or derive it from `images[0].style.name`

## Key Files to Read for Implementation

| File | What to read | Why |
|------|-------------|-----|
| `scripts/templates/app.js` lines 240-856 | Current SmoothImageCarousel | The class being replaced |
| `scripts/templates/app.js` lines 858-1617 | InspirationApp | All carousel integration points |
| `scripts/templates/style.css` lines 750-910 | Carousel + Ken Burns CSS | CSS to simplify |
| `scripts/templates/index.html` lines 50-70 | Image panel HTML structure | DOM context for carousel |
| `output/content.json` | Live data structure | Image array format the carousel receives |
