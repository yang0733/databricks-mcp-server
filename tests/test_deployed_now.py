#!/usr/bin/env python3
"""Test the deployed MCP server with proper OAuth authentication."""

import asyncio
from databricks.sdk import WorkspaceClient
from databricks_mcp import DatabricksOAuthClientProvider
from mcp.client.session import ClientSession
from mcp.client.streamable_http import streamablehttp_client

# Configuration
MCP_SERVER_URL = "https://databricks-mcp-server-2556758628403379.aws.databricksapps.com/mcp"

async def test_deployed_mcp():
    """Test the deployed MCP server."""
    
    print("=" * 80)
    print("Testing Deployed MCP Server")
    print("=" * 80)
    print(f"URL: {MCP_SERVER_URL}")
    print()
    
    try:
        # Create workspace client (uses Databricks CLI auth)
        workspace_client = WorkspaceClient()
        
        print("✅ Authenticated to Databricks workspace")
        print()
        
        # Connect to MCP server with OAuth
        async with streamablehttp_client(
            MCP_SERVER_URL,
            auth=DatabricksOAuthClientProvider(workspace_client)
        ) as (read_stream, write_stream, _):
            async with ClientSession(read_stream, write_stream) as session:
                print("✅ Connected to MCP server")
                print()
                
                # Initialize
                await session.initialize()
                print("✅ Session initialized")
                print()
                
                # List tools
                tools_response = await session.list_tools()
                tools = tools_response.tools
                
                print(f"✅ Found {len(tools)} tools")
                print()
                print("Sample tools:")
                for tool in tools[:10]:
                    print(f"  • {tool.name}: {tool.description[:60]}...")
                print()
                
                # Test a simple tool
                print("Testing 'list_clusters' tool...")
                result = await session.call_tool("list_clusters", {})
                print(f"✅ Tool executed successfully")
                print(f"   Result preview: {str(result)[:200]}...")
                print()
                
        print("=" * 80)
        print("✅ ALL TESTS PASSED!")
        print("=" * 80)
        print()
        print("Your MCP server is working correctly!")
        print(f"MCP Endpoint: {MCP_SERVER_URL}")
        print()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        print()
        print("Troubleshooting:")
        print("  1. Ensure you're authenticated: databricks auth login")
        print("  2. Check app status in Databricks UI → Compute → Apps")
        print("  3. Verify the app URL is correct")


if __name__ == "__main__":
    asyncio.run(test_deployed_mcp())

