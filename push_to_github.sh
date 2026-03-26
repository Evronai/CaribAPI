#!/bin/bash

# CaribAPI GitHub Push Script
# Usage: ./push_to_github.sh GITHUB_REPO_URL
# Example: ./push_to_github.sh https://github.com/yourusername/CaribAPI.git

set -e

echo "🚀 Pushing CaribAPI to GitHub..."
echo "================================="

if [ $# -eq 0 ]; then
    echo "❌ Please provide GitHub repository URL"
    echo ""
    echo "Usage: $0 GITHUB_REPO_URL"
    echo "Example: $0 https://github.com/yourusername/CaribAPI.git"
    echo ""
    echo "First, create a repository on GitHub:"
    echo "1. Go to https://github.com/new"
    echo "2. Repository name: CaribAPI"
    echo "3. Description: Caribbean Business Data Platform"
    echo "4. Choose Public or Private"
    echo "5. Click 'Create repository'"
    echo "6. Copy the repository URL"
    exit 1
fi

REPO_URL="$1"

echo "📦 Repository URL: $REPO_URL"
echo ""

# Check if remote already exists
if git remote | grep -q origin; then
    echo "⚠️  Remote 'origin' already exists. Updating..."
    git remote set-url origin "$REPO_URL"
else
    echo "➕ Adding remote 'origin'..."
    git remote add origin "$REPO_URL"
fi

echo ""
echo "🔍 Checking current branch..."
CURRENT_BRANCH=$(git branch --show-current)
echo "Current branch: $CURRENT_BRANCH"

echo ""
echo "📤 Pushing to GitHub..."
echo "This will push the '$CURRENT_BRANCH' branch to 'origin/$CURRENT_BRANCH'..."

# Push with verbose output
if git push -u origin "$CURRENT_BRANCH"; then
    echo ""
    echo "✅ Successfully pushed to GitHub!"
    echo ""
    echo "🌐 Your repository is now at: $REPO_URL"
    echo ""
    echo "🚀 Next steps:"
    echo "1. Deploy to Render: https://render.com/deploy?repo=$REPO_URL"
    echo "2. Deploy to Railway: https://railway.app/new?template=$REPO_URL"
    echo "3. Or see DEPLOY_NOW.md for detailed instructions"
else
    echo ""
    echo "❌ Failed to push to GitHub."
    echo ""
    echo "💡 Troubleshooting:"
    echo "1. Check your internet connection"
    echo "2. Verify GitHub repository URL is correct"
    echo "3. Ensure you have push permissions"
    echo "4. Try: git push -u origin $CURRENT_BRANCH --force"
    exit 1
fi