#!/bin/bash
# Check if any content needs image generation
# Useful for seeing what content is missing images

echo "🎨 Checking Content Style Status"
echo "================================"

# Navigate to project root
cd "$(dirname "$0")/.."

# Activate virtual environment
source ~/dev/.venv/bin/activate

# Parse content first to get latest data
echo "📝 Parsing content files..."
python scripts/content_parser.py

# Check styles status
echo ""
python scripts/generate_images.py --check-styles