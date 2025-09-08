# Inspiration Site Build Notes

**Project**: rennie.org Inspiration Site with AI-Generated Artwork  
**Build Date**: September 2025  
**Tech Stack**: Python scripts + Nano Banana (Gemini 2.5 Flash Image) + Static Site

## Phase 1: Content Parser ✅ COMPLETED

### Overview
Built `scripts/content_parser.py` to parse markdown files with YAML frontmatter and generate structured prompts for AI image generation.

### Key Achievements

**✅ YAML Frontmatter Parsing**
- Validates required fields: `title`, `author`, `type`, `style_approach`
- Handles optional fields: `source`, `tags`, `status`, `year`
- Graceful error handling for malformed files

**✅ Style Library Integration**
- Loads visual style definitions from `content/styles/styles.json`
- Supports both "scene" and "artistic" style categories
- Handles random style selection within categories
- 4 abstract artistic styles: `essence-of-desire`, `sensation-of-momentum`, `color-field-emotion`, `gestural-expression`

**✅ Personal Context Extraction**
- Parses "Why I Like It" and "What I See In It" sections
- Integrates personal interpretation into image prompts
- Enhances AI generation with emotional context

**✅ JSON-Structured Prompt Generation**
- Creates 903-character descriptive prompts (not keyword lists)
- Combines base style + personal context + mood elements + color palette
- Optimized for square 1:1 aspect ratio
- Follows Nano Banana best practices for narrative descriptions

### Test Results

**Input**: Paul Graham quote "Make something people want"
- **Style Applied**: "essence-of-desire" (artistic approach)
- **Generated Prompt**: 903 characters combining abstract expressionist concepts with personal interpretation
- **Output**: Structured JSON with complete prompt data for image generation

**Sample Prompt Structure**:
```
"Abstract expressionist composition conveying the essence of human desire and fulfillment, flowing organic forms suggesting connection between need and satisfaction, warm resonant colors that evoke joy and utility, emotional landscape rather than literal representation. Inspired by the feeling of: A person getting utility or joy from the experience the product brings to their life..."
```

### Files Created
- `scripts/content_parser.py` - Main parser logic (320 lines)
- `content/inspiration/paul-graham-make-something.md` - Test content
- `content/styles/styles.json` - Visual style library (130 lines)
- `generated/parsed_content.json` - Structured output

---

## Phase 2: Image Generator ✅ COMPLETED

### Overview
Built `scripts/generate_images.py` using Google's Nano Banana API (Gemini 2.5 Flash Image Preview) to generate AI artwork from structured content prompts.

### Key Achievements

**✅ Nano Banana API Integration**
- Uses `google.genai.Client` with `gemini-2.5-flash-image-preview` model
- Proper response handling with `inline_data` extraction
- Robust error handling and API response debugging

**✅ High-Quality Image Generation**
- Generated 1024x1024 PNG images (1.7MB file size)
- Perfect square format for responsive design
- Abstract art that captures emotional essence vs. literal interpretation

**✅ Incremental Generation Logic**
- Checks existing images to avoid duplicate generation
- `--force-all` flag for regeneration
- `--new-only` mode for efficient workflows

**✅ Complete Metadata Tracking**
- Generation timestamp and model used
- Full prompt text and character count
- Cost tracking ($0.039 per image)
- Image dimensions and file paths
- Success/failure status with detailed error info

**✅ Cost Management**
- Accurate cost calculation: $0.039 per 1024x1024 image
- Total cost tracking across generation sessions
- Rate limiting with 2-second delays between requests

### Test Results

**Generated Image**: `paul_graham_make_something_people_want.png`
- **Dimensions**: 1024x1024 pixels
- **File Size**: 1.7MB PNG
- **Style**: Abstract expressionist spiral with flowing organic forms
- **Colors**: Warm golden energy, deep satisfying blues, life-affirming oranges
- **Mood**: Captures "essence of desire and fulfillment" perfectly
- **Cost**: $0.039
- **Generation Time**: ~5 seconds

**Visual Quality Assessment**:
- ✅ **Abstract vs. Literal**: Successfully avoided literal startup office scenes
- ✅ **Emotional Resonance**: Flowing spiral suggests connection between need and satisfaction
- ✅ **Color Psychology**: Warm golds and blues evoke joy and utility
- ✅ **Composition**: Centered spiral with organic forms, perfect square format
- ✅ **Artistic Style**: True abstract expressionist approach

### API Evolution
- **Initial Attempt**: Used `google.generativeai` with `gemini-2.0-flash-exp-image-generation` (deprecated)
- **Final Solution**: Migrated to `google.genai.Client` with `gemini-2.5-flash-image-preview`
- **Key Learning**: New client library required for proper image data extraction

### Files Created
- `scripts/generate_images.py` - Main generator (310 lines)
- `generated/images/paul_graham_make_something_people_want.png` - Test image
- `generated/metadata/paul_graham_make_something_people_want_metadata.json` - Generation metadata
- `generated/generation_summary.json` - Session summary

---

## Technical Specifications Validated

### Content Format ✅
- YAML frontmatter with required fields working
- Markdown section parsing for personal context
- Style approach categorization (scene vs. artistic)

### API Integration ✅
- Model: `gemini-2.5-flash-image-preview`
- Cost: $0.039 per 1024x1024 image (validated)
- Output: PNG format, base64 decoded properly
- Rate limiting: 2-3 second delays implemented

### Prompt Engineering ✅
- 903-character descriptive sentences (not keywords)
- Emotional language with personal context integration
- Art movement terminology (Abstract Expressionism)
- Square composition optimization

### File Structure ✅
```
content/
├── inspiration/
│   └── paul-graham-make-something.md ✅
└── styles/
    └── styles.json ✅

generated/
├── images/
│   └── paul_graham_make_something_people_want.png ✅
├── metadata/
│   └── paul_graham_make_something_people_want_metadata.json ✅
├── parsed_content.json ✅
└── generation_summary.json ✅

scripts/
├── content_parser.py ✅
└── generate_images.py ✅
```

---

## Next Phase: Site Builder

### Ready for Phase 3
With content parsing and image generation complete, Phase 3 will build:

1. **Static Site Generator** (`scripts/build_site.py`)
   - Single-page app with random content display
   - Responsive HTML/CSS/JS
   - JSON API endpoint for content

2. **Frontend Components** (`web/`)
   - `index.html` - Homepage template
   - `style.css` - Modern, clean aesthetic  
   - `script.js` - Random selection and smooth transitions

3. **Deployment Automation** (`bin/`)
   - Bash scripts for common operations
   - GitHub Actions workflow
   - DreamHost deployment pipeline

### Current Status
- **Content Pipeline**: Fully functional end-to-end
- **Cost Validation**: $0.039 per image confirmed
- **Quality Assurance**: Abstract art approach validated
- **Technical Foundation**: Solid Python infrastructure ready for site building

**Total Development Time**: Phase 1 + Phase 2 = ~2 hours  
**Total Cost**: $0.039 for test image generation