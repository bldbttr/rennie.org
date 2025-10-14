#!/bin/bash

# Local Preview Server for rennie.org
# Serves the output directory with a simple HTTP server to avoid CORS issues

set -e

cd "$(dirname "$0")/.."

# Check if output directory exists
if [ ! -d "output" ]; then
    echo "❌ No output directory found"
    echo "   Run './bin/generate-new-images-locally.sh' first"
    exit 1
fi

# Check if index.html exists
if [ ! -f "output/index.html" ]; then
    echo "❌ No index.html found in output directory"
    echo "   Run 'python scripts/build_site.py' first"
    exit 1
fi

echo "🌐 Starting local preview server..."
echo "📁 Serving from: $(pwd)/output/"

# Try PHP built-in server first (supports PHP and POST requests)
if command -v php &> /dev/null; then
    echo "🚀 Server starting at: http://localhost:8000 (PHP)"
    echo "   ✓ PHP endpoint available for logging"
    echo "   Press Ctrl+C to stop"
    echo ""
    cd output && php -S localhost:8000
# Fall back to Python 3
elif command -v python3 &> /dev/null; then
    echo "🚀 Server starting at: http://localhost:8000 (Python)"
    echo "   ⚠️  PHP endpoint not available (logs will use localStorage only)"
    echo "   Press Ctrl+C to stop"
    echo ""
    cd output && python3 -m http.server 8000
# Fall back to Python 2
elif command -v python &> /dev/null; then
    echo "🚀 Server starting at: http://localhost:8000 (Python)"
    echo "   ⚠️  PHP endpoint not available (logs will use localStorage only)"
    echo "   Press Ctrl+C to stop"
    echo ""
    cd output && python -m SimpleHTTPServer 8000
else
    echo "❌ Python/PHP not found"
    echo "   Install Python or PHP to use local preview server"
    echo "   Alternative: Use any other local server in the output/ directory"
    exit 1
fi