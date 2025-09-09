#!/bin/bash

# Cleanup Orphaned Images
# Identifies and removes images that are no longer needed:
# - Images for deleted content files
# - Excess variation images when count is reduced

set -e

cd "$(dirname "$0")/.."

echo "🧹 ORPHANED IMAGES CLEANUP"
echo "=========================="

# First parse content to ensure we have latest data
echo "📝 Parsing content files..."
python scripts/content_parser.py > /dev/null 2>&1

# Check for orphaned images first
echo "🔍 Checking for orphaned images..."
echo ""

check_output=$(python scripts/generate_images.py --check-orphaned)
check_exit_code=$?

if [ $check_exit_code -ne 0 ]; then
    echo "❌ Error checking for orphaned images"
    exit 1
fi

echo "$check_output"

# Check if any orphaned images were found
if echo "$check_output" | grep -q "No orphaned images found"; then
    echo ""
    echo "✅ All images are current - no cleanup needed!"
    exit 0
fi

echo ""
echo "🤔 CONFIRMATION REQUIRED"
echo "========================"

# Show what would be removed with dry run
echo "📋 Preview of what will be removed:"
echo ""

dry_run_output=$(python scripts/generate_images.py --cleanup-orphaned --dry-run)
echo "$dry_run_output"

echo ""
echo "⚠️  This will permanently remove the orphaned files (after archiving them for safety)"
echo "📁 Files will be archived to generated/archive/cleanup_TIMESTAMP/ before deletion"
echo ""

read -p "Proceed with cleanup? (yes/no): " confirmation

if [ "$confirmation" != "yes" ] && [ "$confirmation" != "y" ]; then
    echo "❌ Cleanup cancelled by user"
    exit 1
fi

echo ""
echo "🗑️  PERFORMING CLEANUP"
echo "====================="

# Perform actual cleanup
cleanup_output=$(python scripts/generate_images.py --cleanup-orphaned)
cleanup_exit_code=$?

echo "$cleanup_output"

if [ $cleanup_exit_code -ne 0 ]; then
    echo ""
    echo "❌ Cleanup failed"
    exit 1
fi

echo ""
echo "✅ CLEANUP COMPLETED"
echo "==================="
echo "🧹 Orphaned images have been removed and archived"
echo "📁 Check generated/archive/ if you need to restore any files"
echo "💡 Run './bin/check-images.sh' to verify current image status"