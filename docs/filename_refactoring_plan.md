# Filename Refactoring Plan
**Date:** September 2025  
**Issue:** Complex, fragile filename generation based on title/author content  
**Solution:** Simple, stable filename generation based on markdown filenames  

## Problem Analysis

### Current Fragile Pattern
The `generate_image_filename()` method in `scripts/generate_images.py` creates filenames by processing title and author content:

```python
def generate_image_filename(self, content_data: Dict[str, Any], variation: int = 1) -> str:
    author = content_data['author'].lower().replace(' ', '_')
    title = content_data['title'].lower()
    title_clean = ''.join(c if c.isalnum() or c in [' ', '-'] else '' for c in title)
    title_clean = title_clean.replace(' ', '_')[:50]  # Limit length
    return f"{author}_{title_clean}_v{variation}.png"
```

### Problems with Current Approach
1. **Long, unwieldy filenames**: `marc_andreessen_you_can_always_feel_productmarket_fit_when_its_hap_v1.png`
2. **Fragile**: Changes to title/author break image associations
3. **Truncation issues**: 50-character limit causes inconsistent naming
4. **Complex debugging**: Hard to map files to generated assets
5. **Multiple implementations**: Different parts of code extract filenames differently

### Current Content Files
- `content/inspiration/pmarca-pmf.md` 
- `content/inspiration/steve-jobs-customer-experience-back-to-technology.md`
- `content/inspiration/paul-graham-make-something.md`

### Desired Naming Pattern
- `pmarca-pmf_v1.png`, `pmarca-pmf_v2.png`, `pmarca-pmf_v3.png`
- `steve-jobs-customer-experience-back-to-technology_v1.png`, etc.
- `paul-graham-make-something_v1.png`, etc.

## Implementation Plan

### Phase 1: Create Filename Utility Function
**File:** `scripts/generate_images.py`
**New method:**

```python
def get_base_filename_from_content(self, content_data: Dict[str, Any]) -> str:
    """Extract base filename from content_file field"""
    content_file = content_data.get('content_file', '')
    if content_file.startswith('content/inspiration/'):
        return content_file.replace('content/inspiration/', '').replace('.md', '')
    else:
        # Fallback for unexpected paths
        return Path(content_file).stem if content_file else 'unknown'
```

### Phase 2: Replace Core Filename Generation
**File:** `scripts/generate_images.py`
**Replace method:**

```python  
def generate_image_filename(self, content_data: Dict[str, Any], variation: int = 1) -> str:
    """Generate a consistent filename based on content file name."""
    base_filename = self.get_base_filename_from_content(content_data)
    return f"{base_filename}_v{variation}.png"
```

### Phase 3: Update All References Throughout Codebase

#### `scripts/generate_images.py` Updates:
1. **`check_new_styles()` method (lines 132-134, 151-153)**:
   - Replace manual `content_file.replace()` logic with utility function
   
2. **`check_images_inventory()` method (lines 235-239)**:
   - Replace manual filename extraction with utility function

3. **All metadata filename generation**:
   - Ensure consistency with new naming scheme

#### `scripts/build_site.py` Updates:
1. **Image path resolution logic**:
   - Update any hardcoded expectations about filename format
   
2. **Metadata loading**:
   - Ensure `load_image_metadata()` works with new naming scheme

#### `bin/generate-new-images-locally.sh` Updates:
1. **Display messages**:
   - Update to show simple filenames instead of complex generated names

### Phase 4: Clean Break Migration

#### Step 1: Remove Old Files
```bash
# Remove all existing generated images and metadata
rm -rf generated/images/*.png
rm -rf generated/metadata/*.json
# Keep archive folder for reference
```

#### Step 2: Test New System
```bash
# Parse content to ensure content_file fields are correct
python scripts/content_parser.py

# Test filename generation without API calls
python scripts/generate_images.py --check-images

# Verify expected filenames match simple pattern
```

## Files Requiring Changes

### Primary Changes
- **`scripts/generate_images.py`**: Major refactoring of filename logic
- **`scripts/build_site.py`**: Minor updates to image path handling

### Secondary Updates  
- **`bin/generate-new-images-locally.sh`**: Display message updates
- **Documentation**: Update any references to filename patterns

### No Changes Required
- **`scripts/content_parser.py`**: Already correctly populates `content_file` field
- **Content files**: No changes to markdown structure needed

## Expected Outcomes

### Before Refactoring
```
📝 Processing: You can always feel product/market fit when it's happening by Marc Andreessen
🖼️ Image: marc_andreessen_you_can_always_feel_productmarket_fit_when_its_hap_v1.png (brightness: 0.563)
✓ Metadata saved: generated/metadata/marc_andreessen_you_can_always_feel_productmarket_fit_when_its_hap_v2_metadata.json
```

### After Refactoring
```
📝 Processing: pmarca-pmf.md
🖼️ Image: pmarca-pmf_v1.png (brightness: 0.563)  
✓ Metadata saved: generated/metadata/pmarca-pmf_v2_metadata.json
```

## Benefits

