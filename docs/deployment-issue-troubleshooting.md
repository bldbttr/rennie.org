# GitHub Actions Deployment Issue Troubleshooting

**Issue**: GitHub Actions workflow failing at "Generate new images" step after implementing multi-image variations feature.

## Problem Summary

The deployment has been failing consistently since implementing Phase 5 (multi-image variations feature). The workflow completes these steps successfully:
- ✅ Set up job
- ✅ Checkout repository  
- ✅ Set up Python 3.11
- ✅ Cache Python dependencies
- ✅ Install dependencies
- ✅ Parse content
- ❌ **FAILS HERE**: Generate new images
- ⏸️ Build static site (not reached)
- ⏸️ Setup SSH key for deployment (not reached)
- ⏸️ Deploy to DreamHost (not reached)

## Root Cause Analysis

### Initial Issue: Import Path Problems
- **Problem**: Added `from content_parser import ContentParser` inside `generate_variations()` method
- **Symptom**: `ModuleNotFoundError: No module named 'content_parser'` when run from different directories
- **Status**: ✅ FIXED with dynamic sys.path manipulation

### Current Issue: Unknown Error in Image Generation
- **Problem**: Script still fails in GitHub Actions even after import fixes
- **Testing**: Local testing works fine: `python scripts/generate_images.py --new-only` succeeds
- **Status**: ❌ UNRESOLVED - Cannot access detailed logs due to permissions

## Changes Made

### Multi-Image Variations Feature (Phase 5)
- Enhanced `scripts/generate_images.py` with `generate_variations()` method
- Added `--variations` flag (default: 3)
- Smart style selection: original → same category → opposite category
- Updated site builder to handle multiple images array
- Frontend random image selection

### Import Fixes Applied
```python
# Fixed dynamic import in generate_variations method
import sys
import os
script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)
from content_parser import ContentParser
```

## Deployment Workflow Status

### Failed Runs
- `17568867698` - Multi-image variations implementation
- `17570975475` - Import fix test  
- `17571016137` - Deployment without variations test

### Current Workflow Configuration
```yaml
# Temporarily simplified for debugging
python scripts/generate_images.py --new-only
# Was: python scripts/generate_images.py --new-only --variations 3
```

## Local Testing Results

✅ **Working locally**:
```bash
source ~/dev/.venv/bin/activate
python scripts/generate_images.py --new-only --variations 1
# Result: "Generation Summary: Successful: 0, Skipped: 1, Errors: 0"
```

✅ **Import test**:
```bash
python scripts/generate_images.py --help
# Shows all flags including --variations
```

## Likely Causes

1. **GitHub Actions Environment Issue**
   - Different Python path behavior in CI environment
   - Missing dependencies not caught by requirements.txt
   - Environment variable issues with enhanced script

2. **Code Logic Issue**
   - Error in variations generation logic not visible in local testing
   - Edge case in style selection algorithm
   - Memory/timeout issues with enhanced processing

3. **API Integration Issue**
   - Enhanced Nano Banana API calls causing failures
   - Rate limiting or authentication issues with multiple variations
   - Response parsing issues in new variation logic

## Immediate Action Items

1. **Get Detailed Logs**
   - Need repository admin access to view full GitHub Actions logs
   - Alternative: Add extensive debug logging to scripts

2. **Staged Rollback Test**
   - Test deployment with original single-image generation
   - Verify base functionality before re-adding variations

3. **Enhanced Local Testing**
   - Test with exact GitHub Actions Python version (3.11)
   - Test import paths from various working directories
   - Test with and without API key to simulate different scenarios

## Workaround Strategy

### Option 1: Temporary Rollback
- Revert to single-image generation for reliable deployment
- Re-implement variations feature with better error handling

### Option 2: Debug Enhancement
- Add extensive logging to generation script
- Implement try/catch around variations logic
- Add fallback to single-image generation on failure

### Option 3: Alternative Architecture
- Move variations generation to separate workflow step
- Generate single image in main workflow, variations in post-processing
- Deploy with single image, enhance with variations asynchronously

## Files Modified in This Session

- `scripts/generate_images.py` - Multi-variations logic + import fixes
- `scripts/build_site.py` - Multi-image support  
- `.github/workflows/deploy.yml` - Updated for variations (reverted for debugging)
- `bin/generate-new.sh` - Added --variations 3 (may need revert)
- `bin/regenerate-all.sh` - Added --variations 3 (may need revert)

## Next Steps for New Session

1. Access detailed GitHub Actions logs or add debug logging
2. Test deployment with clean single-image generation
3. Gradually re-introduce variations feature with better error handling
4. Consider splitting variations into separate workflow or post-processing step

**Current Site Status**: Multi-image variations working locally and deployed manually, but automated deployment broken.