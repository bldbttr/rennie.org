#!/bin/bash
# Secure Git Setup for rennie.org

echo "🔐 Setting up secure Git configuration"

# Step 1: Clear any cached credentials (for security)
git config --global --unset credential.helper 2>/dev/null || true
git config --unset credential.helper 2>/dev/null || true

# Step 2: Set up proper user configuration
git config --global user.name "hoggfather"
git config --global user.email "krennie@users.noreply.github.com"

# Step 3: Use HTTPS with credential manager for security
git config --global credential.helper osxkeychain

echo "✅ Git configured securely"
echo ""
echo "When you push to GitHub, you'll be prompted for:"
echo "  Username: hoggfather"
echo "  Password: [use a Personal Access Token, not your GitHub password]"
echo ""
echo "📝 To create a Personal Access Token:"
echo "1. Go to: https://github.com/settings/tokens"
echo "2. Click 'Generate new token (classic)'"
echo "3. Give it a name: 'rennie.org-development'"
echo "4. Select scopes: 'repo' (full control of private repositories)"
echo "5. Click 'Generate token'"
echo "6. Copy the token and use it as your password when git prompts you"
echo ""

# Step 4: Create the repository structure
cd /Users/krennie/dev/rennie.org
echo "📂 Current directory: $(pwd)"

# Initialize git if not already done
if [ ! -d ".git" ]; then
    git init
    echo "✅ Git repository initialized"
fi

# Create project structure
mkdir -p .github/workflows content generated/images public scripts

# Create .gitignore
cat > .gitignore << 'EOF'
# Environment files
.env
.env.local
*.key

# Generated content (created by GitHub Actions)
generated/
public/images/*.png

# Python
__pycache__/
*.py[cod]
*$py.class
.venv/
venv/
env/

# Dependencies
node_modules/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Test files
test_*.png
*_test.py
nano-banana-test/

# Keep bin/ directory but ignore temporary files in it
bin/*.tmp
bin/*.log
EOF

# Create initial content
cat > content/quotes.json << 'EOF'
{
  "items": [
    {
      "id": "make-something-people-want",
      "text": "Make something people want",
      "author": "Paul Graham",
      "type": "quote",
      "year": "2005",
      "source": "Y Combinator",
      "image_prompt": "A vibrant startup office scene with passionate entrepreneurs building something amazing, people collaborating around laptops and whiteboards, warm lighting, modern aesthetic, inspiring and energetic mood, digital art style",
      "tags": ["startup", "entrepreneurship", "y-combinator"],
      "status": "active"
    }
  ],
  "metadata": {
    "version": "1.0", 
    "last_updated": "2025-09-06",
    "total_items": 1
  }
}
EOF

# Create README
cat > README.md << 'EOF'
# Poetry & Art - rennie.org

Personal homepage displaying inspiring quotes and poems with AI-generated artwork using Google's Nano Banana.

## Features
- 🎨 AI-generated artwork using Nano Banana (Gemini 2.5 Flash Image)
- 📝 Curated quotes and poetry
- 🔄 Random selection on page load
- 📱 Responsive design
- 🚀 Automated GitHub Actions deployment

## Current Content
- "Make something people want" - Paul Graham

## Tech Stack
- Image Generation: Google Gemini 2.5 Flash Image
- Frontend: HTML/CSS/JavaScript
- Deployment: GitHub Actions → DreamHost
EOF

# Add and commit
git add .
git commit -m "Initial commit: Right-sized poetry site structure

- Individual content files in content/inspiration/
- Reusable style library in content/styles/
- Paul Graham quote as initial test content
- Proper project documentation
- Ready for Nano Banana image generation and GitHub Actions"

echo ""
echo "🎯 NEXT STEPS:"
echo "1. Go to https://github.com/new"
echo "2. Repository name: 'rennie.org'"
echo "3. Description: 'Personal poetry site with AI-generated artwork'"
echo "4. Make it PUBLIC (for free GitHub Actions)"
echo "5. DON'T check any initialization boxes"
echo "6. Click 'Create repository'"
echo ""
echo "7. Then run these commands:"
echo "   git remote add origin https://github.com/hoggfather/rennie.org.git"
echo "   git branch -M main"
echo "   git push -u origin main"
echo ""
echo "✅ Repository ready for GitHub!"
