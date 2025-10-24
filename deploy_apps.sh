#!/bin/bash
#Deploy MCP Server and Chat Agent to Databricks Apps

set -e

echo "================================================================================"
echo "🚀 DEPLOYING DATABRICKS MCP SERVER + CHAT AGENT"
echo "================================================================================"
echo

# Configuration
APP_NAME_MCP="databricks-mcp-server"
APP_NAME_CHAT="databricks-chat-agent"
WORKSPACE_PATH="/Users/cliff.yang@databricks.com/databricks-mcp-apps"

echo "📋 Configuration:"
echo "  Workspace: https://e2-demo-west.cloud.databricks.com"
echo "  MCP App: $APP_NAME_MCP"
echo "  Chat App: $APP_NAME_CHAT"
echo "  Upload path: $WORKSPACE_PATH"
echo

# Create workspace directory for app files
echo "📁 Creating workspace directory..."
databricks workspace mkdirs "$WORKSPACE_PATH" 2>/dev/null || true
echo "✓ Directory ready"
echo

# Upload source code
echo "📤 Uploading source code..."
databricks workspace import-dir \
  . \
  "$WORKSPACE_PATH/source" \
  --overwrite
echo "✓ Source code uploaded"
echo

# Create/Update MCP Server App
echo "================================================================================"
echo "📦 DEPLOYING MCP SERVER"
echo "================================================================================"
echo

# Check if app exists
if databricks apps get "$APP_NAME_MCP" 2>/dev/null; then
    echo "⚠️  App $APP_NAME_MCP already exists, updating..."
else
    echo "Creating new app: $APP_NAME_MCP..."
    databricks apps create "$APP_NAME_MCP" \
      --description "MCP Server for Databricks CLI - 48 tools for managing Databricks" \
      --compute-size MEDIUM \
      || echo "Note: App may already exist"
    echo "✓ App created"
fi

echo
echo "Deploying source code to $APP_NAME_MCP..."
databricks apps deploy "$APP_NAME_MCP" \
  --source-code-path "$WORKSPACE_PATH/source" \
  --mode SNAPSHOT
echo "✓ MCP Server deployed"
echo

# Start the app
echo "Starting $APP_NAME_MCP..."
databricks apps start "$APP_NAME_MCP" || echo "App may already be running"
echo "✓ MCP Server started"
echo

# Create/Update Chat Agent App
echo "================================================================================"
echo "📦 DEPLOYING CHAT AGENT"
echo "================================================================================"
echo

# Check if app exists
if databricks apps get "$APP_NAME_CHAT" 2>/dev/null; then
    echo "⚠️  App $APP_NAME_CHAT already exists, updating..."
else
    echo "Creating new app: $APP_NAME_CHAT..."
    databricks apps create "$APP_NAME_CHAT" \
      --description "Natural language chat interface using Claude Sonnet 4.5" \
      --compute-size MEDIUM \
      || echo "Note: App may already exist"
    echo "✓ App created"
fi

echo
echo "Deploying source code to $APP_NAME_CHAT..."
databricks apps deploy "$APP_NAME_CHAT" \
  --source-code-path "$WORKSPACE_PATH/source" \
  --mode SNAPSHOT
echo "✓ Chat Agent deployed"
echo

# Start the app
echo "Starting $APP_NAME_CHAT..."
databricks apps start "$APP_NAME_CHAT" || echo "App may already be running"
echo "✓ Chat Agent started"
echo

# Get app URLs
echo "================================================================================"
echo "✅ DEPLOYMENT COMPLETE"
echo "================================================================================"
echo
echo "Your apps are now deployed!"
echo
echo "🔧 MCP Server:"
echo "   https://e2-demo-west.cloud.databricks.com/ml/apps/$APP_NAME_MCP"
echo
echo "💬 Chat Agent:"
echo "   https://e2-demo-west.cloud.databricks.com/ml/apps/$APP_NAME_CHAT"
echo
echo "================================================================================"
echo
echo "📚 Next steps:"
echo "  1. Check status: databricks apps get $APP_NAME_CHAT"
echo "  2. View logs: databricks apps get $APP_NAME_CHAT (look for 'url' field)"
echo "  3. List apps: databricks apps list"
echo
echo "================================================================================"

