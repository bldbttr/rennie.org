# Image-Style Deployment Mismatch Investigation

**Date**: September 26, 2025
**Issue**: Style names not matching displayed images
**Status**: **DEPLOYMENT MISMATCH IDENTIFIED** - Local vs Production serving different images
**Context Limit**: Investigation incomplete due to thread context limits

## Problem Summary

User reported that style names and descriptions were sometimes matching each other, but not matching the actual displayed images. Investigation revealed this is **NOT a frontend synchronization issue** but a **deployment/image serving mismatch**.

## Key Findings

### 1. Frontend Synchronization ✅ WORKING CORRECTLY

**Investigation Method**: Added comprehensive debug logging to carousel state management.

**Debug Logs Showed**:
```
thirdchair_v1.png → style: "kline-gestural"
thirdchair_v2.png → style: "monet-impressionist"
thirdchair_v3.png → style: "kibuishi-world"

paul-graham-make-something_v1.png → style: "monet-impressionist"
```

**Data Verification**:
- ✅ content.json has correct image-to-style mappings
- ✅ Carousel receives correct style data (`image.style.name`)
- ✅ `updateStyleInfo()` displays the correct style name
- ✅ Modal shows metadata for correct image index
- ✅ All synchronization fixes from earlier in session are working

### 2. Image Generation Pipeline ✅ WORKING CORRECTLY

**Process Verified**:
1. **Style Assignment**: Each image gets specific style during generation
   - v1: Uses original style from content frontmatter
   - v2: Random style from same category
   - v3: Random style from opposite category

2. **Data Coupling**: Style metadata properly stored with each image
   ```json
   {
     "filename": "thirdchair_v1.png",
     "style": {"name": "kline-gestural", "approach": "painting_technique"}
   }
   ```

3. **Generation Metadata**: Prompts match assigned styles
   - thirdchair_v1 prompt: "Franz Kline style bold gestural abstraction..."
   - Matches style name: "kline-gestural"

### 3. **CRITICAL DISCOVERY**: Deployment Mismatch 🚨

**Local vs Production Serving Different Images**:

- **Local development** (`http://localhost:8000`):
  - Serves images from `/generated/images/`
  - Images match their assigned styles correctly

- **Production** (`https://rennie.org`):
  - Appears to serve different images
  - Images from `/generated/archive/2025-09-26_11-38/` (older generation)
  - **These older images have different visual styles than current metadata**

**Evidence**:
- User reports: "the images we are seeing locally are totally different than what's in production"
- Local images match `/generated/images/`
- Production images match `/generated/archive/2025-09-26_11-38/`
- Spot check confirms `/generated/images/` and `/generated/metadata/` are properly matched

## Root Cause Analysis

### Deployment Pipeline Issue

The problem appears to be in the **image deployment process**:

1. **New images generated**: Stored in `/generated/images/` with correct style metadata
2. **Content.json updated**: References new images with correct style mappings
3. **Deployment issue**: Production is serving old images from archive instead of current images
4. **Result**: Style names from new metadata, but images from old generation

### Investigation Needed

**Next troubleshooting session should investigate**:

1. **Deployment Process**:
   - How images get copied from `/generated/images/` to production
   - Whether GitHub Actions is copying correct image files
   - If there's a caching issue serving old images

2. **Image Serving Path**:
   - What images are actually being served in production
   - Whether `/output/images/` contains correct files before deployment
   - If CDN or hosting is caching old images

3. **Archive System**:
   - Why production might be serving from archive instead of current
   - Whether deployment script has path bugs

## Files for Investigation

### Current State (Local - Working)
- `/generated/images/` - Current images with correct styles
- `/generated/metadata/` - Metadata matching current images
- `/output/content.json` - Style mappings for current images

### Archive State (Production - Mismatched)
- `/generated/archive/2025-09-26_11-38/` - Older images with different styles
- Production serving path investigation needed

### Code Files
- `/scripts/build_site.py` - Image copying logic
- `/.github/workflows/` - Deployment automation
- `/bin/deploy.sh` - Deployment scripts

## Debug Tools Added

**For future investigation**, comprehensive logging was added:

