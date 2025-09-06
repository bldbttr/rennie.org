# Right-Sized Structure for rennie.org

## Directory Structure
```
rennie.org/
├── .github/workflows/          # GitHub Actions (essential)
│   └── generate-and-deploy.yml
│
├── bin/                        # Operational scripts (essential)
│   ├── setup.sh
│   ├── generate-new.sh         # Generate images for new content
│   ├── regenerate-all.sh       # Regenerate all images  
│   └── deploy.sh               # Deploy to DreamHost
│
├── content/                    # Content management (essential)
│   ├── inspiration/            # Individual content pieces
│   │   ├── paul-graham-make-something.md
│   │   ├── frost-road-not-taken.md
│   │   └── template.md         # Template for new content
│   │
│   └── styles/                 # Style library (high value)
│       ├── styles.json         # Reusable prompt templates
│       └── README.md           # Style guide
│
├── scripts/                    # Python utilities (essential)
│   ├── generate_images.py      # Nano Banana image generation
│   ├── build_site.py           # Static site generator
│   ├── content_parser.py       # Parse markdown content
│   └── requirements.txt
│
├── web/                        # Static web files (simple)
│   ├── index.html             # Main page template
│   ├── style.css              # Styles
│   ├── script.js              # Frontend logic
│   └── assets/                # Static assets
│       └── fonts/
│
├── generated/                  # Generated content (gitignored)
│   ├── images/
│   ├── content.json           # Processed content for web
│   └── manifest.json          # Generation metadata
│
├── output/                     # Deployable site (gitignored)
│   ├── index.html
│   ├── style.css
│   ├── script.js
│   └── images/
│
├── docs/                       # Essential documentation
│   ├── content-guide.md        # How to add new content
│   └── README.md
│
├── .env.example
├── .gitignore
└── README.md
```

## Content File Example (Simplified)
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
This quote from Paul Graham captures the essence of successful entrepreneurship...
```

## Style Library (Simple but Powerful)
```json
{
  "styles": {
    "modern-inspirational": {
      "base_prompt": "modern aesthetic, inspiring and uplifting, professional quality, warm lighting",
      "elements": ["startup office", "collaboration", "innovation"],
      "mood": "energetic and optimistic"
    },
    "classical-poetry": {
      "base_prompt": "romantic period painting style, classical composition, soft dreamy quality", 
      "elements": ["literary atmosphere", "timeless beauty"],
      "mood": "contemplative and serene"
    }
  }
}
```

## What We're Cutting vs. Keeping

### ✂️ **Cutting (Overkill)**
- Complex Python package structure → Simple scripts
- Frontend build process → Direct HTML/CSS/JS
- Multiple config files → Just .env
- Comprehensive logging → Basic print statements
- Full test suite → Manual testing
- Environment configs → Single production setup

### ✅ **Keeping (Right-Sized)**
- Individual content files → Better than monolithic JSON
- Style library → Saves time, creates consistency  
- Python scripts → Need automation anyway
- Bash scripts → Essential for workflow
- GitHub Actions → Core requirement
- Basic documentation → Self-explanatory project

## Complexity Scorecard

| Feature | Complex Version | Right-Sized | Benefit |
|---------|----------------|-------------|---------|
| Content | Backend package | Simple scripts | 🟢 Same outcome, less complexity |
| Styles | Multiple JSON files | Single styles.json | 🟢 Still reusable, much simpler |
| Frontend | Build process | Static files | 🟢 Zero build complexity |
| Config | Multiple files | .env only | 🟢 One place for settings |
| Docs | Comprehensive | Essential only | 🟢 Self-documenting structure |

## Why This Is Right-Sized

1. **Still Professional** - Proper structure without over-engineering
2. **Easy to Understand** - Anyone can figure out the layout quickly  
3. **Maintainable** - You can come back to this in 6 months and understand it
4. **Scalable** - Can easily add more content without restructuring
5. **Automatable** - GitHub Actions work great with this structure
6. **Flexible** - Easy to upgrade pieces later if needed

This gives you 80% of the benefits with 40% of the complexity.
