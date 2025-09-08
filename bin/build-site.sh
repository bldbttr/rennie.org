#!/bin/bash
# Build the static site

cd "$(dirname "$0")/.."

echo "🏗️  Building static site..."

# Activate virtual environment
source ~/dev/.venv/bin/activate

# Build the site
python scripts/build_site.py

echo "✅ Site built successfully"
echo "🌐 Open output/index.html to preview"