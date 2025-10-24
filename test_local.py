#!/usr/bin/env python3
"""Local testing script for Databricks CLI MCP Server."""

import asyncio
import sys
from fastmcp.client import Client
from fastmcp.client.transports import StreamableHttpTransport


# Configuration - UPDATE THESE WITH YOUR DATABRICKS CREDENTIALS
DATABRICKS_HOST = "https://e2-demo-west.cloud.databricks.com"
DATABRICKS_TOKEN = "dapi14c8fa7e4aaa0907a3144b740fd91f50"
SERVER_URL = "http://localhost:8000/mcp/"


async def test_mcp_server():
    """Test the Databricks CLI MCP server."""
    
    print("=" * 80)
    print("Databricks CLI MCP Server - Local Testing")
    print("=" * 80)
    print()
    
    # Set up authentication headers
    headers = {
        "x-databricks-host": DATABRICKS_HOST,
        "x-databricks-token": DATABRICKS_TOKEN,
        "x-session-id": "test-session-123"
    }
    
    transport = StreamableHttpTransport(SERVER_URL, headers=headers)
    
    try:
        async with Client(transport=transport) as client:
            print(f"✓ Connected to {SERVER_URL}")
            print()
            
            # Test 1: List available tools
            print("TEST 1: List Available Tools")
            print("-" * 40)
            tools = await client.list_tools()
            print(f"✓ Found {len(tools)} tools:")
            for i, tool in enumerate(tools[:10], 1):
                print(f"  {i}. {tool.name}")
            if len(tools) > 10:
                print(f"  ... and {len(tools) - 10} more")
            print()
            
            # Test 2: Get session context
            print("TEST 2: Get Session Context")
            print("-" * 40)
            result = await client.call_tool("get_session_context", {})
            if result:
                # Handle both list and direct result
                if isinstance(result, list):
                    context_data = result[0].content[0].text
                else:
                    context_data = str(result.content[0].text if hasattr(result, 'content') else result)
                print(f"✓ Session context: {context_data[:200]}")
            print()
            
            # Test 3: List clusters
            print("TEST 3: List Clusters")
            print("-" * 40)
            try:
                result = await client.call_tool("list_clusters", {})
                if result:
                    if isinstance(result, list):
                        clusters_data = result[0].content[0].text
                    else:
                        clusters_data = str(result.content[0].text if hasattr(result, 'content') else result)
                    print(f"✓ Clusters retrieved:")
                    print(f"  {clusters_data[:300]}...")
                print()
            except Exception as e:
                print(f"⚠ Error listing clusters: {str(e)[:200]}")
                print()
            
            # Test 4: List jobs
            print("TEST 4: List Jobs")
            print("-" * 40)
            try:
                result = await client.call_tool("list_jobs", {"limit": 5})
                if result:
                    jobs_data = str(result.content[0].text if hasattr(result, 'content') else result)[:300]
                    print(f"✓ Jobs retrieved:")
                    print(f"  {jobs_data}...")
                print()
            except Exception as e:
                print(f"⚠ Error listing jobs: {str(e)[:200]}")
                print()
            
            # Test 5: List workspace
            print("TEST 5: List Workspace")
            print("-" * 40)
            try:
                result = await client.call_tool("list_workspace", {"path": "/Workspace"})
                if result:
                    workspace_data = str(result.content[0].text if hasattr(result, 'content') else result)[:300]
                    print(f"✓ Workspace objects retrieved:")
                    print(f"  {workspace_data}...")
                print()
            except Exception as e:
                print(f"⚠ Error listing workspace: {str(e)[:200]}")
                print()
            
            # Test 6: Set workspace path (stateful operation)
            print("TEST 6: Set Workspace Path (Stateful)")
            print("-" * 40)
            try:
                result = await client.call_tool("set_workspace_path", {"path": "/Workspace/Users"})
                if result:
                    message = str(result.content[0].text if hasattr(result, 'content') else result)
                    print(f"✓ {message}")
                
                # Verify context was updated
                result = await client.call_tool("get_session_context", {})
                if result:
                    context_data = str(result.content[0].text if hasattr(result, 'content') else result)[:200]
                    print(f"✓ Updated context: {context_data}")
                print()
            except Exception as e:
                print(f"⚠ Error setting workspace path: {str(e)[:200]}")
                print()
            
            # Test 7: List SQL warehouses
            print("TEST 7: List SQL Warehouses")
            print("-" * 40)
            try:
                result = await client.call_tool("list_warehouses", {})
                if result:
                    warehouses_data = str(result.content[0].text if hasattr(result, 'content') else result)[:300]
                    print(f"✓ SQL warehouses retrieved:")
                    print(f"  {warehouses_data}...")
                print()
            except Exception as e:
                print(f"⚠ Error listing warehouses: {str(e)[:200]}")
                print()
            
            # Test 8: List Unity Catalog catalogs
            print("TEST 8: List Unity Catalog Catalogs")
            print("-" * 40)
            try:
                result = await client.call_tool("list_catalogs", {})
                if result:
                    catalogs_data = str(result.content[0].text if hasattr(result, 'content') else result)[:300]
                    print(f"✓ UC catalogs retrieved:")
                    print(f"  {catalogs_data}...")
                print()
            except Exception as e:
                print(f"⚠ Error listing catalogs: {str(e)[:200]}")
                print()
            
            # Test 9: List secret scopes
            print("TEST 9: List Secret Scopes")
            print("-" * 40)
            try:
                result = await client.call_tool("list_secret_scopes", {})
                if result:
                    scopes_data = str(result.content[0].text if hasattr(result, 'content') else result)[:300]
                    print(f"✓ Secret scopes retrieved:")
                    print(f"  {scopes_data}...")
                print()
            except Exception as e:
                print(f"⚠ Error listing secret scopes: {str(e)[:200]}")
                print()
            
            print("=" * 80)
            print("Testing Complete!")
            print("=" * 80)
            print()
            print("Summary:")
            print("  ✓ Successfully connected to MCP server")
            print("  ✓ Authenticated with Databricks")
            print("  ✓ Tested stateful session context")
            print("  ✓ Verified multiple tool categories")
            print()
            print("Next steps:")
            print("  1. Review any errors above")
            print("  2. Test specific operations relevant to your use case")
            print("  3. Deploy to Databricks Apps for production use")
            print()
            
    except Exception as e:
        print(f"✗ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def main():
    """Main entry point."""
    print()
    print("Databricks CLI MCP Server - Local Test")
    print()
    
    # Check if credentials are configured
    if "your-workspace" in DATABRICKS_HOST or "your-personal" in DATABRICKS_TOKEN:
        print("⚠ ERROR: Please configure your Databricks credentials in test_local.py")
        print()
        print("Update these variables:")
        print("  DATABRICKS_HOST = 'https://your-workspace.cloud.databricks.com'")
        print("  DATABRICKS_TOKEN = 'your-personal-access-token'")
        print()
        print("To get a personal access token:")
        print("  1. Go to your Databricks workspace")
        print("  2. Click your username → Settings → Developer")
        print("  3. Click 'Manage' next to Access tokens")
        print("  4. Click 'Generate new token'")
        print()
        sys.exit(1)
    
    print("Configuration:")
    print(f"  Host: {DATABRICKS_HOST}")
    print(f"  Token: {'*' * 20}{DATABRICKS_TOKEN[-4:]}")
    print(f"  Server: {SERVER_URL}")
    print()
    print("Starting tests...")
    print()
    
    asyncio.run(test_mcp_server())


if __name__ == "__main__":
    main()

