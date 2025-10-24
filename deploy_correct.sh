#!/bin/bash
set -e

echo "════════════════════════════════════════════════════════════"
echo "  Databricks MCP Server Deployment (Official Method)"
echo "════════════════════════════════════════════════════════════"
echo ""
echo "✅ Using FastMCP (HTTP-compatible transport as required)"
echo "📖 Following: https://docs.databricks.com/aws/en/generative-ai/mcp/custom-mcp"
echo ""

# Configuration
APP_NAME="databricks-mcp-server"
WORKSPACE_HOST="${DATABRICKS_HOST:-https://your-workspace.cloud.databricks.com}"

echo "Configuration:"
echo "  App Name: $APP_NAME"
echo "  Workspace: $WORKSPACE_HOST"
echo ""

# Step 1: Authenticate (if not already authenticated)
echo "Step 1: Verifying authentication..."
if ! databricks current-user me &>/dev/null; then
    echo "⚠️  Not authenticated. Running databricks auth login..."
    databricks auth login --host "$WORKSPACE_HOST"
else
    echo "✅ Already authenticated"
fi

# Get current username
DATABRICKS_USERNAME=$(databricks current-user me | jq -r .userName)
echo "  User: $DATABRICKS_USERNAME"
echo ""

# Step 2: Create app (if it doesn't exist)
echo "Step 2: Creating Databricks App..."
if databricks apps get $APP_NAME &>/dev/null; then
    echo "✅ App '$APP_NAME' already exists"
else
    echo "  Creating new app..."
    databricks apps create $APP_NAME
    echo "✅ App created"
fi
echo ""

# Step 3: Prepare deployment package
echo "Step 3: Preparing deployment package..."
echo "  Files to deploy:"
echo "    • server.py (FastMCP server)"
echo "    • app.yaml (configuration)"
echo "    • requirements.txt (dependencies)"
echo "    • auth.py, databricks_client.py, task_manager.py, tool_registry.py"
echo "    • tools/ (48 Databricks tools)"
echo "    • transports/ (WebSocket support)"
echo ""

# Step 4: Upload source code using databricks sync
echo "Step 4: Uploading source code to workspace..."
WORKSPACE_PATH="/Users/$DATABRICKS_USERNAME/$APP_NAME"
echo "  Target: $WORKSPACE_PATH"

# Create deployment directory with only necessary files
echo "  • Creating clean deployment package..."
rm -rf deploy_clean
mkdir -p deploy_clean

# Copy necessary files
cp server.py deploy_clean/
cp app.yaml deploy_clean/
cp requirements.txt deploy_clean/
cp auth.py deploy_clean/
cp databricks_client.py deploy_clean/
cp task_manager.py deploy_clean/
cp tool_registry.py deploy_clean/

# Copy directories
cp -r tools deploy_clean/
cp -r transports deploy_clean/

cd deploy_clean

echo "  • Syncing to workspace..."
databricks sync . "$WORKSPACE_PATH" --full

cd ..

echo "✅ Source code uploaded"
echo ""

# Step 5: Deploy the app
echo "Step 5: Deploying app..."
databricks apps deploy $APP_NAME \
    --source-code-path "/Workspace$WORKSPACE_PATH"

echo ""
echo "⏳ Waiting for deployment to complete (this may take 2-3 minutes)..."
sleep 15

echo ""
echo "════════════════════════════════════════════════════════════"
echo "  ✅ Deployment Complete!"
echo "════════════════════════════════════════════════════════════"
echo ""
echo "Next steps:"
echo ""
echo "1. Check app status:"
echo "   databricks apps get $APP_NAME"
echo ""
echo "2. View logs:"
echo "   databricks apps logs $APP_NAME"
echo ""
echo "3. Get app URL:"
echo "   databricks apps get $APP_NAME | jq -r .url"
echo ""
echo "4. Test the MCP endpoint:"
echo "   <APP_URL>/mcp"
echo ""
echo "5. Use in notebook:"
echo "   • Upload notebooks/simple_test.py to Databricks"
echo "   • Update MCP_SERVER_URL with your app URL"
echo "   • Run the notebook"
echo ""
echo "════════════════════════════════════════════════════════════"

