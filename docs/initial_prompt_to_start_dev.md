# Inspiration Site Development - Phase 1: Content Parser

## Project Context
Building a personal inspiration homepage for rennie.org that displays quotes/poems with AI-generated abstract artwork using Google's Nano Banana (Gemini 2.5 Flash Image).

## Documentation Available
All specifications are in the `docs/` directory:
- `inspiration_site_spec.md` - Complete technical requirements and architecture
- `visual_style_library.json` - Community-validated Nano Banana techniques  
- `inspiration_content_template.md` - Content structure and examples

## Current Setup
- Repository: https://github.com/bldbttr/rennie.org (live and connected)
- API: Nano Banana working (key: AIzaSyCh41VaooU6xexjq7zndc7FSNOh2Sg4-EE)
- Test content: Paul Graham quote ready in `content/inspiration/`
- Directory structure in place

## Phase 1 Task: Build Content Parser
**File to create**: `scripts/content_parser.py`

**What it needs to do**:
1. Parse markdown files with YAML frontmatter (see template in docs)
2. Load style library from `content/styles/styles.json` 
3. Handle new template structure (style_approach, style arrays, personal sections)
4. Generate JSON-structured prompts for Nano Banana (technique in docs)
5. Support "random" style selection within categories
6. Output structured data for image generation pipeline

**Key implementation notes from research**:
- Use JSON prompting approach (details in visual_style_library.json)
- Extract "Why I Like It" and "What I See In It" sections for prompt enhancement
- Support both "scene" and "artistic" style categories
- Handle edge cases gracefully

**Test case**: Parse `content/inspiration/paul-graham-make-something.md` and generate structured output with "essence-of-desire" style.

**Next phases**: After parser works, build image generator, then site builder, then deployment automation.

All technical details, requirements, and examples are in the docs/ directory - refer to those for complete specifications.
