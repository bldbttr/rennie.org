# Inspiration Site Development Specification
**Project**: rennie.org Inspiration Site with AI-Generated Artwork  
**Repository**: https://github.com/hoggfather/rennie.org  
**Tech Stack**: Nano Banana (Gemini 2.5 Flash Image) + Static Site + GitHub Actions  
**IMPORTANT**: Always use `gemini-2.5-flash` model (latest Nano Banana), NOT preview versions

## Project Intent

Create a personal homepage that displays inspiring quotes, poems, and stories alongside AI-generated artwork. The site should:

- **Showcase curated inspiration** with beautiful AI-generated visuals
- **Rotate content randomly** on each page load/refresh
- **Enable easy content management** through markdown files in git
- **Deploy automatically** when new content is added
- **Cost-effectively generate images** (~$0.04 per image with Nano Banana)
- **Host statically** on existing DreamHost infrastructure

## Current Status

✅ **Repository Structure**: Right-sized directory structure created  
✅ **Git Setup**: Repository live at github.com/hoggfather/rennie.org  
✅ **Nano Banana API**: Tested and working (API key: AIzaSyCh41VaooU6xexjq7zndc7FSNOh2Sg4-EE)  
✅ **Initial Content**: Paul Graham "Make something people want" quote ready  
✅ **Style Library**: Basic reusable prompt templates defined  

🔄 **Next Phase**: Build core automation scripts

## Directory Structure

```
rennie.org/
├── .github/workflows/         # GitHub Actions (to create)
├── bin/                      # Bash scripts (to create)  
├── content/
│   ├── inspiration/          # Individual content pieces ✅
│   │   ├── paul-graham-make-something.md ✅
│   │   └── template.md ✅
│   └── styles/              # Visual style library ✅
│       ├── styles.json ✅
│       └── README.md ✅
├── scripts/                 # Python automation (to create)
├── web/                     # Static website (to create)
├── generated/               # AI-generated images (gitignored)
├── output/                  # Final deployable site (gitignored)
└── docs/                    # Documentation ✅
```

## Development Tasks

### Phase 1: Core Python Scripts (scripts/)

#### 1. Content Parser (`scripts/content_parser.py`)
**Purpose**: Parse markdown files and combine with style library
**Requirements**:
- Parse YAML frontmatter from markdown files
- Load and merge style definitions from `content/styles/styles.json`
- Handle `style_approach` field to categorize literal vs artistic styles
- Support `style` field as either specific style names or "random" for category-based selection
- Generate complete image prompts by combining content + style + personal context
- Extract "Why I Like It" and "What I See In It" sections for prompt enhancement
- Output structured data for image generation and site building
- Handle missing styles gracefully with fallback to category defaults
- Validate required frontmatter fields (title, author, type, source, style_approach)

**Input**: `content/inspiration/*.md` + `content/styles/styles.json`  
**Output**: Structured content data for other scripts

#### 2. Image Generator (`scripts/generate_images.py`)
**Purpose**: Generate missing images using Nano Banana API
**Requirements**:
- Use Google Gemini 2.5 Flash Image API (model: "gemini-2.5-flash") - Latest Nano Banana
- Check which content pieces need images (compare content vs generated/images/)
- Generate only missing images (incremental generation)
- Build prompts using content + style library
- Save images to `generated/images/` with consistent naming
- Create metadata file tracking generation details
- Handle API errors gracefully
- Support force-regeneration flag

**Environment**: Requires `GEMINI_API_KEY`  
**Input**: Parsed content data  
**Output**: PNG images in `generated/images/` + metadata

#### 3. Site Builder (`scripts/build_site.py`)
**Purpose**: Generate static website from content + images
**Requirements**:
- Create single-page application that randomly displays content
- Copy generated images to output directory
- Generate JSON API endpoint for content
- Create responsive HTML/CSS/JS
- Handle missing images gracefully (show placeholder)
- Optimize for fast loading
- Include proper meta tags and SEO

**Input**: Parsed content + generated images  
**Output**: Complete static site in `output/`

### Phase 2: Bash Automation (bin/)

#### 1. Generate New Images (`bin/generate-new.sh`)
**Purpose**: Generate images for content that doesn't have them yet
```bash
#!/bin/bash
cd "$(dirname "$0")/.."
python scripts/generate_images.py --new-only
echo "✅ Generated images for new content"
```

#### 2. Regenerate All (`bin/regenerate-all.sh`) 
**Purpose**: Force regenerate all images (for style changes)
```bash
#!/bin/bash
cd "$(dirname "$0")/.."
python scripts/generate_images.py --force-all
echo "✅ Regenerated all images"
```

#### 3. Build and Deploy (`bin/deploy.sh`)
**Purpose**: Build site and deploy to DreamHost
```bash
#!/bin/bash
cd "$(dirname "$0")/.."
python scripts/build_site.py
# rsync output/ to DreamHost (details TBD)
echo "✅ Deployed to rennie.org"
```

### Phase 3: Static Website (web/)

#### 1. Homepage Template (`web/index.html`)
**Purpose**: Single-page app that displays random inspiration
**Requirements**:
- Clean, elegant design
- Random content selection on load/refresh
- Responsive layout (mobile + desktop)
- Typography focused (content is primary)
- Image as background or side-by-side layout
- Author attribution
- "New Inspiration" button for manual refresh
- Fast loading with minimal dependencies

#### 2. Styling (`web/style.css`)
**Requirements**:
- Modern, clean aesthetic
- Readable typography (Georgia/serif for content)
- Responsive grid layout
- Subtle animations/transitions
- High contrast for accessibility
- Print-friendly styles

