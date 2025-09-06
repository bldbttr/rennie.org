# rennie.org - AI-Generated Inspirational Content

Dynamic inspiration platform: AI-generated images for quotes and content using Nano Banana API.
**Project path:** `/Users/krennie/dev/rennie.org/`

## Tech Stack
- **Frontend:** Static HTML/CSS/JavaScript (no build process)
- **Backend:** Python scripts for image generation and site building
- **AI Generation:** Nano Banana API for image creation
- **Deployment:** GitHub Actions → DreamHost hosting
- **Content:** Markdown-based with frontmatter metadata

## Credit Usage Guidelines

**10s of lines** → Full steam ahead (content files, style tweaks, small scripts)
**100s of lines** → Go ahead, discuss if uncertain (new generators, major features)  
**1000s of lines** → Let's discuss strategy first (architecture changes)

## Project Structure

**Content Management:**
- `/content/inspiration/` - Individual markdown files for quotes/content
- `/content/styles/` - Reusable style templates for image generation
- Use frontmatter for metadata (title, author, tags, style reference)

**Scripts:**
- `/scripts/generate_images.py` - Nano Banana API integration
- `/scripts/build_site.py` - Static site generator
- `/scripts/content_parser.py` - Markdown and frontmatter parser
- `/bin/` - Bash scripts for operations (setup, generate, deploy)

**Generated Content:**
- `/generated/` - Images and processed content (gitignored)
- `/output/` - Deployable static site (gitignored)

## Virtual Environment
**Location:** `/Users/krennie/dev/.venv/` (shared across all dev projects)
```bash
# Activate virtual environment
source ~/dev/.venv/bin/activate

# Install requirements
pip install -r scripts/requirements.txt
```

## Quick Commands

```bash
# Activate virtual environment first
source ~/dev/.venv/bin/activate

# Generate images for new content
./bin/generate-new.sh

# Regenerate all images
./bin/regenerate-all.sh

# Build static site
python scripts/build_site.py

# Deploy to DreamHost
./bin/deploy.sh

# Full workflow (generate + build + deploy)
./bin/generate-new.sh && python scripts/build_site.py && ./bin/deploy.sh
```

## Content File Format

```markdown
---
title: "Make something people want"
author: "Paul Graham"
type: "quote"
source: "Y Combinator"
year: 2005
tags: ["startup", "entrepreneurship"]
style: "modern-inspirational"
status: "active"
---

Make something people want.

## Context
Additional context or notes about the quote...
```

## Style Library

Styles are defined in `/content/styles/styles.json`:
- `modern-inspirational` - Tech/startup aesthetic
- `classical-poetry` - Literary/romantic style
- Create new styles by adding to the JSON

## Development Workflow

1. **Add new content:** Create markdown file in `/content/inspiration/`
2. **Generate image:** Run `./bin/generate-new.sh`
3. **Build site:** Run `python scripts/build_site.py`
4. **Preview locally:** Open `/output/index.html`
5. **Deploy:** Run `./bin/deploy.sh` or push to trigger GitHub Actions

## Session Management
- Keep it simple - this is a right-sized project
- Focus on content quality over complex features
- Manual testing is fine for this scale
- Use print statements for debugging (no complex logging needed)

## Current Status (September 2025)
- 🚧 **Project:** Initial setup phase
- 📁 **Structure:** Core directories created
- ⏳ **Scripts:** To be implemented
- ⏳ **Content:** Ready for first pieces
- ⏳ **Deployment:** GitHub Actions to be configured

Focus: Beautiful, inspiring content with minimal complexity. 80% of the value with 40% of the effort.