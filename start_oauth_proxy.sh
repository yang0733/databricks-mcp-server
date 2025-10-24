#!/bin/bash

# Start OAuth M2M Proxy for Databricks MCP Server
# Uses Service Principal with automatic token refresh

set -e

echo "🔐 Starting OAuth M2M Proxy..."
echo ""

# Check credentials
if [ -z "$DATABRICKS_APP_URL" ] || [ -z "$DATABRICKS_CLIENT_ID" ] || [ -z "$DATABRICKS_CLIENT_SECRET" ]; then
    echo "❌ Missing OAuth configuration!"
    echo ""
    echo "Please set:"
    echo "  export DATABRICKS_APP_URL='https://your-app.databricksapps.com'"
    echo "  export DATABRICKS_HOST='https://your-workspace.cloud.databricks.com'"
    echo "  export DATABRICKS_CLIENT_ID='<service-principal-id>'"
    echo "  export DATABRICKS_CLIENT_SECRET='<oauth-secret>'"
    echo ""
    exit 1
fi

echo "✅ Configuration:"
echo "   App URL: $DATABRICKS_APP_URL"
echo "   Workspace: $DATABRICKS_HOST"
echo "   Client ID: ${DATABRICKS_CLIENT_ID:0:8}..."
echo ""

# Start proxy
echo "🚀 Starting OAuth proxy on http://localhost:8080/mcp"
echo ""

python3 oauth/cursor_oauth_proxy.py
