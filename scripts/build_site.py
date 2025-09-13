#!/usr/bin/env python3
"""
Site Builder for rennie.org Inspiration Platform - Refactored

Generates a static single-page application that displays inspiring quotes
with AI-generated artwork in a breathing, meditative interface.

Features:
- Modular template system
- Responsive design (desktop: 25% quote + 75% image, mobile: stacked)
- Dynamic color adaptation based on image brightness
- Carousel functionality for multiple image variations
- Breathing animation with configurable timing
- Ken Burns effects and touch gesture support
"""

import json
import os
import shutil
from pathlib import Path
from typing import Dict, List, Any
from PIL import Image
import numpy as np


def get_base_filename_from_content(content_data: Dict[str, Any]) -> str:
    """Extract base filename from content_file field"""
    content_file = content_data.get('content_file', '')
    if content_file.startswith('content/inspiration/'):
        return content_file.replace('content/inspiration/', '').replace('.md', '')
    else:
        # Fallback for unexpected paths
        return Path(content_file).stem if content_file else 'unknown'


def load_parsed_content() -> List[Dict[str, Any]]:
    """Load parsed content data from generated/all_content.json"""
    content_file = Path("generated/all_content.json")
    
    if not content_file.exists():
        raise FileNotFoundError(f"Parsed content not found at {content_file}")
    
    with open(content_file, 'r') as f:
        content = json.load(f)
    
    # Convert single content item to list format (for backward compatibility)
    if isinstance(content, dict):
        return [content]
    return content


def get_image_paths(content_item: Dict[str, Any]) -> List[str]:
    """Get all available image variations for content"""
    # Use the same base filename logic as generate_images.py
    base_filename = get_base_filename_from_content(content_item)
    
    # Look for variation files
    image_paths = []
    
    # Check for variations (v1, v2, v3, etc.)
    for variation in range(1, 6):  # Check up to 5 variations
        filename = f"{base_filename}_v{variation}.png"
        full_path = f"generated/images/{filename}"
        
        if Path(full_path).exists():
            image_paths.append(f"images/{filename}")  # Relative path for web
    
    # Fallback to old single-image format if no variations found
    if not image_paths:
        old_filename = f"{base_filename}.png"
        old_path = f"generated/images/{old_filename}"
        if Path(old_path).exists():
            image_paths.append(f"images/{old_filename}")
    
    return image_paths


def get_image_path(content_item: Dict[str, Any]) -> str:
    """Legacy function - returns first available image"""
    paths = get_image_paths(content_item)
    return f"generated/{paths[0]}" if paths else ""


def load_image_metadata(image_filename: str) -> Dict[str, Any]:
    """Load metadata for a generated image"""
    metadata_path = Path("generated/metadata") / image_filename.replace('.png', '_metadata.json')
    
    if metadata_path.exists():
        with open(metadata_path, 'r') as f:
            return json.load(f)
    
    return None


def analyze_image_brightness(image_path: str) -> Dict[str, Any]:
    """Analyze image brightness to determine optimal text panel colors"""
    try:
        image = Image.open(image_path)
        image = image.convert('RGB')
        
        # Convert to numpy array and calculate average brightness
        img_array = np.array(image)
        
        # Calculate weighted brightness (luminance formula)
        brightness = np.mean(img_array[:,:,0] * 0.299 + 
                           img_array[:,:,1] * 0.587 + 
                           img_array[:,:,2] * 0.114)
        
        # Normalize to 0-1 range
        brightness_normalized = brightness / 255.0
        
        # Determine if image is predominantly light or dark
        is_light = brightness_normalized > 0.5
        
        return {
            "brightness": round(brightness_normalized, 3),
            "is_light": is_light,
            "text_color": "#2c3e50" if is_light else "#ecf0f1",
            "background_color": "#f8f9fa" if is_light else "#34495e",
            "accent_color": "#3498db" if is_light else "#e74c3c"
        }
        
    except Exception as e:
        print(f"Warning: Could not analyze image brightness for {image_path}: {e}")
        # Default to dark theme
        return {
            "brightness": 0.5,
            "is_light": False,
            "text_color": "#ecf0f1",
            "background_color": "#34495e", 
            "accent_color": "#e74c3c"
        }


def load_template(template_name: str) -> str:
    """Load a template file from the templates directory"""
    template_path = Path(__file__).parent / "templates" / template_name
    
    if not template_path.exists():
        raise FileNotFoundError(f"Template not found: {template_path}")
    
    return template_path.read_text(encoding='utf-8')


def create_combined_javascript() -> str:
    """Combine carousel and app JavaScript into a single file"""
    carousel_js = load_template("carousel.js")
    app_js = load_template("app.js")
    
    # Combine with a header comment
    combined = f"""/**
 * Breathing Inspiration Experience with Carousel
 * JavaScript for dynamic color adaptation, content rotation, and carousel functionality
 */

{carousel_js}

{app_js}
"""
    return combined


