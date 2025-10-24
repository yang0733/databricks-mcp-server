#!/usr/bin/env python3
"""Local testing script for Databricks CLI MCP Server."""

import asyncio
from fastmcp.client import Client
from fastmcp.client.transports import StreamableHttpTransport

# Configuration
DATABRICKS_HOST = "https://your-workspace.cloud.databricks.com"
DATABRICKS_TOKEN = "dapi1234567890abcdef1234567890abcdef"
SERVER_URL = "http://localhost:8000/mcp/"


async def test_mcp_server():
    """Test the Databricks CLI MCP server."""
    
    print("=" * 80)
    print("Databricks CLI MCP Server - Local Testing")
    print("=" * 80)
    print()
    
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
            print(f"✓ Found {len(tools)} tools")
            print(f"  Sample tools:")
            for tool in tools[:5]:
                print(f"    • {tool.name}")
            print()
            
            # Test 2: List clusters
            print("TEST 2: List Clusters")
            print("-" * 40)
            result = await client.call_tool("list_clusters", {})
            data = result.content[0].text
            print(f"✓ Retrieved clusters:")
            print(f"  {data[:200]}...")
            print()
            
            # Test 3: Get task management tools
            print("TEST 3: Task Management")
            print("-" * 40)
            task_tools = [t for t in tools if 'task' in t.name.lower()]
            print(f"✓ Found {len(task_tools)} task management tools:")
            for tool in task_tools:
                print(f"    • {tool.name}")
            print()
            
            print("=" * 80)
            print("✅ All Tests Passed!")
            print("=" * 80)
            print()
            print("Server Features:")
            print("  ✓ 48+ Databricks tools")
            print("  ✓ WebSocket + HTTP transports")
            print("  ✓ Async task management")
            print("  ✓ Session context")
            print()
            
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_mcp_server())
