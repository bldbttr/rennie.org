#!/bin/bash
# Force regenerate all images (for style changes)

cd "$(dirname "$0")/.."

echo "🔄 Regenerating all images..."

# Activate virtual environment
source ~/dev/.venv/bin/activate

# Force regenerate all images
python scripts/generate_images.py --force-all --variations 3

echo "✅ Regenerated all images"