1. **Predictable**: Clear 1:1 mapping between markdown files and generated assets
2. **Stable**: Editing title/author content doesn't break image associations  
3. **Debuggable**: Easy to trace issues between content and generated files
4. **Maintainable**: Single source of truth for filename generation
5. **Human-readable**: Short, meaningful filenames

## Risk Mitigation

- **Clean break approach**: No backward compatibility complexity
- **Archive preservation**: Keep existing generated files in archive folder
- **Incremental testing**: Test filename generation before full regeneration
- **Validation**: Verify all content files have proper `content_file` fields

## Implementation Timeline

1. **Write plan**: ✅ Complete
2. **Git cleanup**: ✅ Complete - Committed refactoring plan
3. **Remove old files**: ✅ Complete - Clean slate achieved (9 PNG + 9 JSON files removed)
4. **Core refactoring**: ✅ Complete - Added utility function + replaced core method
5. **Update references**: ✅ Complete - Updated all filename logic throughout codebase
6. **Testing**: ✅ Complete - Validated new naming scheme works correctly
7. **Regeneration**: ✅ Ready for full image generation with new scheme

**Total actual time:** ~30 minutes for robust, maintainable filename system.

## Implementation Results ✅

### Successfully Completed (September 2025)

**Git commits:**
- `94a059e`: Add filename refactoring plan
- `6f86a69`: Refactor filename generation to use markdown filenames

**Files Modified:**
- `scripts/generate_images.py`: Major refactoring with new utility function and updated references
- `docs/filename_refactoring_plan.md`: Comprehensive planning document

**Validation Results:**
```bash
# Before refactoring (complex, fragile):
marc_andreessen_you_can_always_feel_productmarket_fit_when_its_hap_v1.png

# After refactoring (simple, stable):
pmarca-pmf_v1.png
steve-jobs-customer-experience-back-to-technology_v1.png  
paul-graham-make-something_v1.png
```

**Testing Confirmed:**
- ✅ Content parsing works correctly with `content_file` field population
- ✅ Filename utility function extracts clean base names from markdown paths
- ✅ Image filename generation produces expected simple patterns
- ✅ Preview analysis shows correct filename mappings
- ✅ Check-images inventory displays clean filenames

**Ready for Image Generation:**
The system now generates predictable, stable filenames based on markdown file names rather than complex title/author processing. All old files removed for clean slate. Image generation script ready to run with new naming scheme.

## Frontend Fix Implementation ✅

### Critical Issue Discovered & Resolved (September 13, 2025)

During final testing, we discovered the **frontend JavaScript was still using the old filename pattern** while the backend had been refactored to the new pattern. This caused a mismatch where:

- **Backend generated:** `pmarca-pmf_v1.png` (new clean pattern)
- **Frontend expected:** `marc_andreessen_you_can_always_feel_productmarket_fit_when_its_hap_v1.png` (old complex pattern)

The site was working because **legacy files from both patterns coexisted** in `output/images/`, creating accidental compatibility.

### Resolution Applied

**File: `scripts/templates/app.js:938-948`** - Updated `getImagePath()` method:

```javascript
// BEFORE (fragile, complex)
getImagePath(content) {
    const author = content.author.toLowerCase().replace(/\s+/g, '_').replace(/[^a-z0-9_]/g, '');
    const title = content.title.toLowerCase().replace(/\s+/g, '_').replace(/[^a-z0-9_]/g, '');
    return `images/${author}_${title}.png`;
}

// AFTER (stable, simple)  
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
```

**File: `scripts/build_site.py:186`** - Updated display message for consistency:

```python
# BEFORE
print(f"📝 Processing: {content['title']} by {content['author']}")

# AFTER  
base_filename = get_base_filename_from_content(content)
print(f"📝 Processing: {base_filename}.md")
```

### Legacy Files Archived

**10 legacy images** safely archived to `generated/archive/filename_refactoring_cleanup_20250913_081751/`:

- `marc_andreessen_you_can_always_feel_productmarket_fit_when_its_hap_v*.png` (3 files)
- `steve_jobs_start_with_the_customer_experience_and_work_backwa_v*.png` (3 files)  
- `paul_graham_make_something_people_want_v*.png` (3 files)
- `paul_graham_make_something_people_want.png` (1 file)

### Testing Results

✅ **Build verification:** Site builds correctly with new system  
✅ **Frontend/backend sync:** Both generate identical filename patterns  
✅ **Clean inventory:** Only new pattern files remain in generated/ and output/  
✅ **Display messages:** Show clean filename format as planned  

### Key Achievements

1. **Eliminated fragility**: No more breaking when titles/authors change
2. **Improved debuggability**: Clear 1:1 mapping between content files and generated assets  
3. **Enhanced maintainability**: Single source of truth for filename generation
4. **Better user experience**: Short, meaningful filenames instead of truncated chaos
5. **Clean architecture**: Consistent filename handling throughout codebase
6. **🆕 Frontend/backend alignment**: Both systems now use identical naming logic
7. **🆕 Legacy compatibility removed**: Clean break from complex filename patterns