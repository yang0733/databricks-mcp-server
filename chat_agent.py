#!/usr/bin/env python3
"""
Interactive Chat Agent for Databricks MCP Server

This agent provides a natural language interface to Databricks operations.
Users can chat with the agent, which uses an LLM to understand intent and
execute appropriate MCP tools.

Requirements:
    pip install anthropic  # or openai for GPT
"""

import asyncio
import sys
import json
import os
from typing import Optional, List, Dict, Any
from fastmcp.client import Client
from fastmcp.client.transports import StreamableHttpTransport

try:
    from anthropic import Anthropic
    HAS_ANTHROPIC = True
except ImportError:
    HAS_ANTHROPIC = False
    print("⚠️  Warning: anthropic package not installed. Install with: pip install anthropic")

# Configuration
DATABRICKS_HOST = os.getenv("DATABRICKS_HOST", "https://e2-demo-west.cloud.databricks.com")
DATABRICKS_TOKEN = os.getenv("DATABRICKS_TOKEN", "dapi14c8fa7e4aaa0907a3144b740fd91f50")
SERVER_URL = "http://localhost:8000/mcp/"
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")  # Set your API key


class DatabricksAgent:
    """Natural language agent for Databricks operations."""
    
    def __init__(self, mcp_client: Client, llm_client: Any):
        self.mcp = mcp_client
        self.llm = llm_client
        self.conversation_history = []
        self.available_tools = []
        self.system_prompt = """You are a helpful Databricks assistant. You help users interact with their Databricks workspace through natural conversation.

You have access to 48+ tools for managing Databricks resources:
- Clusters: create, start, stop, list, get details
- Jobs: create, run, list, cancel, delete
- Notebooks: import, export, list, run
- Workspace: list, import/export files, manage directories
- SQL: execute queries, manage warehouses
- Unity Catalog: browse catalogs, schemas, tables
- Secrets: manage secret scopes and values
- Git Repos: link and manage repositories

When users ask questions:
1. Understand their intent
2. Use the appropriate MCP tools to get information or perform actions
3. Present results in a clear, conversational way
4. Ask for clarification if needed

Be concise but informative. Focus on what the user wants to accomplish."""
        
    async def initialize(self):
        """Load available tools from MCP server."""
        self.available_tools = await self.mcp.list_tools()
        print(f"✓ Loaded {len(self.available_tools)} tools from MCP server")
        
    def extract_result(self, result) -> str:
        """Helper to extract text from MCP result."""
        if isinstance(result, list):
            return result[0].content[0].text
        elif hasattr(result, 'content'):
            return result.content[0].text
        else:
            return str(result)
    
    def format_tools_for_llm(self) -> List[Dict]:
        """Format MCP tools for Anthropic's tool calling."""
        formatted_tools = []
        
        for tool in self.available_tools:
            # Convert MCP tool to Anthropic format
            tool_def = {
                "name": tool.name,
                "description": tool.description or f"Execute {tool.name} operation",
                "input_schema": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            }
            
            # Add input schema if available
            if hasattr(tool, 'inputSchema') and tool.inputSchema:
                schema = tool.inputSchema
                if isinstance(schema, dict):
                    tool_def["input_schema"] = schema
            
            formatted_tools.append(tool_def)
        
        return formatted_tools
    
    async def execute_tool(self, tool_name: str, tool_input: Dict) -> str:
        """Execute an MCP tool and return the result."""
        try:
            result = await self.mcp.call_tool(tool_name, tool_input)
            result_text = self.extract_result(result)
            
            # Try to parse as JSON for pretty printing
            try:
                result_json = json.loads(result_text)
                return json.dumps(result_json, indent=2)
            except:
                return result_text
                
        except Exception as e:
            return f"Error executing {tool_name}: {str(e)}"
    
    async def chat(self, user_message: str) -> str:
        """Process user message and return response."""
        
        # Add user message to history
        self.conversation_history.append({
            "role": "user",
            "content": user_message
        })
        
        # Call LLM with tools
        response = self.llm.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=4096,
            system=self.system_prompt,
            messages=self.conversation_history,
            tools=self.format_tools_for_llm()[:20],  # Limit to first 20 tools for token efficiency
        )
        
        # Process response
        assistant_message = ""
        tool_results = []
        
        while response.stop_reason == "tool_use":
            # Extract tool calls
            for content in response.content:
                if content.type == "text":
                    assistant_message += content.text
                elif content.type == "tool_use":
                    tool_name = content.name
                    tool_input = content.input
                    
                    print(f"\n🔧 Executing: {tool_name}")
                    print(f"   Parameters: {json.dumps(tool_input, indent=2)[:100]}...")
                    
                    # Execute the tool
                    result = await self.execute_tool(tool_name, tool_input)
                    
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": content.id,
                        "content": result
                    })
            
            # Add assistant response to history
            self.conversation_history.append({
                "role": "assistant",
                "content": response.content
            })
            
            # Add tool results to history
            if tool_results:
                self.conversation_history.append({
                    "role": "user",
                    "content": tool_results
                })
            
            # Get next response from LLM
            response = self.llm.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=4096,
                system=self.system_prompt,
                messages=self.conversation_history,
                tools=self.format_tools_for_llm()[:20],
            )
            
            tool_results = []
        
        # Extract final text response
        for content in response.content:
            if content.type == "text":
                assistant_message += content.text
        
        # Add final response to history
        self.conversation_history.append({
            "role": "assistant",
            "content": assistant_message
        })
        
        return assistant_message