def build_site():
    """Main build function that generates the complete static site"""
    print("🏗️  Building rennie.org inspiration site (refactored)...")
    
    # Create output directory
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    
    # Load parsed content
    try:
        content_items = load_parsed_content()
        print(f"✅ Loaded {len(content_items)} content items")
    except FileNotFoundError as e:
        print(f"❌ Error: {e}")
        print("   Run scripts/content_parser.py first to generate parsed content")
        return False
    
    # Process content and analyze images
    processed_content = []
    images_dir = output_dir / "images"
    images_dir.mkdir(exist_ok=True)
    
    for content in content_items:
        base_filename = get_base_filename_from_content(content)
        print(f"📝 Processing: {base_filename}.md")
        
        # Get all image variations
        image_paths = get_image_paths(content)
        content['images'] = []
        
        if image_paths:
            for img_path in image_paths:
                # Full path for analysis
                full_path = f"generated/{img_path}"
                
                if Path(full_path).exists():
                    # Copy image to output directory
                    image_filename = Path(full_path).name
                    output_image_path = images_dir / image_filename
                    shutil.copy2(full_path, output_image_path)
                    
                    # Analyze image brightness
                    brightness_data = analyze_image_brightness(str(full_path))
                    
                    # Load metadata for the image
                    metadata = load_image_metadata(image_filename)
                    
                    # Add to images array
                    image_data = {
                        "path": img_path,
                        "filename": image_filename,
                        "brightness_analysis": brightness_data
                    }
                    
                    # Include generation metadata if available
                    if metadata:
                        image_data["generation"] = metadata.get("generation", {})
                        image_data["style"] = metadata.get("style", {})
                    
                    content['images'].append(image_data)
                    
                    print(f"   🖼️  Image: {image_filename} (brightness: {brightness_data['brightness']})")
            
            # Use first image's brightness for backward compatibility
            if content['images']:
                content['brightness_analysis'] = content['images'][0]['brightness_analysis']
            else:
                content['brightness_analysis'] = {
                    "brightness": 0.5,
                    "is_light": False,
                    "text_color": "#ecf0f1",
                    "background_color": "#34495e",
                    "accent_color": "#e74c3c"
                }
        else:
            print(f"   ⚠️  No images found")
            content['brightness_analysis'] = {
                "brightness": 0.5,
                "is_light": False,
                "text_color": "#ecf0f1",
                "background_color": "#34495e",
                "accent_color": "#e74c3c"
            }
        
        processed_content.append(content)
    
    # Generate HTML file from template
    html_content = load_template("index.html")
    (output_dir / "index.html").write_text(html_content, encoding='utf-8')
    print("✅ Generated index.html")
    
    # Generate CSS file from template
    css_content = load_template("style.css")
    (output_dir / "style.css").write_text(css_content, encoding='utf-8')
    print("✅ Generated style.css")
    
    # Generate combined JavaScript file
    js_content = create_combined_javascript()
    (output_dir / "script.js").write_text(js_content, encoding='utf-8')
    print("✅ Generated script.js (combined)")
    
    # Generate content JSON API (convert numpy types to native Python types)
    def convert_numpy_types(obj):
        if hasattr(obj, 'item'):  # numpy scalar
            return obj.item()
        elif isinstance(obj, dict):
            return {k: convert_numpy_types(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [convert_numpy_types(item) for item in obj]
        return obj
    
    serializable_content = convert_numpy_types(processed_content)
    content_json = json.dumps(serializable_content, indent=2, ensure_ascii=False)
    (output_dir / "content.json").write_text(content_json, encoding='utf-8')
    print("✅ Generated content.json API")
    
    # Generate metadata summary
    build_summary = {
        "build_timestamp": "2025-09-11T00:00:00Z",
        "build_type": "refactored_modular",
        "content_count": len(processed_content),
        "images_included": sum(1 for c in processed_content if Path(get_image_path(c)).exists()),
        "total_size_mb": round(sum(f.stat().st_size for f in Path(output_dir).rglob("*") if f.is_file()) / (1024*1024), 2),
        "content_items": [
            {
                "title": c['title'],
                "author": c['author'],
                "style": c.get('style_name', 'unknown'),
                "has_image": Path(get_image_path(c)).exists(),
                "brightness": c['brightness_analysis']['brightness']
            }
            for c in processed_content
        ]
    }
    
    (output_dir / "build_summary.json").write_text(
        json.dumps(build_summary, indent=2, ensure_ascii=False), 
        encoding='utf-8'
    )
    
    print(f"\n🎉 Site build complete (refactored)!")
    print(f"   📊 Content items: {build_summary['content_count']}")
    print(f"   🖼️  Images: {build_summary['images_included']}")
    print(f"   💾 Total size: {build_summary['total_size_mb']} MB")
    print(f"   📁 Output directory: {output_dir.absolute()}")
    print(f"\n🌐 Open {output_dir.absolute()}/index.html in your browser to preview")
    
    return True


if __name__ == "__main__":
    import sys
    
    # Change to project root directory
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)
    
    success = build_site()
    sys.exit(0 if success else 1)