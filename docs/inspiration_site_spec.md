# Inspiration Site Development Specification
**Project**: rennie.org Inspiration Site with AI-Generated Artwork  
**Repository**: https://github.com/bldbttr/rennie.org  
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

## Current Status (Complete - Production Ready)

✅ **Repository Structure**: Complete directory structure implemented  
✅ **Git Setup**: Repository live at github.com/bldbttr/rennie.org  
✅ **Nano Banana API**: Production-ready (API key configured in .env and GitHub secrets)
✅ **Content Library**: 3 inspirational quotes with 9 AI-generated artwork variations  
✅ **Style Library**: Comprehensive visual style definitions with 8 distinct styles  
✅ **Core Scripts**: All Python automation scripts completed and tested  
✅ **Static Site**: Responsive web interface with sophisticated carousel functionality  
✅ **GitHub Actions**: Complete CI/CD pipeline operational  
✅ **Multi-Variations**: 3 AI image variations per content piece  
✅ **Hybrid Workflow**: Local-first development with automated deployment  
✅ **Production Site**: Live at https://rennie.org  
✅ **Image Carousel**: Complete carousel with Ken Burns effects, touch gestures, fade transitions, and full keyboard controls
✅ **Polish Features**: Escape key pause, style synchronization, cinematic transitions, 30-second immersive experiences

🚀 **Project Status**: Complete and production ready - exceeds initial specifications with gallery-quality user experience

## Directory Structure

```
rennie.org/
├── .github/workflows/         # GitHub Actions ✅
│   └── deploy.yml            # Automated deployment pipeline ✅
├── bin/                      # Bash automation scripts ✅
│   ├── generate-new-images-locally.sh  # Main hybrid local-first workflow ✅
│   ├── preview-local.sh      # Local HTTP server for CORS-free preview ✅
│   ├── commit-and-deploy.sh  # Streamlined deployment ✅
│   ├── check-images.sh       # Image status inventory ✅
│   └── cleanup-images.sh     # Remove orphaned images ✅
├── content/
│   ├── inspiration/          # Individual content pieces ✅
│   │   ├── paul-graham-make-something.md ✅
│   │   ├── pmarca-pmf.md ✅
│   │   └── steve-jobs-customer-experience-back-to-technology.md ✅
│   └── styles/              # Visual style library ✅
│       └── styles.json ✅    # 8 distinct AI art styles
├── scripts/                 # Python automation ✅
│   ├── content_parser.py ✅  # Markdown + YAML processing
│   ├── generate_images.py ✅ # Nano Banana integration
│   ├── build_site.py ✅      # Static site generator
│   └── read_config.py ✅     # Configuration utility for bash scripts
├── generated/               # AI-generated content (now tracked in git) ✅
│   ├── images/             # 3 variations per content piece ✅
│   ├── metadata/           # Generation tracking ✅
│   └── archive/            # Previous generations ✅
├── output/                  # Final deployable site ✅
│   ├── index.html ✅        # Responsive SPA
│   ├── style.css ✅         # Modern styling
│   ├── script.js ✅         # Dynamic functionality
│   └── content.json ✅      # API endpoint
├── config.json ✅            # Centralized configuration ✅
└── docs/                    # Documentation ✅
    ├── HowToUseAndUpdateThisProject.md ✅  # User guide
    ├── inspiration_site_spec.md ✅         # Technical spec
    └── workflow_architecture_analysis.md ✅ # Architecture decisions
```

## Implementation Summary ✅

All development phases have been completed successfully. The project now features a hybrid local-first workflow that solved the original architecture issues.

### Core Python Scripts ✅ COMPLETED

#### 1. Content Parser (`scripts/content_parser.py`) ✅
**Achievements**:
- ✅ Complete YAML frontmatter parsing with validation
- ✅ Sophisticated style library integration with 8 distinct styles
- ✅ Support for `style_category` and `style_specific` fields
- ✅ Random style selection within categories
- ✅ Personal context extraction from markdown sections
- ✅ Structured JSON output with complete prompt data
- ✅ Robust error handling for malformed content

