#!/bin/bash

# Script to create GitHub repository and push code
# You'll need a GitHub Personal Access Token with repo permissions

REPO_NAME="gemini_v3_event_router_api"
USERNAME="rkgupta131"
GITHUB_TOKEN="${GITHUB_TOKEN:-}"

echo "Creating repository: $REPO_NAME"

if [ -z "$GITHUB_TOKEN" ]; then
    echo "⚠️  GITHUB_TOKEN not set. Creating repository via web interface..."
    echo ""
    echo "Please:"
    echo "1. Go to: https://github.com/new"
    echo "2. Repository name: $REPO_NAME"
    echo "3. Don't initialize with README/.gitignore/license"
    echo "4. Click 'Create repository'"
    echo ""
    echo "Then run: git push -u origin main"
    exit 1
fi

# Create repository via API
echo "Creating repository via GitHub API..."
RESPONSE=$(curl -s -X POST \
  -H "Authorization: token $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github.v3+json" \
  https://api.github.com/user/repos \
  -d "{\"name\":\"$REPO_NAME\",\"description\":\"AI-powered webpage builder API using Gemini models\",\"private\":false}")

if echo "$RESPONSE" | grep -q "already exists"; then
    echo "✅ Repository already exists!"
elif echo "$RESPONSE" | grep -q '"name"'; then
    echo "✅ Repository created successfully!"
else
    echo "❌ Failed to create repository:"
    echo "$RESPONSE"
    exit 1
fi

# Set remote and push
echo "Setting up remote..."
git remote remove origin 2>/dev/null
git remote add origin "https://github.com/$USERNAME/$REPO_NAME.git"

echo "Pushing code..."
git push -u origin main

if [ $? -eq 0 ]; then
    echo "✅ Code pushed successfully!"
    echo "Repository URL: https://github.com/$USERNAME/$REPO_NAME"
else
    echo "❌ Push failed. Please check your credentials."
fi

