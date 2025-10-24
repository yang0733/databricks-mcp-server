#!/usr/bin/env python3
"""
Simple test to verify the chat agent infrastructure works.

This tests the agent's ability to connect to the MCP server and
understand the available tools, without requiring an Anthropic API key.
"""

import asyncio
import os
from fastmcp.client import Client
from fastmcp.client.transports import StreamableHttpTransport

# Configuration
DATABRICKS_HOST = os.getenv("DATABRICKS_HOST", "https://e2-demo-west.cloud.databricks.com")
DATABRICKS_TOKEN = os.getenv("DATABRICKS_TOKEN", "dapi14c8fa7e4aaa0907a3144b740fd91f50")
SERVER_URL = "http://localhost:8000/mcp/"


async def test_agent_infrastructure():
    """Test that the chat agent can connect and list tools."""
    
    print("=" * 80)
    print("🧪 TESTING CHAT AGENT INFRASTRUCTURE")
    print("=" * 80)
    print()
    
    # Initialize MCP client
    headers = {
        "x-databricks-host": DATABRICKS_HOST,
        "x-databricks-token": DATABRICKS_TOKEN,
        "x-session-id": "test-chat-session"
    }
    
    transport = StreamableHttpTransport(SERVER_URL, headers=headers)
    
    try:
        async with Client(transport=transport) as mcp_client:
            print("✓ Connected to MCP server")
            print()
            
            # List available tools
            print("📋 Loading available tools...")
            tools = await mcp_client.list_tools()
            print(f"✓ Found {len(tools)} tools")
            print()
            
            # Display tools by category
            categories = {}
            for tool in tools:
                # Extract category from tool name (e.g., "list_clusters" -> "clusters")
                parts = tool.name.split('_')
                if len(parts) > 1:
                    category = parts[-1]
                    if category not in categories:
                        categories[category] = []
                    categories[category].append(tool.name)
            
            print("📦 Tools by category:")
            for category, tool_names in sorted(categories.items()):
                print(f"\n  {category.upper()}:")
                for name in sorted(tool_names)[:5]:  # Show first 5
                    print(f"    • {name}")
                if len(tool_names) > 5:
                    print(f"    ... and {len(tool_names) - 5} more")
            
            print()
            print("=" * 80)
            print()
            
            # Test a simple tool call
            print("🔧 Testing tool execution...")
            print("   Calling: get_session_context")
            
            result = await mcp_client.call_tool("get_session_context", {})
            
            if isinstance(result, list):
                result_text = result[0].content[0].text
            elif hasattr(result, 'content'):
                result_text = result.content[0].text
            else:
                result_text = str(result)
            
            print(f"   ✓ Result: {result_text[:100]}...")
            print()
            
            # Simulate what an LLM would do
            print("=" * 80)
            print("🤖 SIMULATED CONVERSATION FLOW")
            print("=" * 80)
            print()
            print("User: 'Show me all my clusters'")
            print()
            print("LLM Process:")
            print("  1. ✓ Understand intent: User wants to see clusters")
            print("  2. ✓ Select tool: list_clusters")
            print("  3. ✓ Execute tool via MCP")
            print()
            
            # Actually call list_clusters
            print("🔧 Executing: list_clusters")
            result = await mcp_client.call_tool("list_clusters", {})
            
            if isinstance(result, list):
                result_text = result[0].content[0].text
            elif hasattr(result, 'content'):
                result_text = result.content[0].text
            else:
                result_text = str(result)
            
            print(f"   ✓ Result (first 300 chars):")
            print(f"   {result_text[:300]}...")
            print()
            print("  4. ✓ Format response for user")
            print()
            print("Agent: 'I found your clusters. Let me show you...'")
            print("       [formats the cluster data in a user-friendly way]")
            print()
            
            print("=" * 80)
            print("✅ INFRASTRUCTURE TEST COMPLETE")
            print("=" * 80)
            print()
            print("Next steps:")
            print("  1. Set ANTHROPIC_API_KEY environment variable")
            print("  2. Run: python chat_agent.py")
            print("  3. Start chatting with your Databricks workspace!")
            print()
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


def main():
    """Main entry point."""
    success = asyncio.run(test_agent_infrastructure())
    exit(0 if success else 1)


if __name__ == "__main__":
    main()