```javascript
// In updateStyleInfo() - logs what style is being displayed
console.log(`[DEBUG] updateStyleInfo called with index=${index}, image:`, image);
console.log(`[DEBUG] image.style:`, image?.style);
console.log(`[DEBUG] image.filename:`, image?.filename);

// In carousel transitionToImage() - logs what image is being shown
console.log(`[DEBUG] Carousel transitioning to index=${index}, image:`, nextImage);
console.log(`[DEBUG] nextImage.style:`, nextImage?.style);
```

**To use**: Build with current templates and run `./bin/preview-local.sh`, then check browser console.

## Deployment Investigation Priority

**High Priority**:
- Verify production image serving path
- Check if GitHub Actions deploys correct images
- Compare production file timestamps with local

**Medium Priority**:
- CDN/hosting cache invalidation
- Archive system review

## Session Status

- ✅ **Frontend synchronization**: All carousel state issues resolved
- ✅ **Data pipeline**: Image generation and metadata coupling working
- ✅ **Deployment mismatch**: **RESOLVED** - Cache configuration issue fixed
- ✅ **Investigation complete**: Root cause identified and corrected

## RESOLUTION (Session 2 - 2025-09-26)

### Final Root Cause: Browser/CDN Caching Issue ✅

The issue was **NOT** a deployment problem but a **caching configuration issue**:

**Problem**:
- DreamHost hosting set aggressive 30-day cache headers (`max-age=2592000`)
- Users with cached content saw old images while metadata showed new styles
- Fresh browsers (Safari) showed correct images, cached browsers (Chrome) showed old images

**Evidence**:
- ✅ Git commits contained correct images (verified by file size comparison)
- ✅ Deployment process was working correctly (rsync successful)
- ✅ Production server was serving correct files (2,493,945 bytes = Spider-Verse, not 1,769,027 bytes = Ghibli)
- ❌ Browser cache was serving stale content due to 30-day TTL

**Solution Implemented**:
1. **Added `.htaccess` file** to `/output/` directory
2. **Reduced image cache time** from 30 days to 1 day (`max-age=86400`)
3. **Set appropriate cache for code** (1 hour for HTML/CSS/JS)
4. **Enabled compression** for better performance

**Cache Settings**:
```apache
# Images - cache for 1 day (balance between performance and updates)
<FilesMatch "\.(png|jpg|jpeg|gif|svg|webp)$">
    Header set Cache-Control "max-age=86400, public"
</FilesMatch>

# HTML, CSS, JS - cache for 1 hour (in case of updates)
<FilesMatch "\.(html|css|js|json)$">
    Header set Cache-Control "max-age=3600, public"
</FilesMatch>
```

**Verification**:
```bash
# Before: cache-control: max-age=2592000 (30 days)
# After:  cache-control: max-age=86400, public (1 day)
curl -sI "https://rennie.org/images/paul-graham-make-something_v3.png"
```

### Lessons Learned

1. **Image-style mismatches can have multiple causes**:
   - Frontend synchronization bugs ❌
   - Deployment/rsync issues ❌
   - **Browser/CDN caching issues** ✅

2. **Debugging process**:
   - Always verify file integrity at each step (local → git → deployment → production)
   - Check HTTP headers for cache configuration
   - Test with fresh browser sessions to isolate caching

3. **Cache configuration for personal sites**:
   - 30-day cache too aggressive for sites with active development
   - 1-day image cache provides good balance
   - 1-hour code cache allows quick updates

4. **Simple solutions work best**:
   - `.htaccess` file simpler than image versioning
   - Appropriate for low-traffic personal sites
   - No code changes required in application

### Prevention Strategy

**For future deployments**:
- ✅ Cache configuration is now appropriate for development pace
- ✅ New images will be visible within 1 day (vs 30 days)
- ✅ Force refresh (Cmd+Shift+R) still works for immediate testing
- ✅ Performance maintained with reasonable cache times

---

## Context for Next Thread

**Quick Start for Next Investigation**:
1. Compare images being served in production vs `/generated/images/`
2. Check GitHub Actions deployment logs
3. Verify `/output/images/` contents before deployment
4. Test production cache invalidation

**Known Working**: All frontend carousel synchronization, image generation, and metadata coupling. The issue is purely in deployment/serving of image files.