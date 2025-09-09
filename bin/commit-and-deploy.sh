#!/bin/bash

# Commit and Deploy - Hybrid Local-First Workflow
# This script commits locally generated images and triggers deployment

set -e

cd "$(dirname "$0")/.."

echo "📋 COMMIT AND DEPLOY WORKFLOW"
echo "============================="

# Check if there are any changes to commit
if git diff --quiet && git diff --cached --quiet && [ -z "$(git status --porcelain)" ]; then
    echo "⚠️ No changes to commit"
    echo "   Did you run './bin/preview-and-check.sh' first?"
    exit 1
fi

echo "📊 Changes to be committed:"
git status --porcelain

# Check specifically for generated images
if [ -d "generated/images" ] && [ -n "$(find generated/images -name "*.png" -type f)" ]; then
    image_count=$(find generated/images -name "*.png" | wc -l | tr -d ' ')
    echo "✅ Found $image_count generated images ready for commit"
else
    echo "⚠️ No generated images found"
    echo "   Please run './bin/preview-and-check.sh' first to generate images"
    exit 1
fi

# Get commit message from user
echo ""
echo "📝 Enter commit message (or press Enter for default):"
read -r commit_message

if [ -z "$commit_message" ]; then
    commit_message="Add content with locally generated images

🎨 Images generated locally using preview-and-check.sh
✅ Previewed and approved before deployment
🚀 Ready for automatic deployment to rennie.org"
fi

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