# Content Typography Enhancement Specification

## Overview

This specification outlines enhancements to support hierarchical typography in content sections, enabling better visual presentation of quotes with varying lengths and importance levels.

## Current State

### File Structure
```markdown
---
title: "Quote title"
author: "Author Name"
# ... frontmatter
---

Quote content here.

## Why I Like It
Personal context and thoughts.
```

### Rendering
- Content parser extracts main content as `quote_text`
- Frontend renders using `textContent` (plain text only)
- Single font size for entire quote content
- Separate rendering for "Why I Like It" section

## Proposed Enhancement

### 1. File Format Evolution

**Option A: Structured Sections (Recommended)**
```markdown
---
title: "Quote title"
author: "Author Name"
# ... frontmatter
---

## Content
**And you can always feel product/market fit when it's happening.**

The customers are buying the product just as fast as you can make it—or usage is growing just as fast as you can add more servers. Money from customers is piling up in your company checking account.

## Why I Like It
Timeless piece. Describes the mission of investing and building.

Known irony - personal projects don't have PMF :)
```

**Option B: Keep Current Format (Backward Compatible)**
```markdown
---
title: "Quote title"
author: "Author Name"
# ... frontmatter
---

**And you can always feel product/market fit when it's happening.**

The customers are buying the product just as fast as you can make it—or usage is growing just as fast as you can add more servers.

## Why I Like It
Timeless piece. Describes the mission of investing and building.

Known irony - personal projects don't have PMF :)
```

### 2. Typography Hierarchy

#### Content Section
- **Bold text** (wrapped in `**text**`): Primary emphasis
  - Desktop: 2.0rem (up from 1.8rem)
  - Mobile: 1.6rem (up from 1.4rem)
  
- **Regular paragraphs**: Secondary content
  - Desktop: 1.6rem (down from 1.8rem)
  - Mobile: 1.3rem (down from 1.4rem)
  
- **Subsequent paragraphs**: Tertiary content
  - Desktop: 1.4rem
  - Mobile: 1.2rem

#### Why I Like It Section
- **First paragraph**: Main thoughts
  - Current size: 0.95rem desktop, 0.85rem mobile
  
- **Subsequent paragraphs**: Secondary thoughts/footnotes
  - Desktop: 0.85rem (smaller)
  - Mobile: 0.8rem (smaller)

### 3. Implementation Strategy

#### Phase 1: Content Parser Updates
1. **Maintain backward compatibility** - existing content continues to work
2. **Enhanced markdown parsing**:
   - Preserve markdown formatting (`**bold**`, paragraphs)
   - Convert to structured HTML for rendering
3. **Section detection**:
   - Detect `## Content` header if present
   - Fall back to pre-header content if no `## Content` section

#### Phase 2: Frontend Rendering
1. **Switch from `textContent` to `innerHTML`** for formatted content
2. **CSS enhancements**:
   - Typography scales for different emphasis levels
   - Responsive sizing for mobile/desktop
3. **Progressive enhancement**:
   - Plain text fallback for content without formatting
   - Graceful degradation

#### Phase 3: Content Migration
1. **Optional migration** of existing content files
2. **Template/examples** for new content format
3. **Documentation** for content authors

## Technical Implementation

### Content Parser Changes (`scripts/content_parser.py`)

```python
def _parse_content_with_formatting(self, content: str) -> dict:
    """Parse content preserving markdown formatting."""
    
    # Check for structured format (## Content header)
    if '## Content' in content:
        sections = re.split(r'^## ', content, flags=re.MULTILINE)
        content_section = None
        
        for section in sections[1:]:  # Skip first (pre-header content)
            if section.startswith('Content\n'):
                content_section = section[8:].strip()  # Remove "Content\n"
                break
                
        if content_section:
            return {
                'structured': True,
                'html': self._markdown_to_html(content_section),
                'plain': content_section
            }
    
    # Fall back to existing format (content before first ##)
    main_content = content.split('##')[0].strip()
    return {
        'structured': False,
        'html': self._markdown_to_html(main_content),
        'plain': main_content
    }

def _markdown_to_html(self, text: str) -> str:
    """Convert basic markdown to HTML."""
    # Handle bold text
    text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)
    
    # Handle paragraphs
    paragraphs = text.split('\n\n')
    html_paragraphs = [f'<p>{p.strip()}</p>' for p in paragraphs if p.strip()]
    
    return ''.join(html_paragraphs)
```

### Frontend Changes (`scripts/templates/app.js`)

```javascript
updateTextContent(content) {
    const quoteText = document.getElementById('quote-text');
    
    // Check if content has HTML formatting
    if (content.formatted_content) {
        quoteText.innerHTML = content.formatted_content.html;
        quoteText.classList.add('formatted-content');
    } else {
        quoteText.textContent = content.quote_text || content.title;
        quoteText.classList.remove('formatted-content');
    }
    
    // Update context with formatting support
    const context = content.metadata?.why_i_like_it || '';
    if (context) {
        const contextElement = document.getElementById('quote-context');
        contextElement.innerHTML = this._formatContext(context);
    }
}

_formatContext(text) {
    // Split into paragraphs and apply progressive sizing
    const paragraphs = text.split('\n\n');
    return paragraphs.map((p, index) => {
        const className = index === 0 ? 'context-primary' : 'context-secondary';
        return `<p class="${className}">${p}</p>`;
    }).join('');
}
```

