# Databricks notebook source
# MAGIC %md
# MAGIC # Test Databricks MCP Server
# MAGIC
# MAGIC This notebook tests the deployed MCP server from within Databricks.

# COMMAND ----------

# MAGIC %pip install databricks-mcp httpx --quiet
# MAGIC dbutils.library.restartPython()

# COMMAND ----------

import asyncio
from databricks.sdk import WorkspaceClient
from databricks_mcp import DatabricksOAuthClientProvider
from mcp.client.session import ClientSession
from mcp.client.streamable_http import streamablehttp_client

# Configuration
MCP_SERVER_URL = "https://databricks-mcp-server-2556758628403379.aws.databricksapps.com/mcp"

print("=" * 80)
print("Testing MCP Server from Databricks Notebook")
print("=" * 80)
print(f"Server URL: {MCP_SERVER_URL}")
print()

# COMMAND ----------

# Test connection
workspace_client = WorkspaceClient()

async def test_mcp():
    """Test MCP server connection and tools."""
    try:
        async with streamablehttp_client(
            MCP_SERVER_URL,
            auth=DatabricksOAuthClientProvider(workspace_client)
        ) as (read_stream, write_stream, _):
            async with ClientSession(read_stream, write_stream) as session:
                print("✅ Connected to MCP server")
                
                # Initialize
                await session.initialize()
                print("✅ Session initialized")
                
                # List tools
                tools_response = await session.list_tools()
                tools = tools_response.tools
                
                print(f"\n✅ Found {len(tools)} tools")
                print("\nFirst 10 tools:")
                for i, tool in enumerate(tools[:10], 1):
                    print(f"  {i}. {tool.name}")
                
                # Test list_clusters
                print("\n" + "=" * 80)
                print("Testing 'list_clusters' tool:")
                print("=" * 80)
                
                result = await session.call_tool("list_clusters", {})
                print("✅ Tool executed successfully!")
                print(f"\nResult preview:")
                result_text = str(result.content[0].text if result.content else result)
                print(result_text[:500])
                
                print("\n" + "=" * 80)
                print("✅ ALL TESTS PASSED!")
                print("=" * 80)
                
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

# Run test
await test_mcp()

# COMMAND ----------

# MAGIC %md
# MAGIC ## Success!
# MAGIC
# MAGIC If the above tests passed, your MCP server is working correctly and can be used by:
# MAGIC - Other Databricks notebooks
# MAGIC - Databricks agents
# MAGIC - Any code running within the Databricks workspace
# MAGIC
# MAGIC ### Next Steps
# MAGIC 1. Build agents that use these tools
# MAGIC 2. Create workflows with Claude Sonnet 4.5
# MAGIC 3. Share with your team

# COMMAND ----------

