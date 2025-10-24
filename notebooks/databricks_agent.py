# Databricks notebook source
# MAGIC %md
# MAGIC # Databricks CLI MCP Agent
# MAGIC
# MAGIC Natural language interface for Databricks operations using:
# MAGIC - **MCP Server**: Databricks CLI tools (deployed as Databricks App)
# MAGIC - **LLM**: Claude Sonnet 4.5 (Databricks hosted)
# MAGIC
# MAGIC ## Quick Start
# MAGIC 1. Configure MCP_SERVER_URL below
# MAGIC 2. Run all cells
# MAGIC 3. Chat in natural language!

# COMMAND ----------

# MAGIC %md
# MAGIC ## Setup

# COMMAND ----------

# MAGIC %pip install openai mcp --quiet
# MAGIC dbutils.library.restartPython()

# COMMAND ----------

import asyncio
import json
from typing import List, Dict, Optional
from openai import AsyncOpenAI
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client
from databricks_mcp import DatabricksOAuthClientProvider
from databricks.sdk import WorkspaceClient

# Configuration
MCP_SERVER_URL = "https://databricks-mcp-server-2556758628403379.aws.databricksapps.com/mcp"
CLAUDE_MODEL = "your-llm-endpoint"

# Get Databricks context
workspace_client = WorkspaceClient()
databricks_token = dbutils.notebook.entry_point.getDbutils().notebook().getContext().apiToken().get()
workspace_url = dbutils.notebook.entry_point.getDbutils().notebook().getContext().apiUrl().get()

# Initialize Claude client
claude = AsyncOpenAI(
    api_key=databricks_token,
    base_url=f"{workspace_url}/serving-endpoints"
)

print("✅ Setup complete!")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Agent Implementation

# COMMAND ----------

class DatabricksAgent:
    """Natural language agent for Databricks operations."""
    
    def __init__(self, mcp_url: str, claude_client: AsyncOpenAI, model: str):
        self.mcp_url = mcp_url
        self.claude = claude_client
        self.model = model
        self.conversation = []
        self.tools = []
        
    async def initialize(self):
        """Connect to MCP server and load tools."""
        async with streamablehttp_client(
            self.mcp_url,
            auth=DatabricksOAuthClientProvider(workspace_client)
        ) as streams:
            async with ClientSession(*streams[:2]) as session:
                await session.initialize()
                response = await session.list_tools()
                self.tools = response.tools
                print(f"✅ Loaded {len(self.tools)} tools from MCP server")
    
    def format_tools(self) -> List[Dict]:
        """Convert MCP tools to OpenAI format."""
        formatted = []
        for tool in self.tools[:20]:  # Limit for performance
            schema = tool.inputSchema or {}
            
            # Simplify schema for Claude
            simple_schema = {
                "type": "object",
                "properties": {},
                "required": schema.get("required", [])
            }
            
            for prop_name, prop_def in schema.get("properties", {}).items():
                if not isinstance(prop_def, dict):
                    continue
                    
                simple_prop = {}
                if "type" in prop_def:
                    simple_prop["type"] = prop_def["type"]
                elif "anyOf" in prop_def:
                    for option in prop_def["anyOf"]:
                        if isinstance(option, dict) and option.get("type") != "null":
                            simple_prop["type"] = option["type"]
                            break
                    if "type" not in simple_prop:
                        simple_prop["type"] = "string"
                else:
                    simple_prop["type"] = "string"
                
                if "description" in prop_def:
                    simple_prop["description"] = prop_def["description"]
                
                simple_schema["properties"][prop_name] = simple_prop
            
            formatted.append({
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description or tool.name,
                    "parameters": simple_schema
                }
            })
        
        return formatted
    
    async def execute_tool(self, tool_name: str, arguments: Dict) -> str:
        """Execute an MCP tool."""
        async with streamablehttp_client(
            self.mcp_url,
            auth=DatabricksOAuthClientProvider(workspace_client)
        ) as streams:
            async with ClientSession(*streams[:2]) as session:
                await session.initialize()
                result = await session.call_tool(tool_name, arguments)
                return str(result.content[0].text)
    
    async def chat(self, user_message: str) -> str:
        """Process user message and return response."""
        
        # Add user message
        self.conversation.append({
            "role": "user",
            "content": user_message
        })
        
        # System prompt
        system = """You are a Databricks assistant. Help users manage their Databricks workspace.

Available tools: clusters, jobs, SQL, notebooks, workspace, Unity Catalog, repos, secrets.

Be concise and helpful."""
        
        # Call Claude
        response = await self.claude.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system},
                *self.conversation
            ],
            tools=self.format_tools(),
            tool_choice="auto",
            max_tokens=4096
        )
        
        choice = response.choices[0]
        message = choice.message
        
        # Check for tool calls
        if message.tool_calls:
            tool_results = []
            
            for tool_call in message.tool_calls:
                tool_name = tool_call.function.name
                arguments = json.loads(tool_call.function.arguments)
                
                print(f"🔧 Executing: {tool_name}")
                
                try:
                    result = await self.execute_tool(tool_name, arguments)
                    tool_results.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": result[:2000]  # Limit size
                    })
                except Exception as e:
                    tool_results.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": f"Error: {str(e)}"
                    })
            
            # Add assistant message with tool calls
            self.conversation.append({
                "role": "assistant",
                "content": message.content or "",
                "tool_calls": [{
                    "id": tc.id,
                    "type": tc.type,
                    "function": {
                        "name": tc.function.name,
                        "arguments": tc.function.arguments
                    }
                } for tc in message.tool_calls]
            })
            
            # Add tool results
            self.conversation.extend(tool_results)
            
            # Get final response
            final_response = await self.claude.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system},
                    *self.conversation
                ],
                max_tokens=4096
            )
            
            final_message = final_response.choices[0].message.content
            self.conversation.append({
                "role": "assistant",
                "content": final_message
            })
            
            return final_message
        else:
            # No tools needed
            self.conversation.append({
                "role": "assistant",
                "content": message.content
            })
            return message.content

