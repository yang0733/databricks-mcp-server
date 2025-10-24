#!/usr/bin/env python3
"""
Interactive Chat Agent for Databricks MCP Server - Ollama Version

This agent uses Ollama (local LLM) instead of cloud-based APIs.
Completely free and runs entirely on your machine!

Requirements:
    1. Ollama installed: https://ollama.ai
    2. A model pulled: ollama pull llama3.1 (or mistral, qwen, etc.)
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
DATABRICKS_TOKEN = os.getenv("DATABRICKS_TOKEN", "dapi14c8fa7e4aaa0907a3144b740fd91f50")
SERVER_URL = "http://localhost:8000/mcp/"
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:7b")  # or phi4, phi3.5, etc.


class OllamaClient:
    """Simple Ollama API client."""
    
    def __init__(self, base_url: str = OLLAMA_URL, model: str = OLLAMA_MODEL):
        self.base_url = base_url
        self.model = model
        self.client = httpx.AsyncClient(timeout=120.0)
    
    async def chat(self, messages: List[Dict], tools: Optional[List[Dict]] = None) -> Dict:
        """Send chat request to Ollama."""
        
        # Prepare the prompt with tool information
        system_prompt = messages[0]["content"] if messages[0]["role"] == "system" else ""
        
        # Add tool descriptions to the prompt
        if tools:
            tool_descriptions = "\n\nAvailable tools:\n"
            for tool in tools:
                tool_descriptions += f"\n- {tool['name']}: {tool['description']}"
                if tool.get('parameters'):
                    tool_descriptions += f"\n  Parameters: {json.dumps(tool['parameters'], indent=2)}"
            system_prompt += tool_descriptions
        
        # Build conversation
        conversation = []
        for msg in messages:
            if msg["role"] == "system":
                continue
            conversation.append(msg)
        
        # Create the prompt
        full_prompt = f"{system_prompt}\n\n"
        for msg in conversation:
            role = msg["role"]
            content = msg["content"]
            if isinstance(content, str):
                full_prompt += f"{role.upper()}: {content}\n"
        
        full_prompt += "\nASSISTANT: "
        
        # Call Ollama
        try:
            response = await self.client.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": full_prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.7,
                        "top_p": 0.9,
                    }
                }
            )
            
            if response.status_code != 200:
                return {"error": f"Ollama API error: {response.status_code}"}
            
            result = response.json()
            return {
                "response": result.get("response", ""),
                "done": result.get("done", True)
            }
        except Exception as e:
            return {"error": str(e)}
    
    async def close(self):
        await self.client.aclose()


class DatabricksAgentOllama:
    """Natural language agent for Databricks operations using Ollama."""
    
    def __init__(self, mcp_client: Client, ollama_client: OllamaClient):
        self.mcp = mcp_client
        self.llm = ollama_client
        self.conversation_history = []
        self.available_tools = []
        self.tool_map = {}
        self.system_prompt = """You are a helpful Databricks assistant. You help users interact with their Databricks workspace through natural conversation.

When users ask questions:
1. Understand their intent
2. Determine which tool(s) to use
3. If you need to call a tool, respond with: TOOL_CALL: tool_name(param1=value1, param2=value2)
4. Otherwise, provide a helpful conversational response

