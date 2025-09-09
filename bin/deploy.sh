#!/bin/bash

# Deploy site to DreamHost
# Usage: ./bin/deploy.sh

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}🚀 Starting deployment to DreamHost...${NC}"

# Change to project root
cd "$(dirname "$0")/.."

# Check if output directory exists
if [ ! -d "output" ]; then
    echo -e "${RED}❌ Error: output/ directory not found${NC}"
    echo "Run ./bin/build-site.sh first to generate the site"
    exit 1
fi

# Check if SSH key exists
SSH_KEY="$HOME/.ssh/dreamhost_deploy"
if [ ! -f "$SSH_KEY" ]; then
    echo -e "${RED}❌ Error: SSH key not found at $SSH_KEY${NC}"
    echo "Please ensure your DreamHost SSH key is properly configured"
    exit 1
fi

# Deploy using rsync
echo -e "${YELLOW}📤 Syncing files to DreamHost...${NC}"
rsync -avz --delete \
    -e "ssh -i $SSH_KEY -o StrictHostKeyChecking=no" \
    output/ \
    rennie@iad1-shared-e1-05.dreamhost.com:/home/rennie/rennie.org/

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Deployment successful!${NC}"
    echo -e "${GREEN}🌐 Site is live at: https://rennie.org${NC}"
else
    echo -e "${RED}❌ Deployment failed${NC}"
    exit 1
fi