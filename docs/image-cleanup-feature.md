# Image Cleanup Feature Specification

## Problem Statement

Currently, the image generation system can create images but cannot remove orphaned ones. Orphaned images occur when:
1. Content `.md` files are deleted from `content/inspiration/`
2. The number of variations is reduced (e.g., from 5 to 3 variations per content)

## Current State

**Image Management:**
- Images: `generated/images/{content-filename}_v{1-3}.png`
- Metadata: `generated/metadata/{content-filename}_v{variation}_metadata.json`
- Variations: Hard-coded to 3 per content piece
- Archive: Existing images moved to `generated/archive/` during regeneration

**Missing Functionality:**
- No orphaned image detection
- No cleanup/removal capability
- No configuration for variation count

## Solution Design

### Python Intelligence (`scripts/generate_images.py`)

#### New Methods

**`identify_orphaned_images(parsed_content_file, variations_per_content) -> Dict`**
```python
Returns: {
    "missing_content": [
        {"filename": "deleted-content_v1.png", "reason": "content file missing"},
        {"filename": "deleted-content_v2.png", "reason": "content file missing"}
    ],
    "excess_variations": [
        {"filename": "some-content_v4.png", "reason": "need only 3 variations"},
        {"filename": "some-content_v5.png", "reason": "need only 3 variations"}
    ],
    "total_orphaned": 4,
    "estimated_space_saved": "2.4 MB"
}
```

**`cleanup_orphaned_images(dry_run=True, archive_before_delete=True) -> Dict`**
- Archives orphaned images before deletion
- Removes both PNG and metadata files
- Returns detailed report of actions taken

#### New Command Line Options
- `--check-orphaned`: Identify orphaned images
- `--cleanup-orphaned`: Remove orphaned images (with confirmation)
- `--dry-run`: Show what would be removed without acting
- `--variations N`: Set number of variations (make configurable)

### Bash Orchestration

#### New Script: `bin/cleanup-images.sh`
```bash
#!/bin/bash
# Check for orphaned images and offer cleanup with user confirmation
# Shows what will be removed before acting
# Archives before deletion for safety
```

#### Enhanced: `bin/check-images.sh`
Add orphaned image section to output:
```
FILES THAT NEED NO IMAGES:
  (current output)

FILES THAT NEED IMAGES:
  (current output)

ORPHANED IMAGES FOUND:
  deleted-content_v1.png (content file missing)
  deleted-content_v2.png (content file missing)
  some-content_v4.png (excess variation, need only 3)
  
  Total: 3 orphaned images (1.2 MB)
```

#### Enhanced: `bin/generate-new-images-locally.sh`
Add cleanup offer after generation:
```
🧹 CLEANUP ORPHANED IMAGES
===========================
Found 3 orphaned images (1.2 MB). Clean up now? (yes/no):
```

### Configuration

#### Make Variations Configurable
Move from hard-coded `range(1, 4)` to configurable value:

**Option 1: Add to `content/styles/styles.json`**
```json
{
  "config": {
    "variations_per_content": 3
  },
  "styles": { ... }
}
```

**Option 2: Create `config.json`**
```json
{
  "images": {
    "variations_per_content": 3,
    "archive_before_cleanup": true
  }
}
```

## Implementation Phases

### Phase 1: Core Python Logic
1. ✅ Research current image management
2. Add `identify_orphaned_images()` method
3. Add `cleanup_orphaned_images()` method  
4. Add command-line flags for orphaned image operations
5. Make variations count configurable

### Phase 2: Bash Integration
1. Create `bin/cleanup-images.sh` orchestration script
2. Update `bin/check-images.sh` to show orphaned images
3. Add cleanup offer to `bin/generate-new-images-locally.sh`

### Phase 3: Testing & Safety
1. Test with various orphaned image scenarios
2. Verify archive functionality works correctly
3. Ensure dry-run mode shows accurate preview
4. Test user confirmation workflows

## Safety Features

- **Archive First**: Always move to archive before deletion
- **Dry Run Default**: Show what would be removed without acting
- **User Confirmation**: Clear prompts before destructive actions
- **Detailed Reporting**: Log exactly what was removed and why
- **Reversible**: Archived images can be restored if needed

## Usage Examples

```bash
# Check for orphaned images
./bin/check-images.sh

# See what would be cleaned up (dry run)
python scripts/generate_images.py --check-orphaned --dry-run

# Clean up orphaned images with confirmation
./bin/cleanup-images.sh

# Full workflow with cleanup
./bin/generate-new-images-locally.sh  # includes cleanup offer
```

## Architecture Alignment

Follows project principle: **orchestration in bash, intelligence in Python**
- Python: Detection logic, file operations, safety checks
- Bash: User interaction, workflow orchestration, confirmation prompts