#!/bin/bash
# Complete Git deployment for Databricks MCP Server

set -e

echo "================================================================================"
echo "🚀 DEPLOYING DATABRICKS MCP SERVER VIA GITHUB"
echo "================================================================================"
echo

# Step 1: Create GitHub repo (manual)
echo "📝 Step 1: Create GitHub Repository"
echo "-------------------------------------------------------------------------------"
echo
echo "Go to: https://github.com/new"
echo
echo "Settings:"
echo "  • Owner: yang0733"
echo "  • Repository name: databricks-mcp-server"
echo "  • Description: MCP Server for Databricks CLI with 48 tools + Chat Agent"
echo "  • Public (or Private - your choice)"
echo "  • DO NOT initialize with README"
echo
echo "Press ENTER after you've created the repository..."
read

# Step 2: Push to GitHub
echo
echo "📤 Step 2: Pushing code to GitHub"
echo "-------------------------------------------------------------------------------"
echo

# Configure git if needed
git config user.name "Cliff Yang" 2>/dev/null || true
git config user.email "cliff.yang@databricks.com" 2>/dev/null || true

# Add all files
echo "Adding files..."
git add -A

# Commit
echo "Committing changes..."
git commit -m "Deploy: Complete Databricks MCP Server with Claude Sonnet 4.5" || echo "Already committed"

# Push to GitHub
echo "Pushing to GitHub..."
echo "You may need to enter your GitHub credentials..."
git push -u origin main

echo
echo "✓ Code pushed to GitHub!"
echo

# Step 3: Link repo to Databricks
echo "📎 Step 3: Linking GitHub repo to Databricks"
echo "-------------------------------------------------------------------------------"
echo

REPO_PATH="/Repos/cliff.yang@databricks.com/databricks-mcp-server"

# Create repo link
databricks repos create \
  --url https://github.com/yang0733/databricks-mcp-server \
  --provider github \
  --path "$REPO_PATH" \
  || echo "Repo may already exist"

echo "✓ Repo linked to Databricks!"
echo

# Step 4: Deploy to Databricks App
echo "🚀 Step 4: Deploying to Databricks App"
echo "-------------------------------------------------------------------------------"
echo

# Deploy MCP Server
echo "Deploying MCP Server..."
databricks apps deploy databricks-mcp-server \
  --source-code-path "$REPO_PATH" \
  --mode AUTO_SYNC

echo
echo "✓ MCP Server deployed!"
echo

# Check status
echo "Checking deployment status..."
sleep 5
databricks apps get databricks-mcp-server

echo
echo "================================================================================"
echo "✅ DEPLOYMENT COMPLETE!"
echo "================================================================================"
echo
echo "🎉 Your Databricks MCP Server is now live!"
echo
echo "📍 Access your app:"
echo "   https://databricks-mcp-server-2556758628403379.aws.databricksapps.com"
echo
echo "📍 GitHub repo:"
echo "   https://github.com/yang0733/databricks-mcp-server"
echo
echo "📍 Databricks workspace repo:"
echo "   $REPO_PATH"
echo
echo "================================================================================"
echo
echo "🧪 Test it:"
echo "  1. Open the app URL above"
echo "  2. Try the MCP server endpoint: /mcp/"
echo "  3. Use the chat agent for natural language queries"
echo
echo "📊 Monitor:"
echo "  • Logs: databricks apps get databricks-mcp-server"
echo "  • Update: git push (auto-syncs to Databricks)"
echo
echo "================================================================================"

