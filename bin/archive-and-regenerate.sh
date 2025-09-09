#!/bin/bash
# Archive existing images and regenerate all with new styles
# Use this when you've added new styles or want fresh images

echo "🗂️  Archive and Regenerate All Images"
echo "======================================"

# Navigate to project root
cd "$(dirname "$0")/.."

# Activate virtual environment
echo "🐍 Activating virtual environment..."
source ~/dev/.venv/bin/activate

# Check if GEMINI_API_KEY is set
if [ -z "$GEMINI_API_KEY" ]; then
    echo "❌ Error: GEMINI_API_KEY environment variable not set"
    exit 1
fi

# Parse all content first (to get latest content + styles)
echo "📝 Parsing content files..."
python scripts/content_parser.py
if [ $? -ne 0 ]; then
    echo "❌ Content parsing failed"
    exit 1
fi

# Archive existing images and regenerate all (with 3 variations)
echo "🎨 Archiving existing images and generating new ones..."
python scripts/generate_images.py --archive-and-regenerate --variations 3

if [ $? -eq 0 ]; then
    echo "✅ Archive and regeneration completed successfully!"
    echo "💰 Cost: Regenerated all content with 3 variations each"
    echo "📁 Old images archived in generated/archive/"
else
    echo "❌ Image generation failed"
    exit 1
fi