### CSS Changes (`scripts/templates/style.css`)

```css
/* Enhanced quote formatting */
.quote-text.formatted-content p {
    margin: 0 0 1rem 0;
}

.quote-text.formatted-content p:first-child {
    font-size: 2.0rem;  /* Larger for first paragraph */
    line-height: 1.3;
}

.quote-text.formatted-content p:nth-child(2) {
    font-size: 1.6rem;  /* Medium for second paragraph */
    line-height: 1.4;
}

.quote-text.formatted-content p:nth-child(n+3) {
    font-size: 1.4rem;  /* Smaller for subsequent paragraphs */
    line-height: 1.4;
}

.quote-text.formatted-content strong {
    font-weight: bold;
    font-size: 1.1em;  /* Slightly larger than surrounding text */
}

/* Context formatting */
.quote-context .context-primary {
    font-size: 0.95rem;
    line-height: 1.5;
    margin-bottom: 0.8rem;
}

.quote-context .context-secondary {
    font-size: 0.85rem;
    line-height: 1.4;
    opacity: 0.8;
    font-style: italic;
}

/* Mobile responsive */
@media (max-width: 768px) {
    .mobile-quote-text.formatted-content p:first-child {
        font-size: 1.6rem;
    }
    
    .mobile-quote-text.formatted-content p:nth-child(2) {
        font-size: 1.3rem;
    }
    
    .mobile-quote-text.formatted-content p:nth-child(n+3) {
        font-size: 1.2rem;
    }
}
```

## Content Examples

### Example 1: pmarca-pmf.md (Enhanced)
```markdown
---
title: "You can always feel product/market fit when it's happening"
author: "Marc Andreessen"
type: "quote"
source: "https://pmarchive.com/guide_to_startups_part4.html"
style_category: "painting_technique"
style_specific: "random"
vibe: ["movement", "flow", "in-the-zone"]
status: "active"
---

## Content
**And you can always feel product/market fit when it's happening.**

The customers are buying the product just as fast as you can make it—or usage is growing just as fast as you can add more servers. Money from customers is piling up in your company checking account. You're hiring sales and customer support staff as fast as you can.

Reporters are calling because they've heard about your hot new thing and they want to talk to you about it. You start getting entrepreneur of the year awards from Harvard Business School. Investment bankers are staking out your house.

## Why I Like It
Timeless piece. Describes the mission of investing and building, and captures the feeling when it's working and when it's not, without listing a metric. I re-read it a couple times a year.

Known irony - personal projects don't have PMF :)
```

### Example 2: paul-graham-make-something.md (Unchanged)
```markdown
---
title: "Make something people want"
author: "Paul Graham"
type: "quote"
source: "https://paulgraham.com/good.html"
style_category: "random"
style_specific: "random"
vibe: ["zen of purpose"]
status: "active"
---

Make something people want.

## Why I Like It  
PG's wisdom resonates with me. This is the best single encapsulation of a startup or product mission I have come across. I try to challenge myself with this often.

Known irony - this nano banana sandbox is something I wanted to make for myself. :)
```

## ⚠️ CRITICAL: Template System Considerations

**MOST IMPORTANT**: This project uses a template-based build system where `/output/` files are generated from `/scripts/templates/`. Based on project history, this is the #1 source of feature loss.

### Required Template Files (NEVER edit /output/ directly):
- ✅ `scripts/templates/app.js` → generates `output/script.js`
- ✅ `scripts/templates/style.css` → generates `output/style.css`  
- ✅ `scripts/templates/index.html` → generates `output/index.html`

### Development Workflow Protocol:
1. **Test Phase**: Create temporary files in `/output/` for testing (e.g., `typography_test.css`)
2. **Verify Phase**: Test formatting functionality thoroughly
3. **Integration Phase**: Move working code to source templates in `/scripts/templates/`
4. **Validation Phase**: Run build cycle to ensure features survive deployment

### HTML/JavaScript Element ID Synchronization:
- **Recurring Issue**: Template changes break DOM element references
- **Prevention**: Always update HTML element IDs and corresponding JavaScript references together
- **Detection**: When functionality works partially (e.g., content updates but style info doesn't)

## Migration Strategy

### Immediate (No Breaking Changes)
1. **Backward compatibility maintained** - all existing content continues to work
2. **Optional enhancement** - content can be enhanced with formatting
3. **Gradual adoption** - migrate content files one by one

### Benefits
- **Visual hierarchy** improves readability for longer quotes
- **Emphasis** allows highlighting key phrases
- **Progressive disclosure** enables footnotes and asides
- **Responsive design** scales appropriately on mobile

### Considerations
- **Content security** - sanitize HTML input to prevent XSS
- **Performance** - minimal impact (basic HTML parsing)
- **Maintenance** - clear documentation for content authors
- **Accessibility** - maintain semantic HTML structure

## Recommendation

**Proceed with Option A (Structured Sections)** because:
1. **Clear separation** between content and metadata
2. **Future flexibility** for additional sections
3. **Consistency** with existing `## Why I Like It` pattern
4. **Easy migration** path for existing content

This enhancement provides the aesthetic improvement you're seeking while maintaining the simplicity and maintainability that's core to the project philosophy.