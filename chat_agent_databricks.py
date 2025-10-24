#!/usr/bin/env python3
"""
Interactive Chat Agent for Databricks MCP Server - Databricks Claude Edition

Uses Claude Sonnet 4.5 via Databricks Model Serving endpoint.
"""

import asyncio
import sys
import json
import os
import httpx
from typing import Optional, List, Dict, Any
from fastmcp.client import Client
from fastmcp.client.transports import StreamableHttpTransport

# Configuration
DATABRICKS_HOST = os.getenv("DATABRICKS_HOST", "https://e2-demo-west.cloud.databricks.com")
DATABRICKS_TOKEN = os.getenv("DATABRICKS_TOKEN")
MCP_SERVER_URL = os.getenv("MCP_SERVER_URL", "http://localhost:8000/mcp/")
CLAUDE_ENDPOINT = os.getenv("CLAUDE_ENDPOINT", "https://e2-demo-west.cloud.databricks.com/serving-endpoints/databricks-claude-sonnet-4-5/invocations")


class DatabricksClaudeClient:
    """Client for Databricks Claude Model Serving."""
    
    def __init__(self, endpoint_url: str, token: str):
        self.endpoint_url = endpoint_url
        self.token = token
        self.client = httpx.AsyncClient(timeout=120.0)
    
    async def chat(self, messages: List[Dict], tools: Optional[List[Dict]] = None) -> Dict:
        """Send chat request to Databricks Claude endpoint."""
        
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "messages": messages,
            "max_tokens": 4096,
            "temperature": 0.7,
        }
        
        if tools:
            payload["tools"] = tools
        
        try:
            response = await self.client.post(
                self.endpoint_url,
                headers=headers,
                json=payload
            )
            
            if response.status_code != 200:
                return {"error": f"Databricks Claude API error: {response.status_code} - {response.text}"}
            
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    async def close(self):
        await self.client.aclose()


class DatabricksAgent:
    """Natural language agent for Databricks operations using Databricks Claude."""
    
    def __init__(self, mcp_client: Client, claude_client: DatabricksClaudeClient):
        self.mcp = mcp_client
        self.llm = claude_client
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
    
    def format_tools_for_claude(self) -> List[Dict]:
        """Format MCP tools for Claude's tool calling."""
        formatted_tools = []
        
        for tool in self.available_tools:
            tool_def = {
                "name": tool.name,
                "description": tool.description or f"Execute {tool.name} operation",
                "input_schema": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            }
            
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
            
            try:
                result_json = json.loads(result_text)
                return json.dumps(result_json, indent=2)
            except:
                return result_text
                
        except Exception as e:
            return f"Error executing {tool_name}: {str(e)}"
    
    async def chat(self, user_message: str) -> str:
        """Process user message and return response."""
        
        self.conversation_history.append({
            "role": "user",
            "content": user_message
        })
        
        messages = [
            {"role": "system", "content": self.system_prompt},
            *self.conversation_history
        ]
        
        response = await self.llm.chat(
            messages=messages,
            tools=self.format_tools_for_claude()[:20]
        )
        
        if "error" in response:
            return f"Error: {response['error']}"
        
        assistant_message = ""
        tool_results = []
        
        stop_reason = response.get("stop_reason")
        
        while stop_reason == "tool_use":
            for content in response.get("content", []):
                if content.get("type") == "text":
                    assistant_message += content.get("text", "")
                elif content.get("type") == "tool_use":
                    tool_name = content.get("name")
                    tool_input = content.get("input", {})
                    tool_id = content.get("id")
                    
                    print(f"\n🔧 Executing: {tool_name}")
                    if tool_input:
                        print(f"   Parameters: {json.dumps(tool_input, indent=2)[:100]}...")
                    
                    result = await self.execute_tool(tool_name, tool_input)
                    
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": tool_id,
                        "content": result
                    })
            
            self.conversation_history.append({
                "role": "assistant",
                "content": response.get("content", [])
            })
            
            if tool_results:
                self.conversation_history.append({
                    "role": "user",
                    "content": tool_results
                })
            
            messages = [
                {"role": "system", "content": self.system_prompt},
                *self.conversation_history
            ]
            
            response = await self.llm.chat(
                messages=messages,
                tools=self.format_tools_for_claude()[:20]
            )
            
            if "error" in response:
                return f"Error: {response['error']}"
            
            stop_reason = response.get("stop_reason")
            tool_results = []
        
        for content in response.get("content", []):
            if content.get("type") == "text":
                assistant_message += content.get("text", "")
        
        self.conversation_history.append({
            "role": "assistant",
            "content": assistant_message
        })
        
        return assistant_message


async def run_interactive_chat():
    """Run the interactive chat interface."""
    
    print("=" * 80)
    print("🤖 DATABRICKS CHAT AGENT - CLAUDE SONNET 4.5")
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
    
    if not DATABRICKS_TOKEN:
        print("❌ Error: DATABRICKS_TOKEN environment variable not set")
        return
    
    headers = {
        "x-databricks-host": DATABRICKS_HOST,
        "x-databricks-token": DATABRICKS_TOKEN,
        "x-session-id": "chat-agent-session"
    }
    
    transport = StreamableHttpTransport(MCP_SERVER_URL, headers=headers)
    
    async with Client(transport=transport) as mcp_client:
        print("✓ Connected to Databricks MCP Server")
        
        claude_client = DatabricksClaudeClient(CLAUDE_ENDPOINT, DATABRICKS_TOKEN)
        print("✓ Connected to Claude Sonnet 4.5 (via Databricks)")
        print()
        
        agent = DatabricksAgent(mcp_client, claude_client)
        await agent.initialize()
        print()
        
        try:
            while True:
                try:
                    user_input = input("You: ").strip()
                    
                    if not user_input:
                        continue
                    
                    if user_input.lower() in ['exit', 'quit', 'bye']:
                        print()
                        print("👋 Goodbye! Thanks for using Databricks Chat Agent!")
                        break
                    
                    print()
                    print("🤔 Thinking...")
                    
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
        finally:
            await claude_client.close()


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

