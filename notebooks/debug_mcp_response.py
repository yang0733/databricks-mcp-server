# Databricks notebook source
# MAGIC %md
# MAGIC # Debug MCP Server Response
# MAGIC
# MAGIC Let's see what the server is actually returning.

# COMMAND ----------

# MAGIC %pip install httpx --quiet
# MAGIC dbutils.library.restartPython()

# COMMAND ----------

import httpx

# Get credentials
databricks_token = dbutils.notebook.entry_point.getDbutils().notebook().getContext().apiToken().get()
workspace_url = dbutils.notebook.entry_point.getDbutils().notebook().getContext().apiUrl().get()

MCP_SERVER_URL = "https://databricks-mcp-server-2556758628403379.aws.databricksapps.com/mcp"

print("=" * 80)
print("Debugging MCP Server Response")
print("=" * 80)
print(f"Server URL: {MCP_SERVER_URL}")
print(f"Token: ...{databricks_token[-10:]}")
print()

# COMMAND ----------

# Test with different auth approaches
print("TEST 1: Bearer Token in Authorization Header")
print("-" * 80)

client = httpx.Client(
    headers={
        "Authorization": f"Bearer {databricks_token}",
        "Content-Type": "application/json"
    },
    follow_redirects=False,  # Don't follow to see redirect
    timeout=30.0
)

response = client.post(
    MCP_SERVER_URL,
    json={
        "jsonrpc": "2.0",
        "method": "initialize",
        "params": {},
        "id": 1
    }
)

print(f"Status Code: {response.status_code}")
print(f"Content-Type: {response.headers.get('content-type')}")
print(f"Location: {response.headers.get('location', 'None')}")
print()
print(f"Response Body (first 500 chars):")
print(response.text[:500])
print()

# COMMAND ----------

# Test 2: Try as Databricks internal request
print("TEST 2: Using Databricks API Token")
print("-" * 80)

# Try accessing as an internal Databricks request
client2 = httpx.Client(
    headers={
        "X-Databricks-Token": databricks_token,
        "Content-Type": "application/json"
    },
    follow_redirects=False,
    timeout=30.0
)

response2 = client2.post(
    MCP_SERVER_URL,
    json={
        "jsonrpc": "2.0",
        "method": "initialize",
        "params": {},
        "id": 1
    }
)

print(f"Status Code: {response2.status_code}")
print(f"Content-Type: {response2.headers.get('content-type')}")
print(f"Response Body (first 500 chars):")
print(response2.text[:500])
print()

# COMMAND ----------

print("=" * 80)
print("DIAGNOSIS")
print("=" * 80)
print()
print("If you see HTML with OAuth redirects:")
print("  → Databricks Apps requires interactive OAuth authentication")
print("  → Cannot be accessed programmatically from notebooks")
print("  → This is why the official template uses a proxy client")
print()
print("Solution:")
print("  → Use the MCP proxy (like official Databricks template)")
print("  → Or access server from outside Databricks with proper OAuth flow")

# COMMAND ----------

