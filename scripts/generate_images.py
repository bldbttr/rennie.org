#!/usr/bin/env python3
"""
Image Generator for Inspiration Site
Generates AI artwork using Google's Nano Banana (Gemini 2.5 Flash Image) API.
"""

import json
import os
import base64
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
from io import BytesIO
from PIL import Image
import google.genai as genai
from content_parser import ContentParser


class ImageGenerator:
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the image generator with API credentials."""
        self.api_key = api_key or os.environ.get('GEMINI_API_KEY')
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        # Initialize the client for image generation
        self.client = genai.Client(api_key=self.api_key)
        
        # Set up directories
        self.images_dir = Path("generated/images")
        self.metadata_dir = Path("generated/metadata")
        self.images_dir.mkdir(parents=True, exist_ok=True)
        self.metadata_dir.mkdir(parents=True, exist_ok=True)
        
        # Cost tracking
        self.cost_per_image = 0.039  # $0.039 per 1024x1024 image
        
    def generate_image_filename(self, content_data: Dict[str, Any], variation: int = 1) -> str:
        """Generate a consistent filename for an image."""
        # Create filename from author and title
        author = content_data['author'].lower().replace(' ', '_')
        title = content_data['title'].lower()
        # Clean title for filename
        title_clean = ''.join(c if c.isalnum() or c in [' ', '-'] else '' for c in title)
        title_clean = title_clean.replace(' ', '_')[:50]  # Limit length
        
        return f"{author}_{title_clean}_v{variation}.png"
    
    def check_existing_image(self, filename: str) -> bool:
        """Check if an image already exists."""
        image_path = self.images_dir / filename
        return image_path.exists()
    
    def save_image(self, image_data: bytes, filename: str) -> Path:
        """Save image data to file."""
        image_path = self.images_dir / filename
        
        with open(image_path, 'wb') as f:
            f.write(image_data)
        
        return image_path
    
    def save_metadata(self, content_data: Dict[str, Any], filename: str, 
                     generation_info: Dict[str, Any], variation_info: Dict[str, Any] = None) -> Path:
        """Save generation metadata for tracking."""
        metadata_filename = filename.replace('.png', '_metadata.json')
        metadata_path = self.metadata_dir / metadata_filename
        
        metadata = {
            'content': {
                'title': content_data['title'],
                'author': content_data['author'],
                'type': content_data['type'],
                'quote_text': content_data['quote_text'],
                'source_file': content_data['content_file']
            },
            'style': {
                'name': content_data.get('style_name', 'unknown'),
                'approach': content_data.get('style_approach', 'artistic'),
                'variation': variation_info if variation_info else {'type': 'original'}
            },
            'generation': {
                'timestamp': datetime.now().isoformat(),
                'model': 'gemini-2.5-flash-image-preview',
                'prompt': content_data['prompt']['text'],
                'prompt_length': len(content_data['prompt']['text']),
                'cost': self.cost_per_image,
                'image_filename': filename,
                'image_path': str(self.images_dir / filename),
                **generation_info
            }
        }
        
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        return metadata_path
    
    def generate_image(self, content_data: Dict[str, Any], force: bool = False, 
                      variation: int = 1, variation_info: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate an image using Nano Banana API."""
        filename = self.generate_image_filename(content_data, variation)
        
        # Check if image already exists
        if not force and self.check_existing_image(filename):
            print(f"  Image already exists: {filename}")
            return {
                'status': 'skipped',
                'filename': filename,
                'path': str(self.images_dir / filename),
                'reason': 'already_exists'
            }
        
        print(f"  Generating image: {filename}")
        print(f"  Style: {content_data['style_name']} ({content_data['style_approach']})")
        print(f"  Prompt length: {len(content_data['prompt']['text'])} chars")
        
        try:
            # Generate the image using the new Gemini client
            prompt = content_data['prompt']['text']
            
            # Create a focused image generation prompt
            full_prompt = f"Create a 1024x1024 abstract artwork: {prompt}"
            
            print(f"  Full prompt: {full_prompt[:100]}...")
            
            # Generate the image using the new API
            response = self.client.models.generate_content(
                model="gemini-2.5-flash-image-preview",
                contents=full_prompt
            )
            
            # Extract image data from response
            image_parts = [
                part.inline_data.data
                for part in response.candidates[0].content.parts
                if part.inline_data
            ]
            
            if image_parts:
                # Process the first image
                image_data = image_parts[0]
                image = Image.open(BytesIO(image_data))
                
                # Save the image
                image_path = self.images_dir / filename
                image.save(image_path)
                
                # Save metadata
                generation_info = {
                    'attempts': 1,
                    'success': True,
                    'response_parts': len(response.candidates[0].content.parts),
                    'image_parts': len(image_parts),
                    'full_prompt': full_prompt,
                    'image_size': f"{image.width}x{image.height}"
                }
                metadata_path = self.save_metadata(content_data, filename, generation_info)
                
                print(f"  ✓ Image saved: {image_path}")
                print(f"  ✓ Size: {image.width}x{image.height}")
                print(f"  ✓ Metadata saved: {metadata_path}")
                print(f"  ✓ Cost: ${self.cost_per_image:.3f}")
                
                return {
                    'status': 'success',
                    'filename': filename,
                    'path': str(image_path),
                    'metadata_path': str(metadata_path),
                    'cost': self.cost_per_image,
                    'variation': variation
                }
            else:
                # No image found in response
                print(f"  No images found in response")
                print(f"  Response candidates: {len(response.candidates) if hasattr(response, 'candidates') else 'N/A'}")
                
                # Save metadata indicating no image was generated
                generation_info = {
                    'attempts': 1,
                    'success': False,
                    'note': 'No image found in response',
                    'response_candidates': len(response.candidates) if hasattr(response, 'candidates') else 0,
                    'full_prompt': full_prompt
                }
                metadata_path = self.save_metadata(content_data, filename, generation_info)
                
                return {
                    'status': 'no_image',
                    'filename': filename,
                    'metadata_path': str(metadata_path),
                    'note': 'No image found in API response'
                }
            
        except Exception as e:
            print(f"  ✗ Error generating image: {e}")
            
            # Save error metadata
            generation_info = {
                'attempts': 1,
                'success': False,
                'error': str(e)
            }
            metadata_path = self.save_metadata(content_data, filename, generation_info)
            
            return {
                'status': 'error',
                'filename': filename,
                'metadata_path': str(metadata_path),
                'error': str(e)
            }
    
    def generate_variations(self, content_data: Dict[str, Any], num_variations: int = 3, 
                           force: bool = False) -> List[Dict[str, Any]]:
        """Generate multiple variations of an image with different styles."""
        from content_parser import ContentParser
        import random
        
        results = []
        parser = ContentParser()
        
        # Get the current style info
        original_style = content_data.get('style_name', 'unknown')
        original_approach = content_data.get('style_approach', 'artistic')
        
        # Get available styles
        artistic_styles = list(parser.styles_data.get('abstract_artistic_styles', {}).keys())
        scene_styles = list(parser.styles_data.get('animated_moment_styles', {}).keys())
        
        for variation_num in range(1, num_variations + 1):
            print(f"\n  === Variation {variation_num}/{num_variations} ===")
            
            # Determine style for this variation
            if variation_num == 1:
                # Variation 1: Use the original style
                style_name = original_style
                style_approach = original_approach
                variation_type = "original"
            elif variation_num == 2:
                # Variation 2: Random style from same category
                if original_approach == 'artistic':
                    available = [s for s in artistic_styles if s != original_style]
                    style_name = random.choice(available) if available else original_style
                else:
                    available = [s for s in scene_styles if s != original_style]
                    style_name = random.choice(available) if available else original_style
                style_approach = original_approach
                variation_type = "same_category"
            else:
                # Variation 3+: Random style from opposite category
                if original_approach == 'artistic':
                    style_name = random.choice(scene_styles) if scene_styles else original_style
                    style_approach = 'scene'
                else:
                    style_name = random.choice(artistic_styles) if artistic_styles else original_style
                    style_approach = 'artistic'
                variation_type = "opposite_category"
            
            # Create modified content data with new style
            variation_content = content_data.copy()
            
            # Get the new style data and regenerate prompt
            style_data = parser.get_style_data(style_name, style_approach)
            
            # Update the content with new style
            variation_content['style_name'] = style_name
            variation_content['style_approach'] = style_approach
            
            # Regenerate the prompt with new style
            if style_data:
                prompt_parts = []
                prompt_parts.append(style_data.get('base_prompt', ''))
                
                # Add personal context if available
                if variation_content.get('what_i_see_in_it'):
                    prompt_parts.append(f"Inspired by the feeling of: {variation_content['what_i_see_in_it']}")
                
                # Add mood and elements
                if style_data.get('mood_elements'):
                    prompt_parts.append(f"Capturing {', '.join(style_data['mood_elements'])}")
                
                # Add color palette
                if style_data.get('color_palette'):
                    colors = ', '.join(style_data['color_palette'])
                    prompt_parts.append(f"Using a palette of {colors}")
                
                # Add composition guidance
                if style_data.get('composition'):
                    prompt_parts.append(style_data['composition'])
                
                # Always add square format optimization
                prompt_parts.append("square composition, centered focus, 1:1 aspect ratio")
                
                # Join all parts with periods and spaces
                prompt_text = '. '.join(part.strip() for part in prompt_parts if part)
                
                variation_content['prompt'] = {
                    'text': prompt_text,
                    'style_name': style_name,
                    'style_approach': style_approach
                }
            
            # Generate the image with variation info
            variation_info = {
                'variation_number': variation_num,
                'variation_type': variation_type,
                'original_style': original_style,
                'variation_style': style_name,
                'style_approach': style_approach
            }
            
            result = self.generate_image(
                variation_content, 
                force=force, 
                variation=variation_num,
                variation_info=variation_info
            )
            
            results.append(result)
            
            # Rate limiting between variations
            if variation_num < num_variations and result['status'] == 'success':
                time.sleep(2)
        
        return results
    
    def generate_from_parsed_content(self, parsed_content_file: str = "generated/parsed_content.json",
                                    force: bool = False, variations: int = 3) -> List[Dict[str, Any]]:
        """Generate images from parsed content data."""
        # Load parsed content
        parsed_file = Path(parsed_content_file)
        if not parsed_file.exists():
            print(f"Parsed content file not found: {parsed_file}")
            print("Running content parser first...")
            parser = ContentParser()
            all_content = parser.parse_all_content()
            if not all_content:
                raise ValueError("No content found to generate images from")
        else:
            with open(parsed_file, 'r') as f:
                content = json.load(f)
                # Handle both single content and list of content
                all_content = [content] if isinstance(content, dict) else content
        
        results = []
        total_cost = 0
        
        print(f"\nGenerating images for {len(all_content)} content pieces...")
        print("=" * 60)
        
        for i, content_data in enumerate(all_content, 1):
            print(f"\n[{i}/{len(all_content)}] {content_data['title']} by {content_data['author']}")
            
            if variations > 1:
                # Generate multiple variations
                variation_results = self.generate_variations(content_data, num_variations=variations, force=force)
                results.extend(variation_results)
                
                for result in variation_results:
                    if result['status'] == 'success':
                        total_cost += result['cost']
            else:
                # Generate single image (backward compatibility)
                result = self.generate_image(content_data, force=force)
                results.append(result)
                
                if result['status'] == 'success':
                    total_cost += result['cost']
            
            # Rate limiting - wait between content pieces
            if i < len(all_content):
                time.sleep(2)  # 2-3 second delay between content pieces
        
        print("\n" + "=" * 60)
        print("Generation Summary:")
        print(f"  Total content: {len(all_content)}")
        print(f"  Successful: {sum(1 for r in results if r['status'] == 'success')}")
        print(f"  Skipped: {sum(1 for r in results if r['status'] == 'skipped')}")
        print(f"  Errors: {sum(1 for r in results if r['status'] == 'error')}")
        print(f"  Total cost: ${total_cost:.3f}")
        
        # Save results summary
        summary_file = Path("generated/generation_summary.json")
        with open(summary_file, 'w') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'total_content': len(all_content),
                'results': results,
                'total_cost': total_cost
            }, f, indent=2)
        
        print(f"\n✓ Summary saved to {summary_file}")
        
        return results