# COMMAND ----------

# MAGIC %md
# MAGIC ## Interactive Chat

# COMMAND ----------

# Create agent
agent = DatabricksAgent(MCP_SERVER_URL, claude, CLAUDE_MODEL)

# Initialize (load tools)
await agent.initialize()

print("\n" + "="*80)
print("🤖 DATABRICKS AGENT READY")
print("="*80)
print("\nExamples:")
print("  • List my clusters")
print("  • Show SQL warehouses")
print("  • Run query: SELECT * FROM samples.nyctaxi.trips LIMIT 5")
print("  • What Unity Catalog tables exist?")
print("\n" + "="*80 + "\n")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Chat Interface

# COMMAND ----------

# Example: List clusters
query = "List all my Databricks clusters"
print(f"You: {query}\n")

response = await agent.chat(query)
print(f"\nAgent: {response}\n")

# COMMAND ----------

# Example: SQL query
query = "Run a SQL query to get 5 rows from samples.nyctaxi.trips"
print(f"You: {query}\n")

response = await agent.chat(query)
print(f"\nAgent: {response}\n")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Custom Query (Edit and Run!)

# COMMAND ----------

# Your query here
your_query = "Show me my SQL warehouses"

print(f"You: {your_query}\n")
response = await agent.chat(your_query)
print(f"\nAgent: {response}\n")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Summary
# MAGIC
# MAGIC ✅ **MCP Server**: Databricks App with 48 tools  
# MAGIC ✅ **LLM**: Claude Sonnet 4.5 (Databricks hosted)  
# MAGIC ✅ **Authentication**: Automatic (workspace OAuth)  
# MAGIC ✅ **Usage**: Natural language → tool calls → results
# MAGIC
# MAGIC **Next Steps**:
# MAGIC 1. Modify queries in cells above
# MAGIC 2. Create more complex workflows
# MAGIC 3. Share notebook with team
# MAGIC 4. Schedule as job for automation

