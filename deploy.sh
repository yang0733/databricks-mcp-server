#!/bin/bash
# Deployment script for Databricks CLI MCP Server

set -e

APP_NAME="databricks-cli-mcp-server"
SOURCE_PATH="."

echo "=================================="
echo "Databricks CLI MCP Server"
echo "Deployment Script"
echo "=================================="
echo ""

# Check if databricks CLI is installed
if ! command -v databricks &> /dev/null; then
    echo "❌ Error: Databricks CLI is not installed"
    echo ""
    echo "Install with:"
    echo "  brew install databricks"
    echo ""
    exit 1
fi

echo "✓ Databricks CLI found"
echo ""

# Check authentication
echo "Checking Databricks authentication..."
if ! databricks workspace ls / &> /dev/null; then
    echo "❌ Error: Not authenticated with Databricks"
    echo ""
    echo "Configure authentication with:"
    echo "  databricks configure --token"
    echo ""
    exit 1
fi

echo "✓ Authenticated with Databricks"
echo ""

# Deploy the app
echo "Deploying $APP_NAME..."
echo ""

databricks apps deploy $APP_NAME --source-path $SOURCE_PATH

echo ""
echo "=================================="
echo "Deployment Complete!"
echo "=================================="
echo ""
echo "Next steps:"
echo "  1. Check logs: databricks apps logs $APP_NAME --follow"
echo "  2. Get status: databricks apps get $APP_NAME"
echo "  3. Access URL: Check output above for the app URL"
echo ""
echo "To update the app after code changes:"
echo "  ./deploy.sh"
echo ""