def main():
    """Main function for testing the image generator."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate AI artwork for inspiration content')
    parser.add_argument('--force-all', action='store_true', 
                       help='Force regenerate all images')
    parser.add_argument('--new-only', action='store_true',
                       help='Generate only missing images (default)')
    parser.add_argument('--content-file', default='generated/parsed_content.json',
                       help='Path to parsed content JSON file')
    parser.add_argument('--variations', type=int, default=3,
                       help='Number of variations to generate per content piece (default: 3)')
    
    args = parser.parse_args()
    
    # Set API key if provided
    api_key = os.environ.get('GEMINI_API_KEY', 'AIzaSyCh41VaooU6xexjq7zndc7FSNOh2Sg4-EE')
    os.environ['GEMINI_API_KEY'] = api_key
    
    try:
        generator = ImageGenerator()
        
        print("Nano Banana Image Generator")
        print("=" * 60)
        print(f"API Key: {api_key[:10]}...")
        print(f"Model: gemini-2.5-flash-image-preview")
        print(f"Cost per image: ${generator.cost_per_image}")
        print()
        
        # Generate images
        results = generator.generate_from_parsed_content(
            parsed_content_file=args.content_file,
            force=args.force_all,
            variations=args.variations
        )
        
    except Exception as e:
        print(f"Error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())