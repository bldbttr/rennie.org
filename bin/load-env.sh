#!/bin/bash

# Load environment variables from .env file
# Source this script before running commands that need API keys
# Usage: source bin/load-env.sh

ENV_FILE="$(dirname "$0")/../.env"

if [ -f "$ENV_FILE" ]; then
    export $(grep -v '^#' "$ENV_FILE" | xargs)
    echo "✅ Environment variables loaded from .env"
else
    echo "⚠️  Warning: .env file not found"
    echo "📝 Create one from .env.example:"
    echo "   cp .env.example .env"
    echo "   # Then edit .env with your API key"
fi