Be concise and clear. Focus on what the user wants to accomplish."""
        
    async def initialize(self):
        """Load available tools from MCP server."""
        self.available_tools = await self.mcp.list_tools()
        
        # Create tool map
        for tool in self.available_tools:
            self.tool_map[tool.name] = tool
        
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
        """Format MCP tools for LLM."""
        formatted_tools = []
        
        for tool in self.available_tools[:20]:  # Limit to 20 for context size
            tool_def = {
                "name": tool.name,
                "description": tool.description or f"Execute {tool.name} operation",
                "parameters": {}
            }
            
            if hasattr(tool, 'inputSchema') and tool.inputSchema:
                schema = tool.inputSchema
                if isinstance(schema, dict):
                    tool_def["parameters"] = schema.get("properties", {})
            
            formatted_tools.append(tool_def)
        
        return formatted_tools
    
    def parse_tool_call(self, response: str) -> Optional[tuple]:
        """Parse tool call from LLM response."""
        if "TOOL_CALL:" not in response:
            return None
        
        try:
            # Extract tool call
            tool_part = response.split("TOOL_CALL:")[1].strip().split("\n")[0]
            
            # Parse tool name and parameters
            if "(" in tool_part:
                tool_name = tool_part.split("(")[0].strip()
                params_str = tool_part.split("(")[1].split(")")[0]
                
                # Parse parameters
                params = {}
                if params_str:
                    for param in params_str.split(","):
                        if "=" in param:
                            key, value = param.split("=", 1)
                            key = key.strip()
                            value = value.strip().strip("'\"")
                            params[key] = value
                
                return (tool_name, params)
            else:
                return (tool_part.strip(), {})
        except Exception as e:
            print(f"Error parsing tool call: {e}")
            return None
    
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
        
        # Prepare messages for LLM
        messages = [
            {"role": "system", "content": self.system_prompt},
            *self.conversation_history
        ]
        
        # Get LLM response
        llm_response = await self.llm.chat(
            messages=messages,
            tools=self.format_tools_for_llm()
        )
        
        if "error" in llm_response:
            return f"Error: {llm_response['error']}"
        
        response_text = llm_response.get("response", "")
        
        # Check if LLM wants to call a tool
        tool_call = self.parse_tool_call(response_text)
        
        if tool_call:
            tool_name, tool_params = tool_call
            
            print(f"\n🔧 Executing: {tool_name}")
            if tool_params:
                print(f"   Parameters: {json.dumps(tool_params, indent=2)}")
            
            # Execute the tool
            tool_result = await self.execute_tool(tool_name, tool_params)
            
            # Add tool result to context
            self.conversation_history.append({
                "role": "assistant",
                "content": f"I called {tool_name} and got:\n{tool_result[:500]}..."
            })
            
            # Get final response from LLM
            messages = [
                {"role": "system", "content": self.system_prompt},
                *self.conversation_history,
                {"role": "user", "content": "Based on the tool results, provide a helpful response to the user."}
            ]
            
            final_response = await self.llm.chat(messages=messages)
            response_text = final_response.get("response", "")
        
        # Add response to history
        self.conversation_history.append({
            "role": "assistant",
            "content": response_text
        })
        
        return response_text


async def check_ollama():
    """Check if Ollama is running and model is available."""
    try:
        async with httpx.AsyncClient() as client:
            # Check if Ollama is running
            response = await client.get(f"{OLLAMA_URL}/api/tags", timeout=5.0)
            if response.status_code != 200:
                return False, "Ollama is not responding"
            
            # Check if model is available
            models = response.json().get("models", [])
            model_names = [m["name"] for m in models]
            
            if not any(OLLAMA_MODEL in name for name in model_names):
                return False, f"Model '{OLLAMA_MODEL}' not found. Available: {', '.join(model_names)}"
            
            return True, f"Ollama is running with model: {OLLAMA_MODEL}"
    except Exception as e:
        return False, f"Cannot connect to Ollama: {str(e)}"


async def run_interactive_chat():
    """Run the interactive chat interface."""
    
    print("=" * 80)
    print("🤖 DATABRICKS CHAT AGENT - OLLAMA VERSION")
    print("=" * 80)
    print()
    print("Chat naturally with your Databricks workspace using a local LLM!")
    print()
    print("Examples:")
    print("  • 'Show me all my clusters'")
    print("  • 'List my recent jobs'")
    print("  • 'What tables are available?'")
    print()
    print("Type 'exit' or 'quit' to end the conversation")
    print("=" * 80)
    print()
    
    # Check Ollama
    print("Checking Ollama...")
    is_running, message = await check_ollama()
    if not is_running:
        print(f"❌ {message}")
        print()
        print("To fix:")
        print("  1. Install Ollama: https://ollama.ai")
        print("  2. Start Ollama: just run 'ollama' in terminal")
        print(f"  3. Pull a model: ollama pull {OLLAMA_MODEL}")
        print()
        return
    
    print(f"✓ {message}")
    print()
    
    # Initialize MCP client
    headers = {
        "x-databricks-host": DATABRICKS_HOST,
        "x-databricks-token": DATABRICKS_TOKEN,
        "x-session-id": "chat-agent-ollama-session"
    }
    
    transport = StreamableHttpTransport(SERVER_URL, headers=headers)
    
    async with Client(transport=transport) as mcp_client:
        print("✓ Connected to Databricks MCP Server")
        
        # Initialize Ollama client
        ollama_client = OllamaClient()
        print(f"✓ Connected to Ollama ({OLLAMA_MODEL})")
        print()
        
        # Create agent
        agent = DatabricksAgentOllama(mcp_client, ollama_client)
        await agent.initialize()
        print()
        print("💡 Tip: Be specific in your requests. For example:")
        print("   'List all clusters' instead of 'show me stuff'")
        print()
        
        # Chat loop
        try:
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
        finally:
            await ollama_client.close()


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

