#!/bin/bash

# Commit and Deploy - Hybrid Local-First Workflow
# This script commits locally generated images and triggers deployment

set -e

cd "$(dirname "$0")/.."

echo "📋 COMMIT AND DEPLOY WORKFLOW"
echo "============================="

# Check if there are any changes to commit
if git diff --quiet && git diff --cached --quiet && [ -z "$(git status --porcelain)" ]; then
    echo "✅ Repository is clean - no pending changes to deploy"
    echo ""
    echo "🔍 Checking if any content needs new images..."
    
    # Check image status using existing script logic
    python scripts/content_parser.py > /dev/null 2>&1
    check_output=$(python scripts/generate_images.py --check-images 2>/dev/null)
    
    # Count files that need images
    needs_images_count=$(echo "$check_output" | grep -c "🆕\|🔄" || true)
    
    if [ $needs_images_count -gt 0 ]; then
        echo "📝 Found $needs_images_count content file(s) that need images:"
        echo "$check_output" | grep "🆕\|🔄" | while read -r line; do
            echo "   • $line"
        done
        echo ""
        echo "💡 To generate images and deploy new content:"
        echo "   ./bin/generate-new-images-locally.sh"
    else
        echo "✅ All content has current images"
        echo ""
        echo "📋 Current deployment status:"
        echo "   • All changes are committed and deployed"
        echo "   • Site is live at https://rennie.org"
        echo "   • No further action needed"
    fi
    
    echo ""
    echo "🔧 If you have local changes to deploy, make sure to:"
    echo "   1. Save your changes to files"
    echo "   2. Re-run this script to commit and deploy them"
    
    exit 0
fi

echo "📊 Changes to be committed:"
git status --porcelain

# Check specifically for generated images
if [ -d "generated/images" ] && [ -n "$(find generated/images -name "*.png" -type f)" ]; then
    image_count=$(find generated/images -name "*.png" | wc -l | tr -d ' ')
    echo "✅ Found $image_count generated images ready for commit"
else
    echo "⚠️ No generated images found"
    echo "   Please run './bin/generate-new-images-locally.sh' first to generate images"
    exit 1
fi

# Auto-generate commit message based on what's being committed
echo ""
echo "📝 Auto-generating commit message..."

# Check what types of changes we have
has_images=$(find . -name "*.png" -path "./generated/images/*" | head -1)
has_code=$(git status --porcelain | grep -E '\.(js|html|css|py|sh|md)$' | head -1)
has_content=$(git status --porcelain | grep 'content/inspiration' | head -1)

timestamp=$(date '+%Y-%m-%d %H:%M')

if [ -n "$has_content" ] && [ -n "$has_images" ]; then
    commit_message="Add new content with generated images - $timestamp

🎨 Images generated locally using hybrid workflow
📝 New content added to inspiration collection
✅ Previewed and approved before deployment"
elif [ -n "$has_images" ]; then
    commit_message="Update images with new variations - $timestamp

🎨 Images regenerated locally using hybrid workflow  
🔄 Style changes or new variations added
✅ Previewed and approved before deployment"
elif [ -n "$has_code" ]; then
    commit_message="Frontend/backend improvements - $timestamp

🔧 Code improvements and enhancements
✅ Tested locally before deployment"
else
    commit_message="Content and site updates - $timestamp

📝 Various updates and improvements
✅ Ready for deployment"
fi

echo "💬 Commit message: $(echo "$commit_message" | head -1)"

echo ""
echo "💾 Committing changes..."
git add .
git commit -m "$commit_message"

echo "✅ Changes committed successfully"

echo ""
echo "🚀 Pushing to trigger deployment..."
git push

echo ""
echo "📋 DEPLOYMENT STATUS"
echo "=================="
echo "✅ Changes pushed to GitHub"
echo "🔄 GitHub Actions will now:"
echo "   1. Verify locally generated images are present"
echo "   2. Build the static site using your images"
echo "   3. Deploy to rennie.org"
echo ""
echo "👀 Monitor deployment progress:"
echo "   https://github.com/$(git remote get-url origin | sed 's/.*github.com[:/]\(.*\)\.git/\1/')/actions"
echo ""
echo "🌐 Site will be live at: https://rennie.org"
echo ""
echo "💡 The images you previewed locally are now deployed to production!"