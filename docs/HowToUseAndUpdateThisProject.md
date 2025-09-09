# How To Use and Update This Inspiration Site

**Quick Reference:** This site generates AI artwork for inspirational quotes using a hybrid local-first workflow. You preview everything locally before deployment.

## 🚀 Quick Start Commands

```bash
# Check image status for all content
./bin/check-images.sh

# Generate images + preview locally
./bin/generate-new-images-locally.sh

# Deploy to production
./bin/commit-and-deploy.sh
```

---

## Scenario 1: Adding New Inspirational Content

### Step 1: Create Content File

Create a new markdown file in `content/inspiration/`:

```bash
# Example: content/inspiration/einstein-imagination.md
---
title: "Imagination is more important than knowledge"
author: "Albert Einstein"
type: "quote"
source: "https://example.com/source"
style_category: "random"  # or "visual_storytelling" or "painting_technique"
style_specific: "random"  # or specific style name like "monet-impressionist"
vibe: ["wonder", "curiosity"]
status: "active"
---

Imagination is more important than knowledge.

## Why I Like It
This quote captures the essence of creative thinking...
```

### Step 2: Preview and Generate Images

```bash
# This will:
# - Analyze what images are needed
# - Show cost estimate (usually ~$0.12 for 3 variations)
# - Ask for your approval
# - Generate images locally
# - Build the site
# - Open preview in your browser
./bin/generate-new-images-locally.sh
```

**Expected output:**
```
🧮 CALCULATING IMAGE GENERATION NEEDS
=====================================
📊 Content pieces: 4
🖼️  Existing images: 10

💰 COST ANALYSIS
================
🆕 New images: 1 content pieces × 3 variations = 3 images
   Cost: $0.12

🤔 APPROVAL REQUIRED
===================
Generate 3 images for approximately $0.12?
   • 3 new images for missing content

Proceed with generation? (yes/no): yes
```

### Step 3: Review and Deploy

1. **Review the preview** that opens in your browser
2. **Check all variations** - each piece gets 3 image variations 
3. **If satisfied**, deploy:

```bash
./bin/commit-and-deploy.sh
```

This commits your content + images and triggers automatic deployment to rennie.org.

---

## Scenario 2: Updating Visual Styles

### Background: Understanding Styles

The site has two style categories:
- **`visual_storytelling`**: Cinematic techniques (Ghibli, Arcane, Spider-Verse, etc.)
- **`painting_technique`**: Art styles (Turner, Rothko, Monet, Kline)

### Step 1: Get Style Ideas (Optional but Recommended)

**Tip:** Discuss with Claude (claude.ai) to explore style options:

> *"I'm updating the visual styles for my inspiration site. The current content is about [your topic]. What visual storytelling or painting technique would capture the mood of [feeling/concept]? I have styles like monet-impressionist, kline-gestural, ghibli-composition, spiderverse-dimensional..."*

Claude can suggest which existing styles fit your content or propose new ones.

### Step 2: Update Content Files

Edit the frontmatter in your content files:

```yaml
# Before:
style_specific: "random"

# After:
style_specific: "kline-gestural"  # or whatever style you chose
```

### Step 3: Add New Styles (If Needed)

If you want a completely new style, add it to `content/styles/styles.json`:

```json
{
  "painting_technique_styles": {
    "your-new-style": {
      "description": "Brief description of the artistic approach",
      "base_prompt": "Detailed prompt for the AI describing the visual technique...",
      "key_techniques": ["technique1", "technique2"],
      "color_philosophy": "Approach to color and mood"
    }
  }
}
```

### Step 4: Preview Changes

```bash
./bin/generate-new-images-locally.sh
```

**Expected output for style changes:**
```
🔄 Content needing image updates:
   • "Make something people want" by Paul Graham (random → kline-gestural)
   • "Customer experience first" by Steve Jobs (monet-impressionist → ghibli-composition)

💰 COST ANALYSIS
================
🔄 Updated images: 2 content pieces × 3 variations = 6 images
   Cost: $0.23

🤔 APPROVAL REQUIRED
===================
Generate 6 images for approximately $0.23?
   • 6 updated images for style changes
```

**Note:** Style changes will archive your old images to `generated/archive/[timestamp]/` before generating new ones.

### Step 5: Deploy

```bash
./bin/commit-and-deploy.sh
```

---

## Scenario 3: Redeploying the Site (HTML/CSS/JS Changes)

If you've modified the site's code, styles, or layout (files in `scripts/build_site.py`, etc.):

### For Code-Only Changes (No Images)

```bash
# Just rebuild and deploy
python scripts/build_site.py
./bin/commit-and-deploy.sh
```

### If You Want to Regenerate Everything

```bash
# Force regenerate all images + rebuild
./bin/regenerate-all.sh
python scripts/build_site.py
./bin/commit-and-deploy.sh
```

**Warning:** `regenerate-all.sh` will cost ~$0.12 per content piece (so ~$0.36 for 3 pieces).

---

## 🔍 Troubleshooting & Tips

### Check What Needs Updating

```bash
# See image status inventory by content file
./bin/check-images.sh
```

### Understanding the Output

- **🆕 New images**: Missing images for new content
- **🔄 Updated images**: Existing images that need regeneration due to style changes
- **Cost**: Each image costs ~$0.039 (3 variations = ~$0.12 per content piece)

### If Generation Fails

1. **Check API key**: Make sure `GEMINI_API_KEY` is set
2. **Check internet**: Image generation requires API access
3. **Check content format**: Ensure YAML frontmatter is valid

### Viewing Generated Images Locally

Images are saved to `generated/images/` and are now tracked in git. You can browse them directly or view them integrated in the site preview.

### Archive System

Old images are automatically moved to `generated/archive/[timestamp]/` when styles change, so you never lose previous generations.

---

## 🎯 Quick Decision Guide

**I want to...** | **Command**
---|---
Add new quote/content | Create `.md` file → `./bin/generate-new-images-locally.sh` → `./bin/commit-and-deploy.sh`
Change visual styles | Edit frontmatter → `./bin/generate-new-images-locally.sh` → `./bin/commit-and-deploy.sh` 
Check image status by file | `./bin/check-images.sh`
Just rebuild site | `python scripts/build_site.py` → `./bin/commit-and-deploy.sh`
Nuclear option (regenerate all) | `./bin/regenerate-all.sh` → `./bin/commit-and-deploy.sh`

---

## 🔄 The Philosophy

This system follows a **hybrid local-first approach**:

- **Generate locally**: See your images immediately, know exactly what will be deployed
- **Deploy automatically**: GitHub Actions handles the production deployment
- **Cost transparency**: Always know what generation will cost before proceeding
- **Version control**: All images are tracked in git for consistency

**The key insight:** You see locally what gets deployed remotely. No more "git pull to see your images" nonsense!

---

## 🛟 Getting Help

- **Style questions**: Ask Claude at claude.ai about visual approaches
- **Technical issues**: Check `generated/generation_summary.json` for error details
- **Site not updating**: Verify deployment at github.com/bldbttr/rennie.org/actions