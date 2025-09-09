#!/bin/bash

# Enhanced Local Preview with Cost Control and Verbose Progress
# This script generates images locally, shows costs, and creates immediate preview
# The same images will be used in deployment for consistency

set -e

cd "$(dirname "$0")/.."

echo "🔍 ANALYZING CONTENT AND IMAGE REQUIREMENTS"
echo "============================================="

# Check what content exists
CONTENT_COUNT=$(find content/inspiration -name "*.md" | wc -l | tr -d ' ')
echo "📄 Found $CONTENT_COUNT content files"

# Check what images exist
if [ -d "generated/images" ]; then
    IMAGE_COUNT=$(find generated/images -name "*.png" | wc -l | tr -d ' ')
    echo "🖼️  Found $IMAGE_COUNT existing images"
else
    IMAGE_COUNT=0
    echo "🖼️  No images directory found (will create)"
fi

echo ""
echo "🧮 CALCULATING IMAGE GENERATION NEEDS"
echo "====================================="

# First parse content to ensure we have latest data
echo "📝 Parsing content files..."
python scripts/content_parser.py > /dev/null 2>&1

# Use the existing sophisticated change detection system
GENERATION_ANALYSIS=$(python scripts/generate_images.py --check-styles 2>/dev/null | tail -n +3)

# Extract information from the analysis
CONTENT_COUNT=$(echo "$GENERATION_ANALYSIS" | grep "📊 Content pieces:" | sed 's/.*: //')
EXISTING_IMAGES=$(echo "$GENERATION_ANALYSIS" | grep "🖼️  Existing images:" | sed 's/.*: //')

if echo "$GENERATION_ANALYSIS" | grep -q "All content has generated images!"; then
    NEEDS_GENERATION=0
    echo "📊 Content pieces: $CONTENT_COUNT"
    echo "🖼️  Existing images: $EXISTING_IMAGES"
    echo "✅ All content already has images"
    echo ""
    echo "🔍 Checking for style changes that require regeneration..."
    
    # Check if any content has changed styles since generation
    if echo "$GENERATION_ANALYSIS" | grep -q "Content needing image generation:"; then
        echo "⚡ Style changes detected - some images need regeneration"
        NEEDS_UPDATES=1
    else
        echo "✅ All images are current with content and styles"
        NEEDS_UPDATES=0
    fi
else
    # Extract list of content needing generation
    NEEDS_LIST=$(echo "$GENERATION_ANALYSIS" | sed -n '/🎨 Content needing image generation:/,/^$/p' | grep "   •" | sed 's/   • //')
    NEEDS_GENERATION=$(echo "$NEEDS_LIST" | wc -l | tr -d ' ')
    NEEDS_UPDATES=0
    
    echo "📊 Analysis Results:"
    echo "   Content pieces: $CONTENT_COUNT"
    echo "   Existing images: $EXISTING_IMAGES"
    echo "   Missing images: $NEEDS_GENERATION"
    echo ""
    echo "🎨 Content needing new images:"
    echo "$NEEDS_LIST" | sed 's/^/   /'
fi

# Calculate total generation needed (new + updates)
TOTAL_GENERATION=$((NEEDS_GENERATION + NEEDS_UPDATES * 3)) # 3 variations per update

if [ $TOTAL_GENERATION -gt 0 ]; then
    echo ""
    echo "💰 COST ANALYSIS"
    echo "================"
    
    if [ $NEEDS_GENERATION -gt 0 ]; then
        NEW_COST=$(python3 -c "print(f'{$NEEDS_GENERATION * 3 * 0.039:.2f}')")
        echo "🆕 New images: $NEEDS_GENERATION content pieces × 3 variations = $(($NEEDS_GENERATION * 3)) images"
        echo "   Cost: \$$NEW_COST"
    fi
    
    if [ $NEEDS_UPDATES -gt 0 ]; then
        UPDATE_COST=$(python3 -c "print(f'{$NEEDS_UPDATES * 3 * 0.039:.2f}')")
        echo "🔄 Updated images: $NEEDS_UPDATES content pieces × 3 variations = $(($NEEDS_UPDATES * 3)) images"
        echo "   Cost: \$$UPDATE_COST"
    fi
    
    TOTAL_COST=$(python3 -c "print(f'{$TOTAL_GENERATION * 0.039:.2f}')")
    echo "📊 TOTAL: $TOTAL_GENERATION images for \$$TOTAL_COST"
    
    echo ""
    echo "🤔 APPROVAL REQUIRED"
    echo "==================="
    echo "Generate $TOTAL_GENERATION images for approximately \$$TOTAL_COST?"
    
    if [ $NEEDS_GENERATION -gt 0 ] && [ $NEEDS_UPDATES -gt 0 ]; then
        echo "   • $((NEEDS_GENERATION * 3)) new images for missing content"
        echo "   • $((NEEDS_UPDATES * 3)) updated images for style changes"
    elif [ $NEEDS_GENERATION -gt 0 ]; then
        echo "   • $((NEEDS_GENERATION * 3)) new images for missing content"
    else
        echo "   • $((NEEDS_UPDATES * 3)) updated images for style changes"
    fi
    echo ""
    read -p "Proceed with generation? (yes/no): " approval
    
    if [ "$approval" != "yes" ] && [ "$approval" != "y" ]; then
        echo "❌ Generation cancelled by user"
        exit 1
    fi
    echo "✅ Generation approved!"
