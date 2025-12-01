# rennie.org

Personal homepage displaying inspiration with AI-generated artwork.

## Features
- AI-generated artwork using Google Gemini 2.5 Flash
- Image carousel with Ken Burns cinematic effects
- Touch gestures and keyboard navigation
- Multiple image variations per content piece
- Responsive design
- Automated GitHub Actions deployment to DreamHost

## Current Content
- "Make something people want" - Paul Graham
- "Product/Market Fit" - Marc Andreessen
- "Customer Experience" - Steve Jobs
- "Third Chair" - original content

## Tech Stack
- **Image Generation:** Google Gemini 2.5 Flash
- **Frontend:** Static HTML/CSS/JavaScript
- **Backend:** Python scripts for image generation and site building
- **Content:** Markdown files with YAML frontmatter
- **Deployment:** GitHub Actions → DreamHost

## Project Structure
```
content/inspiration/  # Markdown content files
scripts/              # Python scripts (generate_images.py, build_site.py)
bin/                  # Bash utility scripts
generated/images/     # AI-generated artwork (gitignored)
output/               # Built site (gitignored)
```

## Quick Start
```bash
# Activate virtual environment
source ~/dev/.venv/bin/activate

# Check what needs generation
./bin/check-images.sh

# Generate images locally
./bin/generate-new-images-locally.sh

# Preview locally
./bin/preview-local.sh

# Deploy
./bin/commit-and-deploy.sh
```

## License
Personal project - all rights reserved.