async def run_interactive_chat():
    """Run the interactive chat interface."""
    
    print("=" * 80)
    print("🤖 DATABRICKS CHAT AGENT")
    print("=" * 80)
    print()
    print("Chat naturally with your Databricks workspace!")
    print()
    print("Examples:")
    print("  • 'Show me all my clusters'")
    print("  • 'Run a SQL query to get 5 rows from samples.nyctaxi.trips'")
    print("  • 'List my recent jobs'")
    print("  • 'What Unity Catalog tables are available?'")
    print()
    print("Type 'exit' or 'quit' to end the conversation")
    print("=" * 80)
    print()
    
    # Check for Anthropic API key
    if not ANTHROPIC_API_KEY:
        print("❌ Error: ANTHROPIC_API_KEY environment variable not set")
        print()
        print("Please set your Anthropic API key:")
        print("  export ANTHROPIC_API_KEY='your-api-key-here'")
        print()
        print("Get your API key at: https://console.anthropic.com/")
        return
    
    if not HAS_ANTHROPIC:
        print("❌ Error: anthropic package not installed")
        print()
        print("Install with: pip install anthropic")
        return
    
    # Initialize MCP client
    headers = {
        "x-databricks-host": DATABRICKS_HOST,
        "x-databricks-token": DATABRICKS_TOKEN,
        "x-session-id": "chat-agent-session"
    }
    
    transport = StreamableHttpTransport(SERVER_URL, headers=headers)
    
    async with Client(transport=transport) as mcp_client:
        print("✓ Connected to Databricks MCP Server")
        
        # Initialize LLM client
        llm_client = Anthropic(api_key=ANTHROPIC_API_KEY)
        print("✓ Connected to Claude")
        print()
        
        # Create agent
        agent = DatabricksAgent(mcp_client, llm_client)
        await agent.initialize()
        print()
        
        # Chat loop
        while True:
            try:
                # Get user input
                user_input = input("You: ").strip()
                
                if not user_input:
                    continue
                
                if user_input.lower() in ['exit', 'quit', 'bye']:
                    print()
                    print("👋 Goodbye! Thanks for using Databricks Chat Agent!")
                    break
                
                print()
                print("🤔 Thinking...")
                
                # Get agent response
                response = await agent.chat(user_input)
                
                print()
                print(f"Agent: {response}")
                print()
                
            except KeyboardInterrupt:
                print()
                print()
                print("👋 Goodbye! Thanks for using Databricks Chat Agent!")
                break
            except Exception as e:
                print()
                print(f"❌ Error: {str(e)}")
                print()


def main():
    """Main entry point."""
    try:
        asyncio.run(run_interactive_chat())
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

