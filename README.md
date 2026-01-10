# rennie.org

Personal homepage displaying inspiration with AI-generated artwork.

## Features
- AI-generated artwork using Google Nano Banana Pro (Gemini 3 Pro Image)
- Sophisticated image carousel with smooth cross-fade transitions
- Ken Burns cinematic effects (4 animation types: zoom in/out, pan left/right)
- Touch gestures (swipe) and full keyboard navigation
- Multiple image variations per content piece (3 variations, 10 seconds each)
- Carousel indicators with direct navigation
- Accessibility support (prefers-reduced-motion)
- Responsive design
- Automated GitHub Actions deployment to DreamHost

## Current Content
- "Make something people want" - Paul Graham
- "Product/Market Fit" - Marc Andreessen
- "Customer Experience" - Steve Jobs
- "Third Chair" - Henrik Karlsson
- "Mental phenomena are preceded by mind" - Dhammapada

## Tech Stack
- **Image Generation:** Google Nano Banana Pro (Gemini 3 Pro Image)
- **Frontend:** Static HTML/CSS/JavaScript
- **Backend:** Python scripts for image generation and site building
- **Content:** Markdown files with YAML frontmatter
- **Deployment:** GitHub Actions → DreamHost

## Project Structure
```
content/inspiration/  # Markdown content files
scripts/              # Python scripts (generate_images.py, build_site.py)
scripts/templates/    # HTML/CSS/JS source templates (edit these!)
bin/                  # Bash utility scripts
generated/images/     # AI-generated artwork (gitignored)
generated/archive/    # Archived images from previous generations
output/               # Built site (gitignored, template-generated)
docs/                 # Feature specs and implementation guides
```

### ⚠️ Important: Template System
Files in `/output/` are **template-generated** by `scripts/build_site.py` during deployment.

**Never edit directly:**
- `/output/script.js` (generated from `/scripts/templates/app.js`)
- `/output/style.css` (generated from `/scripts/templates/style.css`)
- `/output/index.html` (generated from `/scripts/templates/index.html`)

**Always edit source templates** in `/scripts/templates/` directory. Changes to `/output/` files will be lost during deployment.

## Quick Start
```bash
# Activate virtual environment
source ~/dev/.venv/bin/activate

# Check image status (what needs generation or cleanup)
./bin/check-images.sh

# Generate images for new content (hybrid local-first workflow)
./bin/generate-new-images-locally.sh

# Clean up orphaned images (deleted content or reduced variations)
./bin/cleanup-images.sh

# Preview locally (serves on http://localhost:8000)
./bin/preview-local.sh

# Commit and deploy
./bin/commit-and-deploy.sh

# Archive before regeneration (preserves old images)
python scripts/generate_images.py --archive-and-regenerate
```

## Documentation
- **Carousel Feature**: `docs/carousel_feature_spec.md` - Complete carousel implementation guide
- **Smooth Transitions**: `docs/smooth_carousel_transitions_implementation.md` - Cross-fade system
- **Build System**: `docs/inspiration_site_build_notes.md` - Template management guide
- **Architecture**: `docs/workflow_architecture_analysis.md` - Design decisions and lessons

## License
Personal project - all rights reserved.