#### 2. Image Generator (`scripts/generate_images.py`) ✅
**Achievements**:
- ✅ Google Gemini 2.5 Flash Image API integration
- ✅ Multi-variation generation (3 images per content piece)
- ✅ Smart change detection comparing metadata vs current content
- ✅ Incremental generation with `--new-only` flag
- ✅ Archive system for style changes (`--archive-and-regenerate`)
- ✅ Complete metadata tracking with timestamps and costs
- ✅ Style comparison intelligence for detecting updates needed
- ✅ Cost transparency: $0.039 per image, $0.117 per content piece

#### 3. Site Builder (`scripts/build_site.py`) ✅
**Achievements**:
- ✅ Responsive single-page application generator
- ✅ Dynamic image selection from multiple variations
- ✅ JSON API endpoint with complete content metadata
- ✅ Brightness analysis for dynamic text color schemes
- ✅ Mobile-first responsive design
- ✅ Modern CSS with breathing animations
- ✅ Graceful handling of missing images

### Bash Automation Scripts ✅ COMPLETED

#### 1. Hybrid Local-First Workflow (`bin/generate-new-images-locally.sh`) ✅
**Purpose**: Main workflow script with intelligent change detection and cost control
**Features**:
- ✅ Sophisticated change detection using existing metadata comparison
- ✅ Cost estimation with detailed breakdown (new vs updated images)
- ✅ User approval workflow for all generation (no automatic spending)
- ✅ Local preview with immediate visual feedback
- ✅ Integration with archive system for style changes
- ✅ Verbose progress reporting and status updates

#### 2. Streamlined Deployment (`bin/commit-and-deploy.sh`) ✅
**Purpose**: Commit locally generated images and trigger automated deployment
**Features**:
- ✅ Verification of locally generated images before commit
- ✅ Custom commit messages with deployment context
- ✅ GitHub Actions trigger for production deployment
- ✅ Deployment status monitoring guidance

#### 3. Image Status Inventory (`bin/check-images.sh`) ✅
**Purpose**: Display inventory of image status by content file
**Features**:
- ✅ Shows status per content/inspiration/ file: needs new, needs update, or ✅ current
- ✅ Clear indication of what action is needed for each file
- ✅ Cost-free status check and planning tool
- ✅ Integration with content parser for up-to-date analysis

#### 4. Local Preview Server (`bin/preview-local.sh`) ✅
**Purpose**: Local HTTP server for CORS-free development preview
**Features**:
- ✅ Serves at http://localhost:8000 with working content loading
- ✅ Automatic Python 3/2 fallback
- ✅ Professional development workflow
- ✅ No more "Failed to load inspiration content" errors

#### 5. Image Management Scripts ✅
- `bin/cleanup-images.sh` - Remove orphaned images (for deleted content or reduced variations) ✅

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

### Deployment Strategy ✅ IMPLEMENTED
- **Hybrid Local-First Workflow**: Generate and preview locally, deploy automatically
- **Static hosting** on DreamHost with automated rsync deployment
- **Generated images** committed to repository for consistency guarantee
- **GitHub Actions CI/CD** for automated production deployment
- **Change detection intelligence** comparing metadata vs current content
- **Cost control** with user approval for all image generation
- **Archive system** preserving old images when styles change
- **Centralized configuration** eliminating hardcoded parameters throughout codebase

## Configuration Management ✅ IMPLEMENTED

The system uses a centralized `config.json` file to manage all system settings, eliminating hardcoded parameters and enabling easy customization.

### Configuration Structure
```json
{
  "image_generation": {
    "variations_per_content": 3,
    "cost_per_image": 0.039,
    "model": "gemini-2.5-flash"
  },
  "project": {
    "name": "rennie.org inspiration site",
    "version": "1.0"
  }
}
```

### Integration Architecture
- **Python Scripts**: `load_config()` utility with fallback defaults
- **Bash Scripts**: `scripts/read_config.py` utility for config value access
- **Cost Calculations**: All financial displays use actual configured values
- **Variations Management**: Easily change from 3 to any number of variations per content piece

### User Benefits
- **Single Edit Point**: Change variations system-wide by editing one file
- **Cost Transparency**: Accurate cost calculations based on current configuration
- **Easy Customization**: Well-documented configuration options with examples
- **Professional Maintainability**: Eliminates hardcoded parameter scattered throughout codebase

