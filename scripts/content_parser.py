#!/usr/bin/env python3
"""
Content Parser for Inspiration Site
Parses markdown files with YAML frontmatter and generates structured prompts
for Nano Banana image generation.
"""

import json
import yaml
import os
import random
import re
from pathlib import Path
from typing import Dict, List, Any, Optional


class ContentParser:
    def __init__(self, content_dir: str = "content/inspiration", styles_file: str = "content/styles/styles.json"):
        """Initialize the content parser with paths to content and styles."""
        self.content_dir = Path(content_dir)
        self.styles_file = Path(styles_file)
        self.styles_data = self._load_styles()
        
    def _load_styles(self) -> Dict[str, Any]:
        """Load the visual style library from JSON."""
        if not self.styles_file.exists():
            raise FileNotFoundError(f"Style library not found: {self.styles_file}")
        
        with open(self.styles_file, 'r') as f:
            return json.load(f)
    
    def parse_markdown(self, file_path: Path) -> Dict[str, Any]:
        """Parse a markdown file with YAML frontmatter."""
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Split frontmatter and content
        if content.startswith('---'):
            parts = content.split('---', 2)
            if len(parts) >= 3:
                frontmatter = yaml.safe_load(parts[1])
                markdown_content = parts[2].strip()
            else:
                raise ValueError(f"Invalid frontmatter format in {file_path}")
        else:
            raise ValueError(f"No frontmatter found in {file_path}")
        
        # Validate required fields
        required_fields = ['title', 'author', 'type', 'style_approach']
        for field in required_fields:
            if field not in frontmatter:
                raise ValueError(f"Missing required field '{field}' in {file_path}")
        
        # Parse markdown sections
        sections = self._parse_sections(markdown_content)
        
        return {
            'file_path': str(file_path),
            'frontmatter': frontmatter,
            'content': sections.get('main', ''),
            'why_i_like_it': sections.get('why_i_like_it', ''),
            'what_i_see_in_it': sections.get('what_i_see_in_it', ''),
            'visual_notes': sections.get('visual_notes', ''),
            'all_sections': sections
        }
    
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
                elif 'what i see in it' in header:
                    sections['what_i_see_in_it'] = content
                elif 'visual notes' in header:
                    sections['visual_notes'] = content
                else:
                    sections[header.replace(' ', '_')] = content
        
        return sections
    
    def select_style(self, style_approach: str, style_spec: Any) -> str:
        """Select a style based on the specification."""
        if isinstance(style_spec, list):
            # If it's a list, use the first style (could randomize if multiple)
            return style_spec[0] if style_spec else self._get_random_style(style_approach)
        elif style_spec == "random":
            # Random selection from the category
            return self._get_random_style(style_approach)
        elif isinstance(style_spec, str):
            # Direct style name
            return style_spec
        else:
            # Fallback to random
            return self._get_random_style(style_approach)
    
    def _get_random_style(self, style_approach: str) -> str:
        """Get a random style from the specified category."""
        categories = self.styles_data.get('style_categories', {})
        
        if style_approach in categories:
            styles = categories[style_approach].get('styles', [])
            return random.choice(styles) if styles else 'essence-of-desire'
        
        # Default fallback
        return 'essence-of-desire'
    
    def get_style_data(self, style_name: str, style_approach: str) -> Dict[str, Any]:
        """Get the complete style data for a given style name."""
        # Check in the appropriate style collection based on approach
        if style_approach == 'artistic':
            styles = self.styles_data.get('abstract_artistic_styles', {})
        elif style_approach == 'scene':
            styles = self.styles_data.get('animated_moment_styles', {})
        else:
            # Try both
            styles = {**self.styles_data.get('abstract_artistic_styles', {}),
                     **self.styles_data.get('animated_moment_styles', {})}
        
        return styles.get(style_name, {})
    
    def generate_prompt(self, parsed_content: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a structured prompt for Nano Banana API."""
        frontmatter = parsed_content['frontmatter']
        
        # Select and get style
        style_approach = frontmatter.get('style_approach', 'artistic')
        style_name = self.select_style(style_approach, frontmatter.get('style'))
        style_data = self.get_style_data(style_name, style_approach)
        
        # Build the prompt components
        prompt_parts = []
        
        # Start with base prompt from style
        if 'base_prompt' in style_data:
            prompt_parts.append(style_data['base_prompt'])
        
        # Add personal context if available
        if parsed_content['what_i_see_in_it']:
            prompt_parts.append(f"Inspired by the feeling of: {parsed_content['what_i_see_in_it']}")
        
        # Add mood elements
        if 'mood_elements' in style_data:
            moods = ', '.join(style_data['mood_elements'])
            prompt_parts.append(f"Capturing the essence of {moods}")
        
        # Add color palette
        if 'color_palette' in style_data:
            colors = ', '.join(style_data['color_palette'])
            prompt_parts.append(f"Using a palette of {colors}")
        
        # Add composition guidance
        if 'composition' in style_data:
            prompt_parts.append(style_data['composition'])
        
        # Add visual notes if provided
        if parsed_content['visual_notes']:
            prompt_parts.append(parsed_content['visual_notes'])
        
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
            'prompt': {
                'text': full_prompt,
                'components': {
                    'base': style_data.get('base_prompt', ''),
                    'personal_context': parsed_content['what_i_see_in_it'],
                    'mood': style_data.get('mood_elements', []),
                    'colors': style_data.get('color_palette', []),
                    'composition': style_data.get('composition', ''),
                    'visual_notes': parsed_content['visual_notes']
                }
            },
            'metadata': {
                'source': frontmatter.get('source'),
                'status': frontmatter.get('status', 'active'),
                'tags': frontmatter.get('tags', []),
                'why_i_like_it': parsed_content['why_i_like_it']
            }
        }
    
    def parse_all_content(self) -> List[Dict[str, Any]]:
        """Parse all markdown files in the content directory."""
        results = []
        
        for file_path in self.content_dir.glob('*.md'):
            # Skip template files
            if 'template' in file_path.name.lower():
                continue
                
            try:
                parsed = self.parse_markdown(file_path)
                prompt_data = self.generate_prompt(parsed)
                results.append(prompt_data)
                print(f"✓ Parsed: {file_path.name}")
            except Exception as e:
                print(f"✗ Error parsing {file_path.name}: {e}")
        
        return results


def main():
    """Main function - always parse all content files."""
    parser = ContentParser()
    
    print("Parsing all content files...\n")
    
    all_content = parser.parse_all_content()
    if all_content:
        output_file = Path("generated/all_content.json")
        output_file.parent.mkdir(exist_ok=True)
        
        with open(output_file, 'w') as f:
            json.dump(all_content, f, indent=2)
        
        print(f"\n✓ Parsed {len(all_content)} content files")
        print(f"✓ Saved to {output_file}")
        
        # Show summary
        for content in all_content:
            print(f"  - {content['title']} by {content['author']} ({content['style_approach']}: {content['style_name']})")
    else:
        print("No content files found or all files had errors.")


if __name__ == "__main__":
    main()