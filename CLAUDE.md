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

# Check image status (shows what needs generation or cleanup)
./bin/check-images.sh

# Generate images for new content (hybrid local-first workflow)
./bin/generate-new-images-locally.sh

# Clean up orphaned images (for deleted content or reduced variations)
./bin/cleanup-images.sh

# Commit and deploy locally generated images
./bin/commit-and-deploy.sh

# Legacy: Generate missing images only
./bin/generate-new.sh

# Legacy: Regenerate all images
./bin/regenerate-all.sh
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

## Project Philosophy

**Personal Project Scale** - This is a personal inspiration site, not an enterprise application. We've learned to avoid over-engineering:

- **Right-sized solutions**: Prefer simple, maintainable code over enterprise patterns
- **Local-first workflow**: Immediate feedback over complex CI/CD when possible  
- **Stable, predictable naming**: Simple filename schemes over complex generation logic
- **Manual processes are OK**: Don't automate everything - some things are fine to do by hand

See `docs/workflow_architecture_analysis.md` and `docs/filename_refactoring_plan.md` for lessons learned about avoiding over-engineering.

## Session Management
- Keep it simple - this is a right-sized project
- Focus on content quality over complex features
- Manual testing is fine for this scale
- Use print statements for debugging (no complex logging needed)

## Current Status (September 2025)
- ✅ **Project:** Fully operational with hybrid local-first workflow  
- ✅ **Structure:** Complete directory structure and automation
- ✅ **Scripts:** All Python and bash scripts implemented
- ✅ **Content:** 3+ inspirational pieces with AI-generated artwork
- ✅ **Deployment:** Live at https://rennie.org via GitHub Actions

Focus: Beautiful, inspiring content with minimal complexity. 80% of the value with 40% of the effort.