## Key Design Decisions Made ✅ VALIDATED

1. **Individual markdown files** over monolithic JSON (easier editing/version control) ✅
2. **Reusable style library** over hardcoded prompts (consistency + efficiency) ✅
3. **Right-sized structure** over enterprise complexity (maintainable for personal project) ✅
4. **Nano Banana over alternatives** (best quality + reasonable cost) ✅
5. **Static site over dynamic** (simple hosting + fast loading) ✅
6. **GitHub Actions automation** (streamlined workflow) ✅
7. **Hybrid local-first workflow** over pure cloud-first CI/CD (immediate feedback + deployment confidence) ✅
8. **Metadata-based change detection** over simple file existence checks (intelligent updates) ✅
9. **Multi-variation generation** over single images (visual variety and user engagement) ✅
10. **Cost transparency with user approval** over automatic spending (budget control) ✅
11. **Centralized configuration system** over hardcoded parameters (professional maintainability) ✅

## Testing Strategy

1. **Test locally first**: Run scripts manually to verify functionality
2. **Test with Paul Graham quote**: Use existing content as initial validation
3. **Test incremental generation**: Verify only new content generates images
4. **Test complete workflow**: Add new content → generate → build → verify
5. **Test error handling**: Missing styles, API failures, malformed content

## Success Criteria ✅ ALL ACHIEVED

✅ **Add new content**: Create markdown file → preview locally → commit → automatic deployment  
✅ **Beautiful visuals**: AI-generated images with 3 variations per content piece match mood and style  
✅ **Fast loading**: Responsive site loads quickly with optimized 1024x1024 images  
✅ **Mobile friendly**: Responsive design works beautifully on phones and tablets  
✅ **Cost effective**: $0.117 per content piece (3 images), transparent cost control  
✅ **Maintainable**: Well-documented with user guide and architectural analysis  
✅ **Instant feedback**: See your creative work immediately before deployment  
✅ **Production confidence**: Same images locally and in production (no surprises)  
✅ **Change detection**: Smart system detects content and style changes automatically  
✅ **Archive preservation**: Old images preserved when styles change

## Design Questions ✅ RESOLVED

1. **Image aspect ratio**: Square (1:1) ✅ - Chosen for optimal responsive display
2. **Content display**: Full-screen background with text overlay ✅ - Immersive experience
3. **Collection organization**: Fully random ✅ - Maintains surprise and discovery
4. **Social sharing**: Not implemented - Focus on personal inspiration over sharing
5. **Analytics**: Not implemented - Privacy-focused, distraction-free experience

## Critical Maintenance Patterns ⚠️ DOCUMENTED

### HTML/JavaScript Element ID Synchronization
**Recurring Issue**: Template refactoring breaks DOM element references, causing silent failures.

**Pattern**: HTML template (`scripts/templates/index.html`) uses `id="content-info"`, JavaScript (`scripts/templates/app.js`) references `getElementById('style-info')` → null element → functionality breaks silently.

**Affected Feature**: Carousel style synchronization - style info only updates with quote changes, not image variations.

**Prevention**: Always update HTML element IDs and corresponding JavaScript references together during template refactoring. Add console warnings for missing DOM elements during development.

**Quick Fix**: Verify element ID consistency between HTML templates and JavaScript DOM queries when carousel navigation works but style display doesn't update.

## Current Live Status ✅

- **Production Site**: https://rennie.org ✅
- **Content Library**: 3 inspirational pieces with 9 total image variations ✅
- **Deployment**: Fully automated via GitHub Actions ✅
- **Workflow**: Hybrid local-first with streamlined bin directory ✅
- **Local Preview**: CORS-free development server ✅
- **Documentation**: Complete user guide and technical specifications ✅

## Recommended Next Steps

1. **Content Expansion**: Add more inspirational quotes using the established workflow
2. **Style Exploration**: Experiment with new visual styles in collaboration with Claude
3. **Archive Review**: Periodically review archived images for potential restoration
4. **Performance Monitoring**: Monitor site performance as content library grows
5. **Backup Strategy**: Consider periodic backups of the complete generated content

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
