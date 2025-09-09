#!/bin/bash
# Local deployment script - for when GitHub Actions is being difficult
# or when you just want to deploy NOW without waiting 15 minutes

echo "🚀 Local Deployment (The Simple Way)"
echo "===================================="

# Navigate to project root
cd "$(dirname "$0")/.."

# Activate virtual environment
echo "🐍 Activating virtual environment..."
source ~/dev/.venv/bin/activate

# Check for API key
if [ -z "$GEMINI_API_KEY" ]; then
    echo "⚠️  Warning: GEMINI_API_KEY not set (image generation will skip)"
fi

# Parse all content
echo "📝 Parsing content..."
python scripts/content_parser.py
if [ $? -ne 0 ]; then
    echo "❌ Content parsing failed"
    exit 1
fi

# Generate missing images (if API key is available)
if [ -n "$GEMINI_API_KEY" ]; then
    echo "🎨 Generating missing images..."
    python scripts/generate_images.py --new-only --variations 3
else
    echo "⏭️  Skipping image generation (no API key)"
fi

# Build the site
echo "🏗️  Building static site..."
python scripts/build_site.py
if [ $? -ne 0 ]; then
    echo "❌ Site build failed"
    exit 1
fi

# Deploy to DreamHost
echo "📤 Deploying to DreamHost..."
rsync -avz --delete output/ rennie@iad1-shared-e1-05.dreamhost.com:~/rennie.org/

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ DEPLOYED SUCCESSFULLY!"
    echo "🌐 Site: https://rennie.org"
    echo "⏱️  Total time: ~2 minutes (vs ~15 with GitHub Actions)"
    echo ""
    echo "Note: CDN cache may take 1-2 minutes to update"
else
    echo "❌ Deployment failed"
    exit 1
fi