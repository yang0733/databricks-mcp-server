# Databricks notebook source
# MAGIC %md
# MAGIC # Simple MCP Server Test
# MAGIC
# MAGIC Quick test of the Databricks CLI MCP Server from a notebook.

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1. Install Dependencies

# COMMAND ----------

%pip install httpx --quiet
dbutils.library.restartPython()

# COMMAND ----------

# MAGIC %md
# MAGIC ## 2. Configuration

# COMMAND ----------

import httpx
import json

# UPDATE THIS: Your MCP server URL after deployment
MCP_SERVER_URL = "http://localhost:8000/mcp/"  # Replace with your deployed app URL

# Get Databricks credentials automatically
databricks_token = dbutils.notebook.entry_point.getDbutils().notebook().getContext().apiToken().get()
workspace_url = dbutils.notebook.entry_point.getDbutils().notebook().getContext().apiUrl().get()

print("Configuration:")
print(f"  Workspace: {workspace_url}")
print(f"  Token: {'*' * 30}{databricks_token[-4:]}")
print(f"  MCP Server: {MCP_SERVER_URL}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 3. Test Connection

# COMMAND ----------

# Setup headers for MCP requests
headers = {
    "x-databricks-host": workspace_url,
    "x-databricks-token": databricks_token,
    "x-session-id": "notebook-test-123",
    "Content-Type": "application/json"
}

# Test: List available tools
try:
    response = httpx.post(
        MCP_SERVER_URL,
        headers=headers,
        json={
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/list"
        },
        timeout=30.0
    )
    
    result = response.json()
    tools = result.get('result', {}).get('tools', [])
    
    print(f"✅ Connected to MCP server")
    print(f"✅ Found {len(tools)} tools\n")
    print("Sample tools:")
    for tool in tools[:10]:
        print(f"  • {tool['name']}: {tool.get('description', 'No description')[:60]}...")
        
except Exception as e:
    print(f"❌ Connection failed: {e}")
    print("\nTroubleshooting:")
    print("  1. Make sure MCP server is deployed")
    print("  2. Update MCP_SERVER_URL above")
    print("  3. Check server is running in Apps console")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 4. Test Tools

# COMMAND ----------

# Test: List clusters
def call_tool(tool_name: str, arguments: dict = None) -> dict:
    """Helper function to call MCP tools."""
    response = httpx.post(
        MCP_SERVER_URL,
        headers=headers,
        json={
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments or {}
            }
        },
        timeout=60.0
    )
    return response.json()

# COMMAND ----------

# Example 1: List clusters
print("=" * 80)
print("TEST: List Clusters")
print("=" * 80)

try:
    result = call_tool("list_clusters")
    print(json.dumps(result, indent=2))
except Exception as e:
    print(f"Error: {e}")

# COMMAND ----------

# Example 2: List SQL warehouses
print("=" * 80)
print("TEST: List SQL Warehouses")
print("=" * 80)

try:
    result = call_tool("list_warehouses")
    print(json.dumps(result, indent=2))
except Exception as e:
    print(f"Error: {e}")

# COMMAND ----------

# Example 3: List Unity Catalog catalogs
print("=" * 80)
print("TEST: List Catalogs")
print("=" * 80)

try:
    result = call_tool("list_catalogs")
    print(json.dumps(result, indent=2))
except Exception as e:
    print(f"Error: {e}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 5. Batch Test All Safe Tools

# COMMAND ----------

# Test multiple read-only tools
safe_tools = [
    "list_clusters",
    "list_jobs",
    "list_warehouses",
    "list_notebooks",
    "list_catalogs",
    "list_schemas",
    "list_repos"
]

print("Testing safe (read-only) tools...")
print("=" * 80)

results = {}
for tool_name in safe_tools:
    try:
        result = call_tool(tool_name)
        if "error" in result:
            results[tool_name] = f"❌ {result['error'].get('message', 'Unknown error')}"
        else:
            results[tool_name] = "✅ Success"
    except Exception as e:
        results[tool_name] = f"❌ {str(e)[:50]}"

# Print summary
for tool_name, status in results.items():
    print(f"{tool_name:30s} {status}")

print("=" * 80)
success_count = sum(1 for s in results.values() if s.startswith("✅"))
print(f"\n✅ {success_count}/{len(safe_tools)} tools working correctly")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Next Steps
# MAGIC
# MAGIC 1. ✅ If tests pass, MCP server is working!
# MAGIC 2. Try the full agent notebook: `databricks_agent.py`
# MAGIC 3. Build custom workflows using the tools
# MAGIC 4. Share with your team

# COMMAND ----------

