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
import hashlib
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
        required_fields = ['title', 'author', 'type']
        for field in required_fields:
            if field not in frontmatter:
                raise ValueError(f"Missing required field '{field}' in {file_path}")
        
        # Set defaults for style fields if not present
        if 'style_category' not in frontmatter:
            frontmatter['style_category'] = 'random'
        if 'style_specific' not in frontmatter:
            frontmatter['style_specific'] = 'random'
        
        # Parse markdown sections
        sections = self._parse_sections(markdown_content)
        
        return {
            'file_path': str(file_path),
            'frontmatter': frontmatter,
            'content': sections.get('main', ''),
            'why_i_like_it': sections.get('why_i_like_it', ''),
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
                # Remove what_i_see_in_it handling
                else:
                    sections[header.replace(' ', '_')] = content
        
        return sections
    
    def get_stable_style_for_content(self, content_file: str, content_text: str, style_category: str, style_specific: str) -> tuple[str, str, bool]:
        """Get stable style assignment using existing metadata when available.
        If content has changed, generates a new random style.
        Returns (style_name, actual_category, content_changed)
        """
        # Check for existing metadata to maintain style consistency
        base_filename = self._get_base_filename_from_content_file(content_file)
        metadata_file = Path(f"generated/metadata/{base_filename}_v1_metadata.json")
        
        if metadata_file.exists():
            try:
                with open(metadata_file, 'r') as f:
                    metadata = json.load(f)
                    existing_style = metadata.get('style', {}).get('name')
                    existing_approach = metadata.get('style', {}).get('approach')
                    existing_content = metadata.get('content', {}).get('quote_text', '')
                    
                    # Check if content has changed
                    content_changed = existing_content != content_text
                    
                    if content_changed:
                        # Content changed - generate new random style for variety
                        style_name, actual_category = self._generate_new_style_assignment(style_category, style_specific)
                        return style_name, actual_category, True
                    elif existing_style and existing_approach:
                        # Content unchanged - use existing style assignment for consistency
                        return existing_style, existing_approach, False
            except (json.JSONDecodeError, FileNotFoundError):
                pass
        
        # No existing metadata - generate new random assignment
        style_name, actual_category = self._generate_new_style_assignment(style_category, style_specific)
        return style_name, actual_category, False
    
    def _get_base_filename_from_content_file(self, content_file: str) -> str:
        """Extract base filename from content file path."""
        if content_file.startswith('content/inspiration/'):
            return content_file.replace('content/inspiration/', '').replace('.md', '')
        else:
            return Path(content_file).stem if content_file else 'unknown'
    
    def _generate_new_style_assignment(self, style_category: str, style_specific: str) -> tuple[str, str]:
        """Generate new random style assignment for content without existing metadata."""
        return self.select_style(style_category, style_specific)

    def select_style(self, style_category: str, style_specific: str) -> tuple[str, str]:
        """Select a style based on category and specific preferences.
        Returns (style_name, actual_category)
        """
        # Handle true random - pick from all available styles
        if style_category == "random":
            all_styles = []
            painting_styles = list(self.styles_data.get('painting_technique_styles', {}).keys())
            storytelling_styles = list(self.styles_data.get('visual_storytelling_techniques', {}).keys())
            
            for style in painting_styles:
                all_styles.append((style, 'painting_technique'))
            for style in storytelling_styles:
                all_styles.append((style, 'visual_storytelling'))
            
            if all_styles:
                style_name, actual_category = random.choice(all_styles)
                return style_name, actual_category
            else:
                return 'turner-atmospheric', 'painting_technique'
        
        # Handle specific category
        elif style_category in ['painting_technique', 'visual_storytelling']:
            if style_specific == "random":
                # Random from the specified category
                return self._get_random_style(style_category), style_category
            else:
                # Specific style requested - validate it exists in the category
                if self._validate_style_in_category(style_specific, style_category):
                    return style_specific, style_category
                else:
                    print(f"Warning: Style '{style_specific}' not found in '{style_category}', using random")
                    return self._get_random_style(style_category), style_category
        
        # Fallback to random painting technique
        else:
            print(f"Warning: Unknown style_category '{style_category}', using random painting technique")
            return self._get_random_style('painting_technique'), 'painting_technique'
    
    def _get_random_style(self, style_category: str) -> str:
        """Get a random style from the specified category."""
        if style_category == 'painting_technique':
            styles = list(self.styles_data.get('painting_technique_styles', {}).keys())
        elif style_category == 'visual_storytelling':
            styles = list(self.styles_data.get('visual_storytelling_techniques', {}).keys())
        else:
            styles = []
        
        return random.choice(styles) if styles else 'turner-atmospheric'
    
    def _validate_style_in_category(self, style_name: str, style_category: str) -> bool:
        """Check if a style name exists in the specified category."""
        if style_category == 'painting_technique':
            return style_name in self.styles_data.get('painting_technique_styles', {})
        elif style_category == 'visual_storytelling':
            return style_name in self.styles_data.get('visual_storytelling_techniques', {})
        return False
    
    def get_style_data(self, style_name: str, style_category: str) -> Dict[str, Any]:
        """Get the complete style data for a given style name."""
        # Check in the appropriate style collection based on category
        if style_category == 'painting_technique':
            styles = self.styles_data.get('painting_technique_styles', {})
        elif style_category == 'visual_storytelling':
            styles = self.styles_data.get('visual_storytelling_techniques', {})
        else:
            # Try both
            styles = {**self.styles_data.get('painting_technique_styles', {}),
                     **self.styles_data.get('visual_storytelling_techniques', {})}
        
        return styles.get(style_name, {})
    
    def generate_prompt(self, parsed_content: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a structured prompt for Nano Banana API."""
        frontmatter = parsed_content['frontmatter']
        content_file = parsed_content['file_path']
        content_text = parsed_content['content']
        
        # Select and get style using stable assignment system with content change detection
        style_category = frontmatter.get('style_category', 'random')
        style_specific = frontmatter.get('style_specific', 'random')
        style_name, actual_category, content_changed = self.get_stable_style_for_content(
            content_file, content_text, style_category, style_specific
        )
        style_data = self.get_style_data(style_name, actual_category)
        
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
            'style_category': actual_category,
            'style_data': style_data,
            'vibe': frontmatter.get('vibe', []),
            'content_changed': content_changed,
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
            print(f"  - {content['title']} by {content['author']} ({content['style_category']}: {content['style_name']})")
    else:
        print("No content files found or all files had errors.")


if __name__ == "__main__":
    main()