else
    echo ""
    echo "✅ No image generation needed"
fi

echo ""
echo "🎨 GENERATING IMAGES"
echo "==================="

if [ $TOTAL_GENERATION -gt 0 ]; then
    echo "🚀 Starting image generation for $TOTAL_GENERATION images..."
    echo "⏱️  Expected time: ~$((TOTAL_GENERATION * 8)) seconds"
    echo ""
    
    # Set API key and generate
    if [ -z "$GEMINI_API_KEY" ]; then
        echo "❌ GEMINI_API_KEY environment variable not set"
        echo "   Please set it with: export GEMINI_API_KEY=your_key_here"
        exit 1
    fi
    
    # Generate with progress output
    if [ $NEEDS_UPDATES -gt 0 ]; then
        # If we have updates, we need to archive and regenerate
        echo "🔄 Archiving old images and regenerating with new styles..."
        GEMINI_API_KEY="$GEMINI_API_KEY" python scripts/generate_images.py --archive-and-regenerate
    else
        # Just generate missing images
        echo "🆕 Generating missing images..."
        GEMINI_API_KEY="$GEMINI_API_KEY" python scripts/generate_images.py --new-only
    fi
    
    echo ""
    echo "✅ Image generation completed!"
    echo "💵 Actual cost: ~\$$TOTAL_COST"
else
    echo "⏭️  No generation needed"
fi

echo ""
echo "🏗️  BUILDING SITE FOR PREVIEW"
echo "============================="

echo "📦 Building static site with all content and images..."
python scripts/build_site.py

if [ -f "output/index.html" ]; then
    echo "✅ Site built successfully"
    echo "📁 Output ready in: $(pwd)/output/"
else
    echo "❌ Site build failed"
    exit 1
fi

echo ""
echo "👀 LAUNCHING LOCAL PREVIEW"
echo "========================="

echo "🌐 Opening site preview in your default browser..."
open output/index.html

echo ""
echo "📋 DEPLOYMENT READINESS SUMMARY"
echo "==============================="
echo "✅ Content parsed: $CONTENT_COUNT files"

if [ $TOTAL_GENERATION -gt 0 ]; then
    NEW_IMAGE_COUNT=$(find generated/images -name "*.png" | wc -l | tr -d ' ')
    echo "✅ Images ready: $NEW_IMAGE_COUNT total ($TOTAL_GENERATION newly generated)"
    echo "💵 Generation cost: ~\$$TOTAL_COST"
else
    echo "✅ Images ready: $EXISTING_IMAGES total (all current)"
fi

echo "✅ Site built: output/index.html ready"
echo "✅ Preview opened: Check your browser"
echo ""
echo "🚀 NEXT STEPS:"
echo "  1. Review the site preview that just opened"
echo "  2. If satisfied, commit and push:"
echo "     ./bin/commit-and-deploy.sh"
echo "     (or: git add . && git commit -m 'Update with new images' && git push)"
echo "  3. GitHub Actions will deploy these exact same images"
echo ""
echo "💡 The images you see locally are identical to what will be deployed!"
echo ""

if [ $TOTAL_GENERATION -gt 0 ]; then
    echo "📁 Generated images are now tracked in git (no longer gitignored)"
    echo "🏛️  Old images have been archived to generated/archive/ if any were replaced"
fi