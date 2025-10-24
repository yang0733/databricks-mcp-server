#!/bin/bash
# Deploy both MCP Server and Chat Agent to Databricks Apps

set -e

echo "================================================================================"
echo "🚀 DEPLOYING DATABRICKS MCP SERVER + CHAT AGENT"
echo "================================================================================"
echo

# Check prerequisites
echo "📋 Checking prerequisites..."
echo

if ! command -v databricks &> /dev/null; then
    echo "❌ Databricks CLI not found"
    echo
    echo "Install with:"
    echo "  pip install databricks-cli"
    exit 1
fi

echo "✓ Databricks CLI installed"
echo

# Check if authenticated
if ! databricks workspace ls / &> /dev/null; then
    echo "❌ Not authenticated with Databricks"
    echo
    echo "Run: databricks configure --token"
    echo "  Host: https://e2-demo-west.cloud.databricks.com"
    echo "  Token: <your-personal-access-token>"
    exit 1
fi

echo "✓ Authenticated with Databricks"
echo

# Get Databricks token
echo "📝 Getting Databricks credentials..."
DATABRICKS_TOKEN="${DATABRICKS_TOKEN:-$DATABRICKS_ACCESS_TOKEN}"

if [ -z "$DATABRICKS_TOKEN" ]; then
    echo "⚠️  DATABRICKS_TOKEN not set in environment"
    read -s -p "Enter your Databricks Personal Access Token: " DATABRICKS_TOKEN
    echo
fi

echo "✓ Credentials configured"
echo

# Create secret for token (if not exists)
echo "🔐 Setting up secrets..."
databricks secrets create-scope --scope databricks-mcp --initial-manage-principal users || echo "Scope already exists"
databricks secrets put --scope databricks-mcp --key token --string-value "$DATABRICKS_TOKEN" || echo "Secret already set"
echo "✓ Secrets configured"
echo

# Deploy MCP Server
echo "================================================================================"
echo "📦 DEPLOYING MCP SERVER"
echo "================================================================================"
echo

databricks apps create \
  --name databricks-mcp-server \
  --description "MCP Server for Databricks CLI - 48 tools" \
  --config app_mcp_server.yaml \
  --source-code-path . \
  || databricks apps update \
     --name databricks-mcp-server \
     --config app_mcp_server.yaml \
     --source-code-path .

echo
echo "✓ MCP Server deployed"
echo

# Wait for MCP server to be ready
echo "⏳ Waiting for MCP server to start..."
sleep 10
echo "✓ MCP Server should be ready"
echo

# Deploy Chat Agent
echo "================================================================================"
echo "📦 DEPLOYING CHAT AGENT"
echo "================================================================================"
echo

databricks apps create \
  --name databricks-chat-agent \
  --description "Chat agent with Claude Sonnet 4.5" \
  --config app_chat_agent.yaml \
  --source-code-path . \
  || databricks apps update \
     --name databricks-chat-agent \
     --config app_chat_agent.yaml \
     --source-code-path .

echo
echo "✓ Chat Agent deployed"
echo

# Get app URLs
echo "================================================================================"
echo "✅ DEPLOYMENT COMPLETE"
echo "================================================================================"
echo
echo "Your apps are now deployed! Access them at:"
echo
echo "🔧 MCP Server:"
echo "   https://e2-demo-west.cloud.databricks.com/apps/databricks-mcp-server"
echo
echo "💬 Chat Agent:"
echo "   https://e2-demo-west.cloud.databricks.com/apps/databricks-chat-agent"
echo
echo "================================================================================"
echo
echo "📚 Next steps:"
echo "  1. Open the Chat Agent URL to start chatting"
echo "  2. Use the MCP Server URL for programmatic access"
echo "  3. Monitor logs: databricks apps logs databricks-chat-agent"
echo
echo "================================================================================"

