# Deployment Architecture: Lessons Learned

**Project**: rennie.org Inspiration Site  
**Date**: September 9, 2025  
**Status**: Working but over-engineered

## Executive Summary

We implemented a GitHub Actions CI/CD pipeline for a simple static site that displays 3 quotes with AI-generated images. While it works, it took ~4 hours to debug and is overkill for this project's scope. This document captures the tradeoffs and proposes a pragmatic path forward.

## What We Built

### Current Architecture (GitHub Actions CI/CD)
```
Push to GitHub → Actions Workflow → Parse → Generate Images → Build → Deploy to DreamHost
```

**Components:**
- GitHub Actions workflow (`deploy.yml`) 
- Python scripts for parsing, image generation, site building
- SSH deployment to DreamHost
- Automatic image generation with Nano Banana API
- Archive system for style changes

## Time Investment vs. Value

### Time Spent (~4 hours)
- 1 hour: Initial GitHub Actions setup
- 2 hours: Debugging content parser issues (single-file test mode bug)
- 30 min: SSH key configuration issues  
- 30 min: Path-based trigger confusion (scripts vs content)

### Value Delivered
- ✅ Push content → automatic deployment (when it works)
- ✅ Cost tracking for AI image generation
- ❌ Complex debugging when things break
- ❌ Can't easily see what's happening
- ❌ Overkill for 3 quotes

## Architecture Tradeoffs

### GitHub Actions Approach

**Pros:**
- Hands-off after setup
- "Best practice" for team projects
- Automatic image generation
- Git history of all changes
- No local dependencies needed

**Cons:**
- Complex to debug (can't see logs easily)
- Path-based triggers are fragile
- Caching makes verification difficult
- 15+ minute feedback loop for issues
- Total overkill for personal project

### Simpler Alternative (Local Scripts + Rsync)

**Pros:**
- Immediate feedback
- Full control and visibility
- 2-minute deployment
- Easy to debug
- Perfect for personal projects

**Cons:**
- Manual process
- Need local environment
- No automatic triggers

## Honest Assessment

**We over-engineered this.** For a personal site with 3 quotes that rarely changes, a simple bash script would have been sufficient:

```bash
# What we should have done (30 minutes total):
python parse.py && python generate.py && python build.py
rsync -avz output/ dreamhost:~/rennie.org/
```

Instead, we built enterprise-grade CI/CD for a weekend project. Classic developer behavior! 😅

## Proposed Path Forward

### Keep What We Have (For Now)
Since it's working, keep the GitHub Actions pipeline but set expectations:
- **Use for**: Adding new content occasionally
- **Don't use for**: Urgent updates or debugging
- **Escape hatch**: Local deployment script as backup

### Create Simple Fallback
Add `/bin/local-deploy.sh`:
```bash
#!/bin/bash
# Direct deployment when GitHub Actions is being difficult
source ~/dev/.venv/bin/activate
python scripts/content_parser.py
python scripts/generate_images.py --new-only  
python scripts/build_site.py
rsync -avz output/ rennie@iad1-shared-e1-05.dreamhost.com:~/rennie.org/
echo "✅ Deployed in 2 minutes (vs 15 with Actions)"
```

### When to Abandon GitHub Actions
Pull the plug if any of these happen:
1. Another 30+ minutes debugging deployment issues
2. Need to update more than once per week
3. Want to iterate quickly on design changes
4. SSH keys break again

## Lessons for Future Projects

1. **Start simple** - Basic scripts first, automation later
2. **Match complexity to project scope** - 3 quotes don't need CI/CD
3. **Local first** - Get it working locally before automating
4. **Time box architecture** - 30 min setup max for personal projects
5. **YAGNI applies to DevOps too** - You Aren't Gonna Need It

## The Bottom Line

We built a Ferrari to go to the corner store. It works, it's impressive, but a bicycle would have been fine. 

**Keep it for now** since we already paid the complexity tax, but next time: **start with the bicycle**.

---

*"Make something people want" - Paul Graham*  
*In this case, we made CI/CD that nobody wanted, including ourselves.* 🤷