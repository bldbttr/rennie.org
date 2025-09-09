#!/bin/bash

# Check what images need generation due to content or style changes
# Uses existing change detection from generate_images.py

set -e

cd "$(dirname "$0")/.."

echo "🔍 ANALYZING CONTENT FOR IMAGE GENERATION NEEDS"
echo "=============================================="

# First parse content to ensure we have latest data
echo "📝 Parsing content files..."
python scripts/content_parser.py

echo ""
echo "🎨 CHECKING FOR IMAGE GENERATION NEEDS"
echo "====================================="

# Use the existing check-styles functionality
python scripts/generate_images.py --check-styles