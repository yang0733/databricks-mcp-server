# Chat Agent Implementation Guide

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                          USER INTERFACE                              │
│                   (Natural Language Input)                           │
└─────────────────────┬───────────────────────────────────────────────┘
                      │
                      │ "Show me all clusters"
                      │ "Run a query to get top 10 trips"
                      │ "What jobs failed today?"
                      ▼
┌─────────────────────────────────────────────────────────────────────┐
│                       CHAT AGENT                                     │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  1. Conversation Manager                                      │  │
│  │     - Maintains conversation history                          │  │
│  │     - Tracks context across turns                             │  │
│  │                                                                │  │
│  │  2. Intent Processor                                          │  │
│  │     - Parses user natural language                            │  │
│  │     - Maps to Databricks operations                           │  │
│  │                                                                │  │
│  │  3. Tool Orchestrator                                         │  │
│  │     - Selects appropriate MCP tools                           │  │
│  │     - Handles multi-step workflows                            │  │
│  │     - Manages tool parameters                                 │  │
│  │                                                                │  │
│  │  4. Response Formatter                                        │  │
│  │     - Converts technical output to natural language           │  │
│  │     - Formats tables, lists, and data                         │  │
│  └──────────────────────────────────────────────────────────────┘  │
└─────────────────────┬───────────────────────────────────────────────┘
                      │
                      │ Tool calls + parameters
                      ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    CLAUDE AI (LLM)                                   │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  • Model: Claude 3.5 Sonnet                                   │  │
│  │  • Capabilities:                                              │  │
│  │    - Natural language understanding                           │  │
│  │    - Function/tool calling                                    │  │
│  │    - Multi-step reasoning                                     │  │
│  │    - Context retention                                        │  │
│  │    - Code understanding                                       │  │
│  └──────────────────────────────────────────────────────────────┘  │
└─────────────────────┬───────────────────────────────────────────────┘
                      │
                      │ JSON-RPC requests
                      ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    MCP SERVER (FastMCP)                              │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  48 Tools across 8 categories:                                │  │
│  │                                                                │  │
│  │  • Clusters:  create, start, stop, delete, list, get          │  │
│  │  • Jobs:      create, run, cancel, list, get                  │  │
│  │  • SQL:       execute queries, manage warehouses              │  │
│  │  • Notebooks: import, export, run                             │  │
│  │  • Unity Cat: browse catalogs, schemas, tables                │  │
│  │  • Workspace: file operations, directory management           │  │
│  │  • Secrets:   manage scopes and secret values                 │  │
│  │  • Repos:     Git repository management                       │  │
│  │  • Context:   Session state management                        │  │
│  └──────────────────────────────────────────────────────────────┘  │
└─────────────────────┬───────────────────────────────────────────────┘
                      │
                      │ Databricks SDK calls
                      ▼
┌─────────────────────────────────────────────────────────────────────┐
│                   DATABRICKS WORKSPACE                               │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  • Clusters & Compute                                         │  │
│  │  • Jobs & Workflows                                           │  │
│  │  • SQL Warehouses                                             │  │
│  │  • Unity Catalog                                              │  │
│  │  • Notebooks & Files                                          │  │
│  │  • Git Repos                                                  │  │
│  │  • Secret Management                                          │  │
│  └──────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
```

## Component Details

### 1. Chat Agent (`chat_agent.py`)

**Responsibilities:**
- Manage conversation flow
- Integrate LLM for natural language understanding
- Execute MCP tools based on user intent
- Format responses in user-friendly way

**Key Classes:**

```python
class DatabricksAgent:
    def __init__(self, mcp_client: Client, llm_client: Anthropic)
    async def initialize()  # Load tools from MCP
    async def chat(user_message: str) -> str  # Main conversation loop
    async def execute_tool(tool_name, tool_input) -> str  # Tool execution
    def format_tools_for_llm() -> List[Dict]  # Convert MCP to LLM format
