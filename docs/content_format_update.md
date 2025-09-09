# Content Format & Code Update Guide

## Updated Markdown Format

**New Simplified Format:**
```yaml
---
title: "Make something people want"
author: "Paul Graham"
type: "quote"
source: "https://paulgraham.com/good.html"
style_approach: "painting_technique"  # or "visual_storytelling"
style: "random"  # or specific style name like "turner-atmospheric"
vibe: ["anticipation", "clarity", "desire"]  # 1-3 words max
status: "active"
---

Make something people want.

## Why I Like It  
PG's wisdom resonates with me. This is the best single encapsulation of a startup or product mission I have come across. I try to challenge myself with this constantly.
```

**Key Changes:**
- **Removed:** `What I See In It` section (replaced with `vibe`)
- **Added:** `vibe` field with 1-3 emotional/atmospheric words
- **Kept:** `Why I Like It` for website context (not used in prompts)
- **Updated:** Style names to match new styles.json structure

## Style Approach Values

- `painting_technique`: Uses Turner, Kline, Rothko, Monet approaches
- `visual_storytelling`: Uses Ghibli, Arcane, Kibuishi, Spider-Verse approaches

## Valid Style Names

**Painting Technique Styles:**
- `turner-atmospheric`
- `kline-gestural` 
- `rothko-color-field`
- `monet-impressionist`

**Visual Storytelling Styles:**
- `ghibli-composition`
- `arcane-framing`
- `kibuishi-world`
- `spiderverse-dimensional`

## Common Vibe Words

**Emotional States:**
anticipation, clarity, flow, recognition, wonder, intensity, serenity, energy, contemplation, discovery

**Atmospheric Qualities:**
luminous, dynamic, ethereal, bold, gentle, dramatic, mystical, vibrant, peaceful, explosive

## Code Changes Required

### 1. Update content_parser.py

**Modified `_parse_sections` method:**
```python
def _parse_sections(self, markdown: str) -> Dict[str, str]:
    """Parse markdown content into sections."""
    sections = {}
    
    # Split by ## headers
    parts = re.split(r'^## ', markdown, flags=re.MULTILINE)
    
    # First part is main content
    if parts[0]:
        sections['main'] = parts[0].strip()
    
    # Process remaining sections
    for part in parts[1:]:
        lines = part.split('\n', 1)
        if lines:
            header = lines[0].strip().lower()
            content = lines[1].strip() if len(lines) > 1 else ''
            
            # Normalize section names
            if 'why i like it' in header:
                sections['why_i_like_it'] = content
            # Remove what_i_see_in_it handling
            else:
                sections[header.replace(' ', '_')] = content
    
    return sections
```

**Modified `get_style_data` method:**
```python
def get_style_data(self, style_name: str, style_approach: str) -> Dict[str, Any]:
    """Get the complete style data for a given style name."""
    # Check in the appropriate style collection based on approach
    if style_approach == 'painting_technique':
        styles = self.styles_data.get('painting_technique_styles', {})
    elif style_approach == 'visual_storytelling':
        styles = self.styles_data.get('visual_storytelling_techniques', {})
    else:
        # Try both
        styles = {**self.styles_data.get('painting_technique_styles', {}),
                 **self.styles_data.get('visual_storytelling_techniques', {})}
    
    return styles.get(style_name, {})
```

**Modified `_get_random_style` method:**
```python
def _get_random_style(self, style_approach: str) -> str:
    """Get a random style from the specified category."""
    categories = self.styles_data.get('style_categories', {})
    
    if style_approach in categories:
        styles = categories[style_approach].get('styles', [])
        return random.choice(styles) if styles else 'turner-atmospheric'
    
    # Default fallback
    return 'turner-atmospheric'
```

