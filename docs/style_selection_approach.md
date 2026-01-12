# Style Selection Approach

**Last Updated:** January 2026
**Current System:** Even Distribution with Random Assignment

## Overview

The image generation system uses an **even distribution** approach to ensure all 7 visual styles are represented fairly across the 15 total images (5 content pieces × 3 variations each).

## Style Inventory (7 Total)

### Visual Storytellers (5)
1. **ghibli-composition** - Studio Ghibli wide landscapes
2. **spiderverse-dimensional** - Spider-Verse mixed animation
3. **arcane-framing** - Fortiche/Arcane dramatic close-ups
4. **kibuishi-world** - Kazu Kibuishi architectural detail
5. **nolan-cinematic** - Christopher Nolan cinematic realism

### Painters (2)
6. **monet-impressionist** - Claude Monet broken brushwork
7. **turner-atmospheric** - J.M.W. Turner luminous atmosphere

## Selection Algorithm

### Current: Even Distribution (Recommended)

**Goal:** Ensure each style appears 2-3 times across all 15 images

**Implementation:**
```python
# Create balanced deck of 15 style cards
style_deck = []
for style in all_7_styles:
    style_deck.append(style)  # Add once (7 total)
    style_deck.append(style)  # Add twice (14 total)
style_deck.append(random.choice(all_7_styles))  # Add one more (15 total)

# Shuffle the deck
random.shuffle(style_deck)

# Deal 3 cards to each content piece
for content_piece in range(5):
    variation_1 = style_deck.pop()
    variation_2 = style_deck.pop()
    variation_3 = style_deck.pop()
```

**Result:**
- Every style appears at least 2 times
- One random style appears 3 times
- Styles randomly assigned to content pieces
- No duplicates within a content piece's 3 variations

**Example Distribution:**
- Ghibli: 2 times (guaranteed)
- Spiderverse: 3 times (got the extra)
- Arcane: 2 times
- Kibuishi: 2 times
- Nolan: 2 times
- Monet: 2 times
- Turner: 2 times

### Previous: Pure Random (Deprecated)

**Problem:** Resulted in uneven distribution (e.g., Arcane 4x, Ghibli 1x, Turner 0x)

**Why Changed:** User feedback that favorite styles (like Ghibli) were underrepresented with pure randomness.

## Content File Configuration

In content frontmatter:
```yaml
style_category: "random"  # Deprecated - system ignores this
style_specific: "random"  # Deprecated - system ignores this
```

These fields are maintained for backwards compatibility but no longer influence style selection. The even distribution algorithm handles all style assignment.

## Benefits of Even Distribution

1. **Fair Representation:** Every style appears proportionally
2. **Variety:** Still random which content gets which styles
3. **No Gaps:** No style is left out (Turner won't be 0)
4. **User Satisfaction:** Favorite styles guaranteed to appear multiple times
5. **Predictable Costs:** Always generates exactly 15 images

## Statistical Analysis

**With 7 styles and 15 images:**
- Perfect even: 15/7 = 2.14 images per style
- Implementation: 6 styles get 2 images, 1 style gets 3 images
- Variance: Much lower than pure random (σ² ≈ 0.14 vs 2.14)

## Future Considerations

- **Weighted Distribution:** Could give storytellers slightly higher weight (e.g., 3 each) and painters lower weight (e.g., 1-2 each)
- **User Preferences:** Could allow marking favorite styles to appear more frequently
- **Content-Specific Hints:** Could respect optional style hints in content frontmatter for special cases
