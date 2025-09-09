#!/bin/bash

# Check image status for each content file
# Shows two simple lists: files that need no images, and files that need images

set -e

cd "$(dirname "$0")/.."

# First parse content to ensure we have latest data
python scripts/content_parser.py > /dev/null 2>&1

# Get the detailed check results and parse them
check_output=$(python scripts/generate_images.py --check-images)

# Parse the output to separate files that need images vs those that don't
needs_images=()
no_images_needed=()

while IFS= read -r line; do
    if [[ $line =~ ^([a-zA-Z0-9_-]+)[[:space:]]*│[[:space:]]*(🆕|🔄) ]]; then
        filename="${BASH_REMATCH[1]}"
        needs_images+=("$filename")
    elif [[ $line =~ ^([a-zA-Z0-9_-]+)[[:space:]]*│[[:space:]]*✅ ]]; then
        filename="${BASH_REMATCH[1]}"
        no_images_needed+=("$filename")
    fi
done <<< "$check_output"

echo "FILES THAT NEED NO IMAGES:"
if [ ${#no_images_needed[@]} -eq 0 ]; then
    echo "  (none)"
else
    for file in "${no_images_needed[@]}"; do
        echo "  $file"
    done
fi

echo ""
echo "FILES THAT NEED IMAGES:"
if [ ${#needs_images[@]} -eq 0 ]; then
    echo "  (none)"
else
    for file in "${needs_images[@]}"; do
        echo "  $file: 3 images"
    done
fi

echo ""
echo "ORPHANED IMAGES CHECK:"
echo "====================="

# Check for orphaned images using the new Python functionality
orphaned_output=$(python scripts/generate_images.py --check-orphaned 2>/dev/null)
orphaned_exit_code=$?

if [ $orphaned_exit_code -eq 0 ]; then
    if echo "$orphaned_output" | grep -q "No orphaned images found"; then
        echo "✅ No orphaned images found"
    else
        echo "🗑️  Found orphaned images that can be cleaned up:"
        echo ""
        # Extract and display just the file listings from the orphaned output
        echo "$orphaned_output" | sed -n '/📂 Images for deleted content:/,/^$/p' | grep "  •" | sed 's/^  •/  /'
        echo "$orphaned_output" | sed -n '/🔢 Excess variation images:/,/^$/p' | grep "  •" | sed 's/^  •/  /'
        echo ""
        # Extract the summary line
        echo "$orphaned_output" | grep "💾 Estimated space to reclaim:" | sed 's/^💾 //'
        echo ""
        echo "💡 Run './bin/cleanup-images.sh' to remove orphaned images"
    fi
else
    echo "⚠️  Could not check for orphaned images (run 'python scripts/content_parser.py' first)"
fi