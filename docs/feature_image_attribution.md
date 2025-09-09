# Feature: Image Generation Attribution & Transparency

## Overview
Add transparent attribution for AI-generated images, showing both the model used and the generation parameters, enhancing user understanding of the creative process.

## Requirements

### 1. Model Attribution Badge
**Location**: Bottom right corner of the page  
**Content**: Display the AI model used for image generation  
**Format**: `Gemini Flash` or `Gemini 2.0` (keep succinct)
**Styling**: Subtle, semi-transparent badge that doesn't distract from content

### 2. Style Parameter Tooltip
**Trigger**: Hover over the existing style indicator (bottom right)  
**Content**: Display the full prompt and parameters used for image generation
**Information to show**:
- Complete prompt sent to the API
- Model version (e.g., `gemini-2.0-flash-exp`)
- Image dimensions (e.g., `1024x1024`)
- Style approach (artistic/literal)
- Base style template used
- Timestamp of generation

**Format Example**:
```
Style: Modern Inspirational (artistic)
Model: gemini-2.0-flash-exp
Generated: 2025-01-09

Prompt (342 chars):
"Create an abstract composition that captures the essence of 
desire and creation, using flowing organic shapes in vibrant..."

Dimensions: 1024x1024
```

## Implementation Considerations

### Data Storage
- Store generation metadata alongside images
- Options:
  1. Embed in image EXIF data
  2. Create companion JSON metadata files
  3. Include in site's content data structure

### UI/UX Design
- Tooltip should be readable but not overwhelming
- Consider max-width and scrollable content for long prompts
- Mobile: Show on tap instead of hover
- Accessibility: Ensure keyboard navigation support

### Privacy & Security
- Ensure API keys are never exposed in metadata
- Consider if full prompts should be public (they reveal creative process)
- May want to truncate very long prompts in UI

## Implementation Decisions

1. **Metadata Storage**: 
   - Extract from image generation process at runtime
   - Store in `/generated/metadata/` as JSON files during generation
   - Include in site build data structure for runtime access

2. **Prompt Visibility**: 
   - Check prompt length, if >300 chars show summarized version
   - Summary format: First 150 chars + "..." + last 100 chars
   - Include character count indicator (e.g., "Prompt (542 chars)")

3. **Historical Data**: 
   - Gracefully handle missing metadata (don't break the site)
   - Show "Generation details unavailable" for legacy images
   - Plan to regenerate all images with proper tracking in future update

4. **Mobile Experience**: 
   - Tap on style indicator to show details
   - Same tooltip/modal as desktop but triggered by tap
   - Tap outside or X button to dismiss

5. **Performance**: 
   - Include metadata in initial page data (small JSON overhead)
   - Avoids additional network requests
   - Minimal impact on load time

## Technical Requirements

### Backend Changes
- Modify `generate_images.py` to save metadata during generation
- Update `build_site.py` to include metadata in site data
- Ensure metadata follows images through the build pipeline

### Frontend Changes
- Add tooltip component to `web/script.js`
- Style tooltip in `web/style.css`
- Add model attribution badge to layout
- Handle touch events for mobile

### Data Structure
```json
{
  "generation_metadata": {
    "model": "gemini-2.0-flash-exp",
    "model_display": "Gemini 2.0 Flash",
    "timestamp": "2025-01-09T14:30:00Z",
    "dimensions": "1024x1024",
    "style_approach": "artistic",
    "style_name": "modern-inspirational",
    "prompt": "Full prompt text...",
    "prompt_tokens": 150,
    "generation_time_ms": 2500
  }
}
```

## Success Criteria
- Users can identify which AI model created each image
- Creative process is transparent through prompt visibility
- Implementation doesn't impact page load performance
- Mobile users have equal access to information
- Metadata persists through site rebuilds

## Next Steps
1. Decide on metadata storage approach
2. Determine appropriate level of prompt detail to expose
3. Design tooltip UI mockup
4. Implement backend metadata tracking
5. Add frontend tooltip functionality
6. Test across devices and browsers