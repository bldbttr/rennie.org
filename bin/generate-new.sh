#!/bin/bash
# Generate images for content that doesn't have them yet

cd "$(dirname "$0")/.."

echo "🖼️  Generating images for new content..."

# Activate virtual environment
source ~/dev/.venv/bin/activate

# Parse content first (to get all content)
echo "📝 Parsing content files..."
python scripts/content_parser.py
if [ $? -ne 0 ]; then
    echo "❌ Content parsing failed"
    exit 1
fi

# Generate new images only (using all_content.json)
python scripts/generate_images.py --new-only --variations 3

echo "✅ Generated images for new content"