```

**Conversation Flow:**
1. User sends message
2. Agent adds to conversation history
3. LLM analyzes intent and selects tools
4. Agent executes tools via MCP
5. LLM formats results
6. Agent returns natural language response

### 2. LLM Integration

**Provider:** Anthropic Claude
- **Model:** `claude-3-5-sonnet-20241022`
- **Max Tokens:** 4096
- **Features Used:**
  - Tool calling (function calling)
  - Multi-turn conversations
  - Streaming responses (optional)

**Alternative Providers:**
- OpenAI GPT-4 Turbo
- Local models (Ollama, LLaMA)
- Azure OpenAI
- Google Gemini

### 3. Tool Calling Mechanism

**Format Conversion:**

MCP Tool Format:
```json
{
  "name": "list_clusters",
  "description": "List all clusters in the workspace",
  "inputSchema": {
    "type": "object",
    "properties": {
      "filter_by_state": {
        "type": "string",
        "description": "Filter clusters by state"
      }
    }
  }
}
```

Anthropic Tool Format:
```json
{
  "name": "list_clusters",
  "description": "List all clusters in the workspace",
  "input_schema": {
    "type": "object",
    "properties": {
      "filter_by_state": {
        "type": "string",
        "description": "Filter clusters by state"
      }
    },
    "required": []
  }
}
```

**Execution Flow:**
```
User: "Show me running clusters"
  ↓
LLM: { tool: "list_clusters", params: { filter_by_state: "RUNNING" } }
  ↓
MCP: [executes via Databricks SDK]
  ↓
Result: [list of clusters]
  ↓
LLM: "I found 3 running clusters: cluster-1, cluster-2, cluster-3..."
```

### 4. Multi-Step Workflows

The agent can handle complex multi-step operations:

**Example: "Train a new model"**
```
User: "Train a new model on the latest data"

Step 1: LLM calls list_clusters to find ML cluster
Step 2: LLM calls start_cluster if needed
Step 3: LLM calls list_notebooks to find training notebook
Step 4: LLM calls run_notebook with cluster_id
Step 5: LLM formats progress and results

Agent: "I started your ml-cluster and launched the training notebook.
        The model training is now running. Job ID: 12345"
```

## Implementation Details

### Session Management

```python
# Each conversation gets a unique session ID
headers = {
    "x-session-id": f"chat-agent-{timestamp}",
    "x-databricks-host": DATABRICKS_HOST,
    "x-databricks-token": DATABRICKS_TOKEN,
}

# Session state maintained by MCP server
# - workspace_path
# - current_cluster_id
# - current_warehouse_id
```

### Error Handling

```python
async def execute_tool(self, tool_name: str, tool_input: Dict) -> str:
    try:
        result = await self.mcp.call_tool(tool_name, tool_input)
        return self.format_result(result)
    except Exception as e:
        # Return error to LLM for natural language explanation
        return f"Error executing {tool_name}: {str(e)}"
```

### Result Formatting

```python
def extract_result(self, result) -> str:
    # Handle different MCP result formats
    if isinstance(result, list):
        return result[0].content[0].text
    elif hasattr(result, 'content'):
        return result.content[0].text
    else:
        return str(result)
    
    # Try to format as JSON for readability
    try:
        result_json = json.loads(result_text)
        return json.dumps(result_json, indent=2)
    except:
        return result_text
```

## Advanced Features

### 1. Context Awareness

The agent maintains context across the conversation:

```
User: "Start my ML cluster"
Agent: "Starting ml-cluster-1... Done!"

User: "Now run the training notebook on it"
Agent: "Running notebook on ml-cluster-1..." # Remembers cluster from context
```

### 2. Proactive Suggestions

```python
system_prompt = """When users ask about operations, proactively suggest:
- Resource optimization opportunities
- Cost-saving measures
- Best practices
- Related operations they might want"""
```

### 3. Error Recovery

```
User: "Run query on warehouse-prod"
Agent: "warehouse-prod is stopped. Would you like me to start it first?"

User: "Yes"
Agent: "Starting warehouse-prod... [waits] Running your query..."
```

### 4. Batch Operations

```
User: "Stop all idle clusters"
Agent: [Calls list_clusters, identifies idle ones, confirms with user, stops them]
```

## Deployment Options

### Option 1: Local Development
```bash
python chat_agent.py
```
- Best for: Individual development, testing
- Cost: Anthropic API costs only

### Option 2: Web Application
```python
# Wrap with FastAPI or Streamlit
import streamlit as st

