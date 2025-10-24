# Databricks Apps Deployment Guide

Deploy both the MCP Server and Chat Agent to Databricks Apps with Claude Sonnet 4.5.

## 🎯 What Gets Deployed

### 1. MCP Server App
- **48 Databricks tools** exposed via HTTP API
- Runs on port 8000
- Stateful session management
- Accessible at: `https://e2-demo-west.cloud.databricks.com/apps/databricks-mcp-server`

### 2. Chat Agent App  
- **Natural language interface** using Claude Sonnet 4.5
- Connects to MCP Server for tool execution
- Uses Databricks Model Serving endpoint for Claude
- Accessible at: `https://e2-demo-west.cloud.databricks.com/apps/databricks-chat-agent`

## 🚀 Quick Deploy

```bash
cd /Users/cliff.yang/CursorProj/databricks_cli_mcp

# Set your token
export DATABRICKS_TOKEN='dapi14c8fa7e4aaa0907a3144b740fd91f50'

# Deploy both apps
./deploy_to_databricks.sh
```

## 📋 Prerequisites

### 1. Install Databricks CLI
```bash
pip install databricks-cli
```

### 2. Configure Authentication
```bash
databricks configure --token
```
- Host: `https://e2-demo-west.cloud.databricks.com`
- Token: Your Personal Access Token

### 3. Verify Access to Claude Endpoint
Ensure you have access to:
```
https://e2-demo-west.cloud.databricks.com/serving-endpoints/databricks-claude-sonnet-4-5/invocations
```

## 🔧 Manual Deployment Steps

### Step 1: Deploy MCP Server

```bash
databricks apps create \
  --name databricks-mcp-server \
  --description "MCP Server for Databricks CLI" \
  --config app_mcp_server.yaml \
  --source-code-path .
```

### Step 2: Deploy Chat Agent

```bash
databricks apps create \
  --name databricks-chat-agent \
  --description "Chat agent with Claude Sonnet 4.5" \
  --config app_chat_agent.yaml \
  --source-code-path .
```

## 🔐 Secrets Management

The deployment script automatically creates:
- Secret scope: `databricks-mcp`
- Secret key: `token` (your PAT)

Both apps use this secret for authentication.

## 📊 App Configuration

### MCP Server (`app_mcp_server.yaml`)
```yaml
name: databricks-mcp-server
resources:
  - name: mcp-server
    port: 8000
command:
  - python
  - server.py
  - --host=0.0.0.0
  - --port=8000
```

### Chat Agent (`app_chat_agent.yaml`)
```yaml
name: databricks-chat-agent
resources:
  - name: chat-agent
    port: 8080
command:
  - python
  - chat_agent_databricks.py
env:
  - name: CLAUDE_ENDPOINT
    value: https://e2-demo-west.cloud.databricks.com/serving-endpoints/databricks-claude-sonnet-4-5/invocations
  - name: MCP_SERVER_URL
    value: http://databricks-mcp-server:8000/mcp/
```

## 🎯 Using the Deployed Apps

### Chat Agent (Web UI)

1. Open: `https://e2-demo-west.cloud.databricks.com/apps/databricks-chat-agent`
2. Start chatting in natural language:
   - "Show me all my clusters"
   - "List my recent jobs"
   - "What tables are in Unity Catalog?"

### MCP Server (Programmatic)

```python
from fastmcp.client import Client
from fastmcp.client.transports import StreamableHttpTransport

headers = {
    "x-databricks-host": "https://e2-demo-west.cloud.databricks.com",
    "x-databricks-token": "dapi...",
    "x-session-id": "my-session"
}

transport = StreamableHttpTransport(
    "https://e2-demo-west.cloud.databricks.com/apps/databricks-mcp-server/mcp/",
    headers=headers
)

async with Client(transport=transport) as client:
    result = await client.call_tool("list_clusters", {})
    print(result)
```

## 📈 Monitoring

### View Logs
```bash
# MCP Server logs
databricks apps logs databricks-mcp-server

# Chat Agent logs
databricks apps logs databricks-chat-agent
```

### Check Status
```bash
databricks apps list
databricks apps get databricks-mcp-server
databricks apps get databricks-chat-agent
```

### Restart Apps
```bash
databricks apps restart databricks-mcp-server
databricks apps restart databricks-chat-agent
```

## 🔄 Updates

To update the apps after code changes:

```bash
# Update MCP Server
databricks apps update \
  --name databricks-mcp-server \
  --config app_mcp_server.yaml \
  --source-code-path .

# Update Chat Agent
databricks apps update \
  --name databricks-chat-agent \
  --config app_chat_agent.yaml \
  --source-code-path .
```

Or use the deploy script:
```bash
./deploy_to_databricks.sh  # Automatically updates existing apps
```

## 🛠️ Troubleshooting

### App Won't Start
```bash
# Check logs for errors
databricks apps logs databricks-mcp-server --follow

# Verify configuration
databricks apps get databricks-mcp-server
```

### Claude Endpoint Issues
```bash
# Test endpoint access
curl -X POST \
  https://e2-demo-west.cloud.databricks.com/serving-endpoints/databricks-claude-sonnet-4-5/invocations \
  -H "Authorization: Bearer $DATABRICKS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"messages":[{"role":"user","content":"test"}],"max_tokens":10}'
```

### Connection Issues
- Ensure MCP Server is running before starting Chat Agent
- Check that `MCP_SERVER_URL` points to the correct internal URL
- Verify secrets are properly configured

## 💰 Cost Considerations

### MCP Server
- Minimal compute cost (always-on lightweight server)
- No per-request API costs

### Chat Agent
- Claude API calls via Databricks Model Serving
- Costs depend on usage volume
- Consider implementing rate limiting for production

## 🔒 Security

1. **Authentication**: Apps use Databricks PAT via secrets
2. **Network**: Internal communication between apps
3. **RBAC**: Inherits user's Databricks permissions
4. **Audit**: All operations logged in Databricks audit logs

## 🎓 Best Practices

1. **Monitoring**: Set up alerts for app health
2. **Updates**: Use CI/CD for automated deployments
3. **Scaling**: Configure auto-scaling for high traffic
4. **Testing**: Test in dev workspace before production
5. **Secrets**: Rotate PATs regularly

## 📚 Additional Resources

- **Databricks Apps Docs**: https://docs.databricks.com/apps/
- **Model Serving**: https://docs.databricks.com/machine-learning/model-serving/
- **FastMCP**: https://gofastmcp.com

## ✅ Success Checklist

- [ ] Databricks CLI installed and configured
- [ ] Access to Claude Sonnet 4.5 endpoint verified
- [ ] Secrets created successfully
- [ ] MCP Server deployed and accessible
- [ ] Chat Agent deployed and accessible
- [ ] Can chat via web UI
- [ ] Can make programmatic API calls

---

🎉 **You're ready!** Your Databricks MCP Server and Chat Agent are now running as Databricks Apps with Claude Sonnet 4.5!