**Modified `generate_prompt` method:**
```python
def generate_prompt(self, parsed_content: Dict[str, Any]) -> Dict[str, Any]:
    """Generate a structured prompt for Nano Banana API."""
    frontmatter = parsed_content['frontmatter']
    
    # Select and get style
    style_approach = frontmatter.get('style_approach', 'painting_technique')
    style_name = self.select_style(style_approach, frontmatter.get('style'))
    style_data = self.get_style_data(style_name, style_approach)
    
    # Build the prompt components
    prompt_parts = []
    
    # Start with base prompt from style
    if 'base_prompt' in style_data:
        prompt_parts.append(style_data['base_prompt'])
    
    # Add vibe guidance if available
    if frontmatter.get('vibe'):
        vibes = frontmatter['vibe']
        if isinstance(vibes, list):
            vibe_text = ', '.join(vibes)
        else:
            vibe_text = str(vibes)
        prompt_parts.append(f"Capturing the vibe of {vibe_text}")
    
    # Always add square format optimization
    prompt_parts.append("square composition, centered focus, 1:1 aspect ratio")
    
    # Join all parts into a flowing prompt
    full_prompt = ". ".join(prompt_parts)
    
    # Create structured output
    return {
        'content_file': parsed_content['file_path'],
        'title': frontmatter.get('title'),
        'author': frontmatter.get('author'),
        'type': frontmatter.get('type'),
        'quote_text': parsed_content['content'],
        'style_name': style_name,
        'style_approach': style_approach,
        'style_data': style_data,
        'vibe': frontmatter.get('vibe', []),
        'prompt': {
            'text': full_prompt,
            'components': {
                'base': style_data.get('base_prompt', ''),
                'vibe': frontmatter.get('vibe', []),
                'format': 'square composition, centered focus, 1:1 aspect ratio'
            }
        },
        'metadata': {
            'source': frontmatter.get('source'),
            'status': frontmatter.get('status', 'active'),
            'tags': frontmatter.get('tags', []),
            'why_i_like_it': parsed_content['why_i_like_it']
        }
    }
```

### 2. Update generate_images.py

**Modified variation generation logic:**
```python
# In generate_variations method, update the style category references:

# Get available styles
painting_styles = list(parser.styles_data.get('painting_technique_styles', {}).keys())
storytelling_styles = list(parser.styles_data.get('visual_storytelling_techniques', {}).keys())

# Update the variation logic:
elif variation_num == 2:
    # Variation 2: Random style from same category
    if original_approach == 'painting_technique':
        available = [s for s in painting_styles if s != original_style]
        style_name = random.choice(available) if available else original_style
    else:
        available = [s for s in storytelling_styles if s != original_style]
        style_name = random.choice(available) if available else original_style
    style_approach = original_approach
    variation_type = "same_category"
else:
    # Variation 3+: Random style from opposite category
    if original_approach == 'painting_technique':
        style_name = random.choice(storytelling_styles) if storytelling_styles else original_style
        style_approach = 'visual_storytelling'
    else:
        style_name = random.choice(painting_styles) if painting_styles else original_style
        style_approach = 'painting_technique'
    variation_type = "opposite_category"
```

## Updated Content Files

### paul-graham-make-something.md
```yaml
---
title: "Make something people want"
author: "Paul Graham"
type: "quote"
source: "https://paulgraham.com/good.html"
style_approach: "painting_technique"
style: "random"
vibe: ["desire", "clarity"]
status: "active"
---

Make something people want.

## Why I Like It  
PG's wisdom resonates with me. This is the best single encapsulation of a startup or product mission I have come across. I try to challenge myself with this constantly.
```

### pmarca-pmf.md
```yaml
---
title: "You can always feel product/market fit when it's happening"
author: "Marc Andreessen"
type: "quote"
source: "https://pmarchive.com/guide_to_startups_part4.html"
style_approach: "painting_technique"
style: "random"
vibe: ["recognition", "flow"]
status: "active"
---

...And you can always feel product/market fit when it's happening.

## Why I Like It
Timeless insight. First piece that describes the mission of building, and captures the feeling when it's working and when it's not, without listing a metric. I re-read it a couple times a year.
```

### steve-jobs-customer-experience-back-to-technology.md
```yaml
---
title: "Start with the customer experience and work backwards to the technology"
author: "Steve Jobs"
type: "quote"
source: "https://youtu.be/oeqPrUmVz-o?t=112"
style_approach: "visual_storytelling"
style: "random"
vibe: ["clarity", "revelation"]
status: "active"
---

You've gotta start with the customer experience and work backwards to the technology.

## Why I Like It
Masterful clarity, inspiration and motivation. This encapsulates the entire philosophy of great product development - understanding what people actually need and want.
```

## Implementation Steps

1. **Update styles.json** (already done in previous artifact)
2. **Update content_parser.py** with the code changes above
3. **Update generate_images.py** with the style category name changes
4. **Update existing .md files** with new format (remove "What I See In It" sections, add vibe fields)
5. **Test the pipeline** with one file first
6. **Archive existing images** if you want fresh generations with new prompts

## Benefits of This Approach

- **Faster content creation**: Just pick 1-3 vibe words instead of writing interpretative text
- **Cleaner prompts**: Pure artistic style + simple emotional direction
- **Better separation**: Website context ("Why I Like It") stays separate from image generation
- **Consistent workflow**: Every content piece follows the same simple pattern
- **Easy expansion**: Adding new quotes is now a 2-minute task