if st.button("Send"):
    response = await agent.chat(user_input)
    st.write(response)
```
- Best for: Team collaboration, demos
- Cost: Anthropic API + hosting

### Option 3: Slack Bot
```python
from slack_bolt.async_app import AsyncApp

@app.message()
async def handle_message(message, say):
    response = await agent.chat(message['text'])
    await say(response)
```
- Best for: Team-wide access, workflow integration
- Cost: Anthropic API + Slack app hosting

### Option 4: Databricks App
```yaml
# databricks.yml
command:
  - "python"
  - "chat_agent_server.py"
  - "--port=8080"
```
- Best for: Enterprise deployment, compliance
- Cost: Databricks compute + Anthropic API

## Performance Optimization

### Token Efficiency
```python
# Limit tools passed to LLM (reduce context size)
tools=self.format_tools_for_llm()[:20]  # First 20 tools only

# Cache conversation history
if len(self.conversation_history) > 20:
    # Keep only recent messages + initial context
    self.conversation_history = [
        self.conversation_history[0],  # System prompt
        *self.conversation_history[-19:]  # Last 19 messages
    ]
```

### Response Latency
```python
# Stream responses for better UX
response = self.llm.messages.stream(
    model="claude-3-5-sonnet-20241022",
    messages=self.conversation_history,
    tools=self.format_tools_for_llm()
)

for chunk in response:
    print(chunk.content, end='', flush=True)
```

### Cost Management
```python
# Use cheaper models for simple queries
def select_model(query_complexity: str):
    if query_complexity == "simple":
        return "claude-3-haiku-20240307"  # Cheaper
    else:
        return "claude-3-5-sonnet-20241022"  # More capable
```

## Testing Strategy

### Unit Tests
```python
async def test_tool_execution():
    result = await agent.execute_tool("list_clusters", {})
    assert "clusters" in result
```

### Integration Tests
```python
async def test_conversation_flow():
    response1 = await agent.chat("Show my clusters")
    assert "cluster" in response1.lower()
    
    response2 = await agent.chat("Start the first one")
    assert "starting" in response2.lower()
```

### End-to-End Tests
```python
async def test_multi_step_workflow():
    responses = []
    
    responses.append(await agent.chat("Create a job to run daily ETL"))
    responses.append(await agent.chat("Schedule it for 2am"))
    responses.append(await agent.chat("Trigger it now for testing"))
    
    assert all(r for r in responses)
```

## Security Considerations

1. **API Key Management**
   - Store in environment variables
   - Use secret management services
   - Rotate regularly

2. **Databricks Access**
   - Use least-privilege PATs
   - Audit tool usage
   - Log all operations

3. **User Authentication**
   - Require user login
   - Map users to Databricks identities
   - Track who executes what

4. **Input Validation**
   - Sanitize user input
   - Validate tool parameters
   - Prevent injection attacks

## Monitoring & Observability

```python
import logging

logger = logging.getLogger("databricks_agent")

# Log all conversations
logger.info(f"User: {user_message}")
logger.info(f"Tools called: {[t.name for t in tool_calls]}")
logger.info(f"Response: {response[:100]}...")

# Track metrics
metrics.increment("conversations.total")
metrics.timing("llm.response_time", elapsed)
metrics.increment(f"tools.{tool_name}.calls")
```

## Future Enhancements

1. **Voice Interface**: Add speech-to-text/text-to-speech
2. **Visual Output**: Generate charts and graphs
3. **Workflow Builder**: Convert conversations to reusable workflows
4. **Learning**: Remember user preferences and patterns
5. **Collaboration**: Multi-user conversations
6. **Automation**: Schedule recurring operations via chat

## Resources

- **MCP Documentation**: https://gofastmcp.com
- **Anthropic Claude**: https://docs.anthropic.com
- **Databricks SDK**: https://docs.databricks.com/sdk
- **Example Code**: `chat_agent.py`, `test_chat_agent.py`
- **User Guide**: `CHAT_AGENT.md`

