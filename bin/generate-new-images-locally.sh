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

# Get structured analysis from Python
echo "🔍 Analyzing generation requirements..."
ANALYSIS_JSON=$(python scripts/generate_images.py --preview-analysis)

if [ $? -ne 0 ]; then
    echo "❌ Error analyzing content requirements"
    exit 1
fi

# Extract values using jq for reliable JSON parsing
CONTENT_PIECES=$(echo "$ANALYSIS_JSON" | python3 -c "import json, sys; data=json.load(sys.stdin); print(data['content_pieces'])")
EXISTING_IMAGES=$(echo "$ANALYSIS_JSON" | python3 -c "import json, sys; data=json.load(sys.stdin); print(data['existing_images'])")
NEW_PIECES=$(echo "$ANALYSIS_JSON" | python3 -c "import json, sys; data=json.load(sys.stdin); print(data['new_pieces'])")
UPDATE_PIECES=$(echo "$ANALYSIS_JSON" | python3 -c "import json, sys; data=json.load(sys.stdin); print(data['update_pieces'])")
TOTAL_PIECES=$(echo "$ANALYSIS_JSON" | python3 -c "import json, sys; data=json.load(sys.stdin); print(data['total_pieces'])")
TOTAL_IMAGES=$(echo "$ANALYSIS_JSON" | python3 -c "import json, sys; data=json.load(sys.stdin); print(data['total_images'])")
TOTAL_COST=$(echo "$ANALYSIS_JSON" | python3 -c "import json, sys; data=json.load(sys.stdin); print(f\"{data['total_cost']:.2f}\")")
NEEDS_GENERATION=$(echo "$ANALYSIS_JSON" | python3 -c "import json, sys; data=json.load(sys.stdin); print('true' if data['needs_generation'] else 'false')")

echo "📊 Analysis Results:"
echo "   Content pieces: $CONTENT_PIECES"
echo "   Existing images: $EXISTING_IMAGES"

if [ "$NEEDS_GENERATION" = "true" ]; then
    if [ $NEW_PIECES -gt 0 ]; then
        echo "   Missing images: $NEW_PIECES pieces"
    fi
    if [ $UPDATE_PIECES -gt 0 ]; then
        echo "   Update needed: $UPDATE_PIECES pieces"
    fi
    
    echo ""
    if [ $NEW_PIECES -gt 0 ]; then
        echo "🆕 Files needing new images:"
        echo "$ANALYSIS_JSON" | python3 -c "
import json, sys
data = json.load(sys.stdin)
for item in data['new_images_list']:
    print(f'   • {item[\"filename\"]}: 3 images')
"
    fi
    
    if [ $UPDATE_PIECES -gt 0 ]; then
        echo "🔄 Files needing image updates:"
        echo "$ANALYSIS_JSON" | python3 -c "
import json, sys
data = json.load(sys.stdin)
for item in data['updates_list']:
    print(f'   • {item[\"filename\"]}: 3 images')
"
    fi
    
    echo ""
    echo "💰 COST ANALYSIS"
    echo "================"
    
    if [ $NEW_PIECES -gt 0 ]; then
        NEW_COST=$(echo "$ANALYSIS_JSON" | python3 -c "import json, sys; data=json.load(sys.stdin); print(f\"{data['new_pieces'] * 3 * data['cost_per_image']:.2f}\")")
        echo "🆕 New images: $NEW_PIECES content pieces × 3 variations = $((NEW_PIECES * 3)) images"
        echo "   Cost: \$$NEW_COST"
    fi
    
    if [ $UPDATE_PIECES -gt 0 ]; then
        UPDATE_COST=$(echo "$ANALYSIS_JSON" | python3 -c "import json, sys; data=json.load(sys.stdin); print(f\"{data['update_pieces'] * 3 * data['cost_per_image']:.2f}\")")
        echo "🔄 Updated images: $UPDATE_PIECES content pieces × 3 variations = $((UPDATE_PIECES * 3)) images"
        echo "   Cost: \$$UPDATE_COST"
    fi
    
    echo "📊 TOTAL: $TOTAL_IMAGES images ($TOTAL_PIECES pieces × 3 variations) for \$$TOTAL_COST"
    
    echo ""
    echo "🤔 APPROVAL REQUIRED"
    echo "==================="
    echo "Generate $TOTAL_IMAGES images ($TOTAL_PIECES content pieces × 3 variations each) for approximately \$$TOTAL_COST?"
    
    if [ $NEW_PIECES -gt 0 ] && [ $UPDATE_PIECES -gt 0 ]; then
        echo "   • $((NEW_PIECES * 3)) new images for missing content"
        echo "   • $((UPDATE_PIECES * 3)) updated images for style changes"
    elif [ $NEW_PIECES -gt 0 ]; then
        echo "   • $((NEW_PIECES * 3)) new images for missing content"
    else
        echo "   • $((UPDATE_PIECES * 3)) updated images for style changes"
    fi
    echo ""
    read -p "Proceed with generation? (yes/no): " approval
    
    if [ "$approval" != "yes" ] && [ "$approval" != "y" ]; then
        echo "❌ Generation cancelled by user"
        exit 1
    fi
    echo "✅ Generation approved!"
else
    echo "✅ All content already has current images"
fi

echo ""
echo "🎨 GENERATING IMAGES"
echo "==================="

if [ "$NEEDS_GENERATION" = "true" ]; then
    echo "🚀 Starting image generation for $TOTAL_IMAGES images..."
    echo "⏱️  Expected time: ~$((TOTAL_IMAGES * 8)) seconds"
    echo ""
    
    # Set API key and generate
    if [ -z "$GEMINI_API_KEY" ]; then
        # Use the API key from the project documentation
        export GEMINI_API_KEY="AIzaSyCh41VaooU6xexjq7zndc7FSNOh2Sg4-EE"
        echo "🔑 Using project API key for generation"
    fi
    
    # Generate with progress output
    if [ $UPDATE_PIECES -gt 0 ]; then
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
echo "✅ Content parsed: $CONTENT_PIECES files"

if [ "$NEEDS_GENERATION" = "true" ]; then
    NEW_IMAGE_COUNT=$(find generated/images -name "*.png" | wc -l | tr -d ' ')
    echo "✅ Images ready: $NEW_IMAGE_COUNT total ($TOTAL_IMAGES newly generated)"
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

if [ "$NEEDS_GENERATION" = "true" ]; then
    echo "📁 Generated images are now tracked in git (no longer gitignored)"
    echo "🏛️  Old images have been archived to generated/archive/ if any were replaced"
fi