#### 3. Frontend Logic (`web/script.js`)
**Requirements**:
- Load content from JSON API
- Random selection algorithm
- Smooth transitions between content
- Keyboard navigation (spacebar for new inspiration)
- Error handling for missing images
- Local storage to avoid immediate repeats

### Phase 4: GitHub Actions (.github/workflows/)

#### 1. Generate and Deploy Workflow
**Trigger**: Push to main branch with changes in `content/`
**Steps**:
1. Set up Python environment
2. Install dependencies from `scripts/requirements.txt`
3. Run content parser and image generator
4. Build static site
5. Deploy to DreamHost via rsync
6. Commit any generated assets back to repo

**Required Secrets**:
- `GEMINI_API_KEY`: Google AI Studio API key
- `DREAMHOST_SSH_KEY`: SSH private key for deployment
- `DREAMHOST_HOST`: DreamHost server hostname
- `DREAMHOST_USER`: DreamHost username  
- `DREAMHOST_PATH`: Path to rennie.org directory

## Technical Specifications

### Content Format
```yaml
---
title: "Quote or poem title"
author: "Author Name"
type: "quote"  # or "poem", "story"
source: "Original Source"
year: 2025
tags: ["tag1", "tag2"]
style: "modern-inspirational"  # from styles.json
status: "active"  # or "draft", "archived"
---

The actual inspiring content goes here.

## Optional Context
Background information...
```

### Image Generation Prompt Building
1. Load base prompt from style library
2. Add content-specific elements  
3. Include mood and composition guidance
4. **Optimize for square format**: Ensure prompts work well for 1:1 aspect ratio
5. Final prompt format: `"{base_prompt}, {elements}, {mood}, square composition, centered focus"`

### API Integration
- **Model**: `gemini-2.5-flash` (Latest Nano Banana - NOT preview version)
- **Cost**: ~$0.039 per 1024x1024 image
- **Output**: PNG format, base64 encoded, 1024x1024 square
- **Rate Limiting**: Respect API limits with 2-3 second delays between requests

### Image Analysis for Dynamic Adaptation
- **Brightness Calculation**: Analyze generated image RGB values
- **Threshold Detection**: Determine if image is predominantly light or dark
- **Color Scheme Selection**: Map to appropriate text panel color scheme
- **Cache Results**: Store analysis results to avoid repeated calculation

### Deployment Strategy
- **Static hosting** on existing DreamHost account
- **Rsync deployment** via GitHub Actions
- **Generated images** committed to repo for version control
- **Incremental updates** - only generate missing images

## Key Design Decisions Made

1. **Individual markdown files** over monolithic JSON (easier editing/version control)
2. **Reusable style library** over hardcoded prompts (consistency + efficiency)
3. **Right-sized structure** over enterprise complexity (maintainable for personal project)
4. **Nano Banana over alternatives** (best quality + reasonable cost)
5. **Static site over dynamic** (simple hosting + fast loading)
6. **GitHub Actions automation** (streamlined workflow)

## Testing Strategy

1. **Test locally first**: Run scripts manually to verify functionality
2. **Test with Paul Graham quote**: Use existing content as initial validation
3. **Test incremental generation**: Verify only new content generates images
4. **Test complete workflow**: Add new content → generate → build → verify
5. **Test error handling**: Missing styles, API failures, malformed content

## Success Criteria

✅ **Add new content**: Create markdown file → commit → automatic deployment  
✅ **Beautiful visuals**: AI-generated images match content mood and style  
✅ **Fast loading**: Site loads quickly with optimized images  
✅ **Mobile friendly**: Works well on phones and tablets  
✅ **Cost effective**: <$1 total for initial 20 pieces of content  
✅ **Maintainable**: Easy to understand and modify 6 months later

## Open Design Questions

1. **Image aspect ratio**: Square (1:1) or landscape (16:9) or portrait (9:16)?
2. **Content display**: Side-by-side or image background with text overlay?
3. **Collection organization**: Group by tags/themes or keep fully random?
4. **Social sharing**: Include social media meta tags and sharing buttons?
5. **Analytics**: Track which content is most popular?

## Updated Site Specification Summary

Based on research into Nano Banana best practices and abstract art approaches, here are the key insights for claude-code implementation:

### **Nano Banana Best Practices Discovered:**
1. **Descriptive Sentences Over Keywords**: "Describe the scene, don't just list keywords. A narrative, descriptive paragraph will almost always produce a better, more coherent image"
2. **Conversational Refinement**: "Use everyday language while creating images, and keep the conversation going to refine what the model generates"
3. **Emotional Language**: "Use descriptive sentences, not word salads" and include emotional cues
4. **World Knowledge Integration**: "Gemini's world knowledge unlocks new use cases" for contextual understanding

### **Abstract Art Approach:**
- **Focus on Sensation**: "Abstract art aims to evoke emotions, sensations, and ideas through non-representational images"
- **Color Field Emotion**: "Color Field painters believed that color alone could evoke deep, almost spiritual emotions"
- **Gestural Expression**: "Abstract Expressionism values raw emotion over structured form, often conveyed through bold brushstrokes"

### **Implementation Strategy:**
1. **Start with content parser** to combine markdown + style library
2. **Generate Paul Graham image** using "essence-of-desire" style 
3. **Build responsive site** with dynamic color adaptation
4. **Implement breathing animation** (10-20 second cycles)
5. **Test complete workflow** before GitHub Actions setup

### **Ready for claude-code Development:**
The comprehensive spec includes all technical requirements, content examples, and style library. The research validates that Nano Banana can handle abstract, emotional prompts effectively when properly structured.
