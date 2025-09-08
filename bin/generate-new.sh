#!/bin/bash
# Generate images for content that doesn't have them yet

cd "$(dirname "$0")/.."

echo "🖼️  Generating images for new content..."

# Activate virtual environment
source ~/dev/.venv/bin/activate

# Generate new images only
python scripts/generate_images.py --new-only

echo "✅ Generated images for new content"