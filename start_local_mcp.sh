#!/bin/bash

# Start Databricks MCP Server (Local with PAT)
# Uses Personal Access Token for authentication

set -e

echo "🚀 Starting Databricks MCP Server..."
echo ""

# Check credentials
if [ -z "$DATABRICKS_HOST" ] || [ -z "$DATABRICKS_TOKEN" ]; then
    echo "❌ Missing credentials!"
    echo ""
    echo "Please set:"
    echo "  export DATABRICKS_HOST='https://your-workspace.cloud.databricks.com'"
    echo "  export DATABRICKS_TOKEN='dapi...'"
    echo ""
    exit 1
fi

echo "✅ Configuration:"
echo "   Host: $DATABRICKS_HOST"
echo "   Token: ${DATABRICKS_TOKEN:0:12}..."
echo ""

# Start server
echo "🚀 Starting MCP server on http://localhost:8080/mcp"
echo ""

python3 local_mcp_server.py
