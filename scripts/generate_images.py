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


def load_config() -> Dict[str, Any]:
    """Load configuration from config.json"""
    config_path = Path(__file__).parent.parent / "config.json"
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        # Fallback to defaults if config file doesn't exist
        return {
            "image_generation": {
                "variations_per_content": 3,
                "cost_per_image": 0.039,
                "model": "gemini-2.5-flash"
            }
        }


class ImageGenerator:
    # Single source of truth for the model name
    MODEL_NAME = "gemini-2.5-flash-image-preview"
    MODEL_DISPLAY_NAME = "Nano Banana (Gemini 2.5 Flash Image)"
    
    def __init__(self, api_key: Optional[str] = None, check_only: bool = False):
        """Initialize the image generator with API credentials."""
        # Load configuration
        self.config = load_config()
        self.variations_per_content = self.config["image_generation"]["variations_per_content"]
        self.cost_per_image = self.config["image_generation"]["cost_per_image"]
        
        self.api_key = api_key or os.environ.get('GEMINI_API_KEY')
        
        if not check_only and not self.api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        # Initialize the client for image generation (only if not check-only mode)
        self.client = genai.Client(api_key=self.api_key) if self.api_key else None
        
        # Set up directories
        self.images_dir = Path("generated/images")
        self.metadata_dir = Path("generated/metadata")
        self.archive_dir = Path("generated/archive")
        self.images_dir.mkdir(parents=True, exist_ok=True)
        self.metadata_dir.mkdir(parents=True, exist_ok=True)
        self.archive_dir.mkdir(parents=True, exist_ok=True)
        
        # Cost tracking
        self.cost_per_image = 0.039  # $0.039 per 1024x1024 image

    def archive_existing_images(self) -> Optional[str]:
        """Move existing images to timestamped archive folder."""
        import shutil
        
        # Check if there are any images to archive
        existing_images = list(self.images_dir.glob('*.png'))
        existing_metadata = list(self.metadata_dir.glob('*_metadata.json'))
        
        if not existing_images and not existing_metadata:
            print("No existing images to archive.")
            return None
        
        # Create timestamped archive folder
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
        archive_folder = self.archive_dir / timestamp
        archive_folder.mkdir(exist_ok=True)
        
        # Create subfolders
        archive_images = archive_folder / "images"
        archive_metadata = archive_folder / "metadata"
        archive_images.mkdir(exist_ok=True)
        archive_metadata.mkdir(exist_ok=True)
        
        # Move images
        moved_count = 0
        for image_file in existing_images:
            dest = archive_images / image_file.name
            shutil.move(str(image_file), str(dest))
            moved_count += 1
        
        # Move metadata
        for metadata_file in existing_metadata:
            dest = archive_metadata / metadata_file.name
            shutil.move(str(metadata_file), str(dest))
        
        print(f"✓ Archived {moved_count} images to {archive_folder}")
        return str(archive_folder)

    def check_new_styles(self, parsed_content_file: str = "generated/all_content.json") -> Dict[str, Any]:
        """Check if content uses styles that don't have existing images."""
        # Load content data
        if not Path(parsed_content_file).exists():
            return {"error": f"Content file not found: {parsed_content_file}"}
        
        with open(parsed_content_file, 'r') as f:
            content_list = json.load(f)
        
        # Get existing images and their metadata
        existing_images = list(self.images_dir.glob('*.png'))
        existing_metadata = {}
        
        for img_file in existing_images:
            metadata_file = self.metadata_dir / img_file.name.replace('.png', '_metadata.json')
            if metadata_file.exists():
                with open(metadata_file, 'r') as f:
                    metadata = json.load(f)
                    existing_metadata[img_file.name] = {
                        'style_name': metadata.get('style', {}).get('name', 'unknown'),
                        'style_approach': metadata.get('style', {}).get('approach', 'artistic')
                    }
        
        # Check for content without matching images or with different styles
        needs_generation = []
        
        for content in content_list:
            # Generate expected filenames for all variations
            base_filename = self.generate_image_filename(content, 1).replace('_v1.png', '')
            
            # Check if any variation exists and compare styles and content
            variations_exist = []
            style_mismatch = False
            content_change = content.get('content_changed', False)
            current_style = content.get('style_name', 'unknown')
            
            for v in range(1, self.variations_per_content + 1):  # Check for configured variations
                var_filename = f"{base_filename}_v{v}.png"
                if var_filename in [img.name for img in existing_images]:
                    variations_exist.append(v)
                    
                    # Compare style from metadata with current content style (v1 only)
                    if v == 1 and var_filename in existing_metadata:
                        metadata_style = existing_metadata[var_filename]['style_name']
                        if metadata_style != current_style:
                            style_mismatch = True
            
            # Determine if generation is needed
            if not variations_exist:
                # Get filename using utility function
                filename = self.get_base_filename_from_content(content)
                
                needs_generation.append({
                    'title': content['title'],
                    'author': content['author'],
                    'filename': filename,
                    'reason': 'no_images',
                    'expected_style': current_style,
                    'type': 'new'
                })
            elif content_change:
                # Content has changed - needs regeneration with new style
                filename = self.get_base_filename_from_content(content)
                
                needs_generation.append({
                    'title': content['title'],
                    'author': content['author'],
                    'filename': filename,
                    'reason': 'content_change',
                    'expected_style': current_style,
                    'type': 'update'
                })
            elif style_mismatch:
                # Find what style the existing images have
                existing_style = 'unknown'
                first_existing = f"{base_filename}_v1.png"
                if first_existing in existing_metadata:
                    existing_style = existing_metadata[first_existing]['style_name']
                
                # Get filename using utility function
                filename = self.get_base_filename_from_content(content)
                
                needs_generation.append({
                    'title': content['title'],
                    'author': content['author'],
                    'filename': filename,
                    'reason': 'style_change',
                    'expected_style': current_style,
                    'existing_style': existing_style,
                    'type': 'update'
                })
        
        return {
            'existing_images': len(existing_images),
            'content_pieces': len(content_list),
            'needs_generation': needs_generation
        }
    
    def preview_analysis(self, parsed_content_file: str = "generated/all_content.json") -> Dict[str, Any]:
        """Detailed analysis for preview including cost calculations and approval logic."""
        check_result = self.check_new_styles(parsed_content_file)
        
        if "error" in check_result:
            return check_result
        
        # Separate new vs updates
        needs_generation = check_result.get('needs_generation', [])
        new_images = [item for item in needs_generation if item.get('type') == 'new']
        updates = [item for item in needs_generation if item.get('type') == 'update']
        
        # Calculate costs
        new_pieces = len(new_images)
        update_pieces = len(updates)
        total_pieces = new_pieces + update_pieces
        total_images = total_pieces * self.variations_per_content  # variations per piece
        total_cost = total_images * self.cost_per_image
        
        return {
            'content_pieces': check_result['content_pieces'],
            'existing_images': check_result['existing_images'],
            'new_pieces': new_pieces,
            'update_pieces': update_pieces,
            'total_pieces': total_pieces,
            'total_images': total_images,
            'total_cost': total_cost,
            'cost_per_image': self.cost_per_image,
            'variations_per_content': self.variations_per_content,
            'new_images_list': new_images,
            'updates_list': updates,
            'needs_generation': total_pieces > 0
        }
    
    def check_images_inventory(self, parsed_content_file: str = "generated/all_content.json", 
                             ) -> None:
        """Display inventory of image status by content file."""
        # Load content data
        if not Path(parsed_content_file).exists():
            print(f"❌ Content file not found: {parsed_content_file}")
            return
        
        with open(parsed_content_file, 'r') as f:
            content_list = json.load(f)
        
        if not content_list:
            print("📭 No content found")
            return
        
        # Get existing images and their metadata
        existing_images = list(self.images_dir.glob('*.png'))
        existing_metadata = {}
        
        for img_file in existing_images:
            metadata_file = self.metadata_dir / img_file.name.replace('.png', '_metadata.json')
            if metadata_file.exists():
                with open(metadata_file, 'r') as f:
                    metadata = json.load(f)
                    existing_metadata[img_file.name] = {
                        'style_name': metadata.get('style', {}).get('name', 'unknown'),
                        'style_approach': metadata.get('style', {}).get('approach', 'artistic')
                    }
        
        # Check each content piece
        for content in content_list:
            # Get the filename using utility function
            filename = self.get_base_filename_from_content(content)
            
            title = content['title']
            author = content['author']
            current_style = content.get('style_name', 'unknown')
            
            # Generate expected filenames for all variations
            base_filename = self.generate_image_filename(content, 1).replace('_v1.png', '')
            
            # Check if any variation exists and compare styles and content
            variations_exist = []
            style_mismatch = False
            content_change = content.get('content_changed', False)
            existing_style = 'unknown'
            
            for v in range(1, self.variations_per_content + 1):  # Check for configured variations
                var_filename = f"{base_filename}_v{v}.png"
                if var_filename in [img.name for img in existing_images]:
                    variations_exist.append(v)
                    
                    # Only check style consistency for v1 (primary variation)
                    # v2 and v3 are intentional variations with different styles
                    if v == 1 and var_filename in existing_metadata:
                        metadata_style = existing_metadata[var_filename]['style_name']
                        existing_style = metadata_style
                        if metadata_style != current_style:
                            style_mismatch = True
            
            # Determine status
            if not variations_exist:
                status = "🆕 NEEDS NEW IMAGES"
                detail = f"no images exist (style: {current_style})"
            elif content_change:
                status = "🔄 NEEDS UPDATE"
                detail = f"content changed → new style: {current_style}"
            elif style_mismatch:
                status = "🔄 NEEDS UPDATE"
                detail = f"style change: {existing_style} → {current_style}"
            else:
                status = "✅ CURRENT"
                detail = f"{self.variations_per_content} variations with {current_style} style"
            
            # Display the inventory line with clean filename focus (per filename refactoring plan)
            print(f"{filename:<40} │ {status:<15} │ {detail}")
            if status != "✅ CURRENT":
                print()
        
    def get_base_filename_from_content(self, content_data: Dict[str, Any]) -> str:
        """Extract base filename from content_file field"""
        content_file = content_data.get('content_file', '')
        if content_file.startswith('content/inspiration/'):
            return content_file.replace('content/inspiration/', '').replace('.md', '')
        else:
            # Fallback for unexpected paths
            return Path(content_file).stem if content_file else 'unknown'
    
    def generate_image_filename(self, content_data: Dict[str, Any], variation: int = 1) -> str:
        """Generate a consistent filename based on content file name."""
        base_filename = self.get_base_filename_from_content(content_data)
        return f"{base_filename}_v{variation}.png"
    
    def check_existing_image(self, filename: str) -> bool:
        """Check if an image already exists."""
        image_path = self.images_dir / filename
        return image_path.exists()
    
    def identify_orphaned_images(self, parsed_content_file: str = "generated/all_content.json", 
                               ) -> Dict[str, Any]:
        """Identify images that should be removed (orphaned images)."""
        # Load current content data
        if not Path(parsed_content_file).exists():
            return {"error": f"Content file not found: {parsed_content_file}"}
        
        with open(parsed_content_file, 'r') as f:
            content_list = json.load(f)
        
        # Get all existing images
        existing_images = list(self.images_dir.glob('*.png'))
        existing_metadata = list(self.metadata_dir.glob('*_metadata.json'))
        
        # Build set of expected filenames from current content
        expected_files = set()
        for content in content_list:
            base_filename = self.get_base_filename_from_content(content)
            for v in range(1, self.variations_per_content + 1):
                expected_files.add(f"{base_filename}_v{v}.png")
                expected_files.add(f"{base_filename}_v{v}_metadata.json")
        
        # Find orphaned images (exist but not expected)
        missing_content = []
        excess_variations = []
        total_size = 0
        
        for img_file in existing_images:
            if img_file.name not in expected_files:
                # Determine if it's missing content or excess variation
                base_name = img_file.stem.rsplit('_v', 1)[0] if '_v' in img_file.stem else img_file.stem
                variation_match = False
                
                # Check if base content exists but this is an excess variation
                for content in content_list:
                    content_base = self.get_base_filename_from_content(content)
                    if base_name == content_base:
                        excess_variations.append({
                            "filename": img_file.name,
                            "reason": f"excess variation (need only {self.variations_per_content})"
                        })
                        variation_match = True
                        break
                
                if not variation_match:
                    missing_content.append({
                        "filename": img_file.name,
                        "reason": "content file missing"
                    })
                
                # Calculate file size
                try:
                    total_size += img_file.stat().st_size
                except:
                    pass
        
        # Find orphaned metadata files
        orphaned_metadata = []
        for meta_file in existing_metadata:
            if meta_file.name not in expected_files:
                orphaned_metadata.append(meta_file.name)
        
        # Format size for display
        if total_size < 1024:
            size_str = f"{total_size} bytes"
        elif total_size < 1024 * 1024:
            size_str = f"{total_size / 1024:.1f} KB"
        else:
            size_str = f"{total_size / (1024 * 1024):.1f} MB"
        
        return {
            "missing_content": missing_content,
            "excess_variations": excess_variations,
            "orphaned_metadata": orphaned_metadata,
            "total_orphaned": len(missing_content) + len(excess_variations),
            "total_metadata_orphaned": len(orphaned_metadata),
            "estimated_space_saved": size_str,
            "variations_per_content": self.variations_per_content
        }
    
    def cleanup_orphaned_images(self, dry_run: bool = True, archive_before_delete: bool = True,
                              ) -> Dict[str, Any]:
        """Remove orphaned images with safety measures."""
        import shutil
        
        # First identify what needs to be cleaned up
        orphaned_result = self.identify_orphaned_images()
        
        if "error" in orphaned_result:
            return orphaned_result
        
        if orphaned_result["total_orphaned"] == 0 and orphaned_result["total_metadata_orphaned"] == 0:
            return {
                "status": "no_action_needed",
                "message": "No orphaned images found",
                "removed_images": [],
                "removed_metadata": [],
                "archive_location": None
            }
        
        # Collect all files to remove
        files_to_remove = []
        
        # Add orphaned image files
        for item in orphaned_result["missing_content"] + orphaned_result["excess_variations"]:
            img_path = self.images_dir / item["filename"]
            if img_path.exists():
                files_to_remove.append({"path": img_path, "type": "image", "reason": item["reason"]})
        
        # Add orphaned metadata files
        for meta_filename in orphaned_result["orphaned_metadata"]:
            meta_path = self.metadata_dir / meta_filename
            if meta_path.exists():
                files_to_remove.append({"path": meta_path, "type": "metadata", "reason": "orphaned metadata"})
        
        archive_location = None
        
        if dry_run:
            return {
                "status": "dry_run",
                "message": f"Would remove {len(files_to_remove)} files",
                "files_to_remove": [{"filename": f["path"].name, "type": f["type"], "reason": f["reason"]} for f in files_to_remove],
                "estimated_space_saved": orphaned_result["estimated_space_saved"],
                "archive_location": "would create archive" if archive_before_delete else None
            }
        
        # Archive before deletion if requested
        if archive_before_delete and files_to_remove:
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
            archive_folder = self.archive_dir / f"cleanup_{timestamp}"
            archive_folder.mkdir(exist_ok=True)
            
            # Create subfolders
            archive_images = archive_folder / "images"
            archive_metadata = archive_folder / "metadata"
            archive_images.mkdir(exist_ok=True)
            archive_metadata.mkdir(exist_ok=True)
            
            # Archive files before deletion
            for file_info in files_to_remove:
                if file_info["type"] == "image":
                    dest = archive_images / file_info["path"].name
                else:
                    dest = archive_metadata / file_info["path"].name
                
                try:
                    shutil.copy2(str(file_info["path"]), str(dest))
                except Exception as e:
                    print(f"Warning: Could not archive {file_info['path'].name}: {e}")
            
            archive_location = str(archive_folder)
            print(f"✓ Archived {len(files_to_remove)} files to {archive_folder}")
        
        # Actually remove the files
        removed_images = []
        removed_metadata = []
        errors = []
        
        for file_info in files_to_remove:
            try:
                file_info["path"].unlink()
                if file_info["type"] == "image":
                    removed_images.append(file_info["path"].name)
                else:
                    removed_metadata.append(file_info["path"].name)
            except Exception as e:
                errors.append(f"Failed to remove {file_info['path'].name}: {e}")
        
        result = {
            "status": "completed",
            "message": f"Removed {len(removed_images)} images and {len(removed_metadata)} metadata files",
            "removed_images": removed_images,
            "removed_metadata": removed_metadata,
            "archive_location": archive_location,
            "estimated_space_saved": orphaned_result["estimated_space_saved"]
        }
        
        if errors:
            result["errors"] = errors
            result["status"] = "completed_with_errors"
        
        return result
    
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
                'model': self.MODEL_NAME,
                'model_display': self.MODEL_DISPLAY_NAME,
                'prompt': content_data['prompt']['text'],
                'prompt_length': len(content_data['prompt']['text']),
                'dimensions': '1024x1024',
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
                model=self.MODEL_NAME,
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
        import random
        import sys
        import os
        
        # Add scripts directory to Python path for imports
        script_dir = os.path.dirname(os.path.abspath(__file__))
        if script_dir not in sys.path:
            sys.path.insert(0, script_dir)
        
        from content_parser import ContentParser
        
        results = []
        parser = ContentParser()
        
        # Get the current style info
        original_style = content_data.get('style_name', 'unknown')
        original_approach = content_data.get('style_approach', 'painting_technique')
        
        # Get available styles
        painting_styles = list(parser.styles_data.get('painting_technique_styles', {}).keys())
        storytelling_styles = list(parser.styles_data.get('visual_storytelling_techniques', {}).keys())
        
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
                
                # Add vibe guidance if available
                if variation_content.get('vibe'):
                    vibes = variation_content['vibe']
                    if isinstance(vibes, list):
                        vibe_text = ', '.join(vibes)
                    else:
                        vibe_text = str(vibes)
                    prompt_parts.append(f"Capturing the vibe of {vibe_text}")
                
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
        print(f"Looking for parsed content file: {parsed_file}")
        
        if not parsed_file.exists():
            print(f"Parsed content file not found: {parsed_file}")
            print("Running content parser first...")
            import sys
            
            # Add scripts directory to Python path for imports
            script_dir = parsed_file.parent.parent / "scripts"
            if str(script_dir) not in sys.path:
                sys.path.insert(0, str(script_dir))
            
            from content_parser import ContentParser
            parser = ContentParser()
            all_content = parser.parse_all_content()
            if not all_content:
                raise ValueError("No content found to generate images from")
            print(f"Generated {len(all_content)} content items from parser")
        else:
            print(f"Loading content from existing file: {parsed_file}")
            with open(parsed_file, 'r') as f:
                content = json.load(f)
                # Handle both single content and list of content
                all_content = [content] if isinstance(content, dict) else content
                print(f"Loaded {len(all_content)} content items from file")
        
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
    parser.add_argument('--archive-and-regenerate', action='store_true',
                       help='Archive existing images then regenerate all')
    parser.add_argument('--check-styles', action='store_true',
                       help='Check which content needs images generated')
    parser.add_argument('--preview-analysis', action='store_true',
                       help='Detailed analysis with cost calculations for preview script')
    parser.add_argument('--check-images', action='store_true',
                       help='Inventory image status by content file')
    parser.add_argument('--check-orphaned', action='store_true',
                       help='Check for orphaned images that should be removed')
    parser.add_argument('--cleanup-orphaned', action='store_true',
                       help='Remove orphaned images (with confirmation)')
    parser.add_argument('--dry-run', action='store_true',
                       help='Show what would be removed without acting (for cleanup operations)')
    parser.add_argument('--content-file', default='generated/all_content.json',
                       help='Path to parsed content JSON file')
    parser.add_argument('--variations', type=int, default=3,
                       help='Number of variations to generate per content piece (default: 3)')
    
    args = parser.parse_args()
    
    # Check for API key (not needed for analysis-only operations)
    api_key = os.environ.get('GEMINI_API_KEY')
    analysis_only_ops = [args.check_styles, args.preview_analysis, args.check_images, 
                        args.check_orphaned, (args.cleanup_orphaned and args.dry_run)]
    if not api_key and not any(analysis_only_ops):
        print("❌ Error: GEMINI_API_KEY environment variable not set")
        print("Please set your Gemini API key before running image generation")
        return 1
    
    try:
        # Handle style check option
        if args.check_styles:
            generator = ImageGenerator(check_only=True)
            print("Style Check Report")
            print("=" * 40)
            
            check_result = generator.check_new_styles(args.content_file)
            
            if "error" in check_result:
                print(f"❌ {check_result['error']}")
                return 1
            
            print(f"📊 Content pieces: {check_result['content_pieces']}")
            print(f"🖼️  Existing images: {check_result['existing_images']}")
            
            if check_result['needs_generation']:
                # Separate new images from updates
                new_images = [item for item in check_result['needs_generation'] if item.get('type') == 'new']
                updates = [item for item in check_result['needs_generation'] if item.get('type') == 'update']
                
                if new_images:
                    print(f"\n🆕 Content needing new images:")
                    for item in new_images:
                        print(f"   • \"{item['title']}\" by {item['author']} ({item['reason']})")
                
                if updates:
                    print(f"\n🔄 Content needing image updates:")
                    for item in updates:
                        reason_detail = f"{item['existing_style']} → {item['expected_style']}"
                        print(f"   • \"{item['title']}\" by {item['author']} ({reason_detail})")
                
                if new_images and updates:
                    print(f"\nRun './bin/preview-and-check.sh' to generate {len(new_images)} new + {len(updates)} updated images")
                elif new_images:
                    print(f"\nRun './bin/generate-new.sh' to generate {len(new_images)} missing images")
                else:
                    print(f"\nRun './bin/preview-and-check.sh' to update {len(updates)} images with new styles")
            else:
                print("\n✅ All content has generated images with current styles!")
            
            return 0
        
        # Handle preview analysis option
        if args.preview_analysis:
            generator = ImageGenerator(check_only=True)
            analysis = generator.preview_analysis(args.content_file)
            
            if "error" in analysis:
                print(f"❌ {analysis['error']}")
                return 1
            
            # Output structured data for bash script consumption
            print(json.dumps(analysis, indent=2))
            return 0
        
        # Handle check images inventory option
        if args.check_images:
            generator = ImageGenerator(check_only=True)
            generator.check_images_inventory(args.content_file)
            return 0
        
        # Handle orphaned image check
        if args.check_orphaned:
            generator = ImageGenerator(check_only=True)
            print("Orphaned Images Check")
            print("=" * 40)
            
            orphaned_result = generator.identify_orphaned_images(
                parsed_content_file=args.content_file,
                            )
            
            if "error" in orphaned_result:
                print(f"❌ {orphaned_result['error']}")
                return 1
            
            total_orphaned = orphaned_result["total_orphaned"]
            total_metadata = orphaned_result["total_metadata_orphaned"]
            
            if total_orphaned == 0 and total_metadata == 0:
                print("✅ No orphaned images found")
                return 0
            
            print(f"🗑️  Found {total_orphaned} orphaned images and {total_metadata} orphaned metadata files")
            print(f"💾 Estimated space to reclaim: {orphaned_result['estimated_space_saved']}")
            print()
            
            if orphaned_result["missing_content"]:
                print("📂 Images for deleted content:")
                for item in orphaned_result["missing_content"]:
                    print(f"  • {item['filename']} ({item['reason']})")
                print()
            
            if orphaned_result["excess_variations"]:
                print("🔢 Excess variation images:")
                for item in orphaned_result["excess_variations"]:
                    print(f"  • {item['filename']} ({item['reason']})")
                print()
            
            if orphaned_result["orphaned_metadata"]:
                print("📄 Orphaned metadata files:")
                for filename in orphaned_result["orphaned_metadata"]:
                    print(f"  • {filename}")
            
            print(f"💡 Run with --cleanup-orphaned to remove these files")
            print(f"💡 Use --dry-run to preview what would be removed")
            return 0
        
        # Handle orphaned image cleanup
        if args.cleanup_orphaned:
            generator = ImageGenerator(check_only=args.dry_run)
            
            if args.dry_run:
                print("Orphaned Images Cleanup (DRY RUN)")
                print("=" * 40)
            else:
                print("Orphaned Images Cleanup")
                print("=" * 40)
            
            cleanup_result = generator.cleanup_orphaned_images(
                dry_run=args.dry_run,
                archive_before_delete=True,
                            )
            
            if "error" in cleanup_result:
                print(f"❌ {cleanup_result['error']}")
                return 1
            
            if cleanup_result["status"] == "no_action_needed":
                print("✅ No orphaned images found")
                return 0
            
            if cleanup_result["status"] == "dry_run":
                print(f"🔍 Would remove {len(cleanup_result['files_to_remove'])} files:")
                for file_info in cleanup_result["files_to_remove"]:
                    print(f"  • {file_info['filename']} ({file_info['type']}) - {file_info['reason']}")
                print()
                print(f"💾 Estimated space to reclaim: {cleanup_result['estimated_space_saved']}")
                if cleanup_result["archive_location"]:
                    print(f"📁 Would archive to: generated/archive/cleanup_TIMESTAMP/")
                print()
                print("💡 Run without --dry-run to actually remove files")
                return 0
            else:
                # Actual cleanup performed
                print(f"✅ {cleanup_result['message']}")
                if cleanup_result["archive_location"]:
                    print(f"📁 Files archived to: {cleanup_result['archive_location']}")
                print(f"💾 Space reclaimed: {cleanup_result['estimated_space_saved']}")
                
                if "errors" in cleanup_result:
                    print("\n⚠️  Some errors occurred:")
                    for error in cleanup_result["errors"]:
                        print(f"  • {error}")
                
                return 0
        
        # For all other operations, create generator normally
        generator = ImageGenerator()
        
        print("Nano Banana Image Generator")
        print("=" * 60)
        print(f"API Key: {api_key[:10]}...")
        print(f"Model: {generator.MODEL_DISPLAY_NAME}")
        print(f"Cost per image: ${generator.cost_per_image}")
        print(f"Variations: {args.variations}")
        print(f"Content file: {args.content_file}")
        
        # Handle archive option
        if args.archive_and_regenerate:
            print("Mode: Archive existing images and regenerate all")
            generator.archive_existing_images()
            force_mode = True
        else:
            force_mode = args.force_all
            mode_desc = "Force regenerate all" if force_mode else "Generate only missing images"
            print(f"Mode: {mode_desc}")
        
        print()
        
        # Generate images
        results = generator.generate_from_parsed_content(
            parsed_content_file=args.content_file,
            force=force_mode,
            variations=args.variations
        )
        
    except Exception as e:
        print(f"Error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())