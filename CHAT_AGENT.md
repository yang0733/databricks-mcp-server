# Databricks Chat Agent

An interactive natural language interface to your Databricks workspace powered by Claude (or other LLMs).

## Features

- 🗣️ **Natural Language**: Chat with your Databricks workspace in plain English
- 🔧 **48+ Tools**: Access all Databricks operations (clusters, jobs, notebooks, SQL, Unity Catalog, etc.)
- 🧠 **Smart Understanding**: Claude automatically selects the right tools based on your request
- 💬 **Conversational**: Maintains context across the conversation
- 🎯 **Accurate Results**: Direct integration with Databricks via MCP server

## Quick Start

### 1. Prerequisites

```bash
# Install the anthropic package
pip install anthropic

# Or install all requirements
pip install -r requirements.txt
```

### 2. Set Your API Key

Get your Anthropic API key from [https://console.anthropic.com/](https://console.anthropic.com/)

```bash
export ANTHROPIC_API_KEY='sk-ant-...'
```

### 3. Start the MCP Server

In one terminal:

```bash
cd databricks_cli_mcp
export DATABRICKS_HOST="https://your-workspace.cloud.databricks.com"
export DATABRICKS_TOKEN="your-personal-access-token"
python server.py --port 8000
```

### 4. Run the Chat Agent

In another terminal:

```bash
cd databricks_cli_mcp
export ANTHROPIC_API_KEY='sk-ant-...'
export DATABRICKS_HOST="https://your-workspace.cloud.databricks.com"
export DATABRICKS_TOKEN="your-personal-access-token"
python chat_agent.py
```

## Example Conversations

### Example 1: Exploring Clusters

```
You: Show me all my clusters

🔧 Executing: list_clusters

Agent: I found 3 clusters in your workspace:

1. **interactive-cluster-1** (RUNNING)
   - Type: All-purpose
   - Spark: 13.3.x-scala2.12
   - Workers: 2-8 nodes

2. **job-cluster-prod** (TERMINATED)
   - Type: Job cluster
   - Last used: 2 hours ago

3. **ml-training** (PENDING)
   - Starting up...

Would you like me to start any of these clusters?
```

### Example 2: Running SQL Queries

```
You: Run a query to get the top 5 NYC taxi trips by fare amount

🔧 Executing: list_warehouses
🔧 Executing: execute_query

Agent: I found an active warehouse and ran your query. Here are the top 5 trips by fare:

| Pickup Time       | Fare Amount | Distance | Tip    |
|-------------------|-------------|----------|--------|
| 2023-01-15 08:30  | $875.50    | 28.3 mi  | $175  |
| 2023-01-10 14:22  | $624.25    | 22.1 mi  | $125  |
| 2023-01-08 19:45  | $598.00    | 31.5 mi  | $120  |
| 2023-01-20 11:15  | $550.75    | 19.8 mi  | $110  |
| 2023-01-12 16:30  | $485.50    | 25.2 mi  | $95   |

These were all airport runs with premium service!
```

### Example 3: Managing Jobs

```
You: What jobs do I have and when did they last run?

🔧 Executing: list_jobs

Agent: You have 8 jobs configured:

**Recently Run:**
1. daily-etl-pipeline - Last run: 2 hours ago (SUCCESS)
2. model-training - Last run: 6 hours ago (SUCCESS)
3. data-quality-checks - Last run: 1 hour ago (SUCCESS)

**Not Run Today:**
4. weekly-report - Last run: 3 days ago
5. monthly-aggregation - Last run: 15 days ago

**Failed:**
6. streaming-job - Last run: 4 hours ago (FAILED)
   Error: OutOfMemoryError

Would you like me to check the logs for the failed job?
```

### Example 4: Unity Catalog Exploration

```
You: What tables are available in the main catalog?

🔧 Executing: list_schemas
🔧 Executing: list_tables

Agent: I found these tables in the main catalog:

**default schema (15 tables):**
- customers (2.3M rows)
- orders (8.1M rows)
- products (1,200 rows)
...

**analytics schema (8 tables):**
- daily_metrics (365 rows)
- user_cohorts (1.5M rows)
...

**ml schema (5 tables):**
- features (3.2M rows)
- predictions (1.1M rows)
...

Would you like to see the schema for any specific table?
```

## How It Works

```
┌─────────┐       Natural Language       ┌──────────┐
│  User   │ ──────────────────────────> │  Chat    │
│         │                              │  Agent   │
└─────────┘                              └────┬─────┘
                                              │
                                              │ 1. Understands intent
                                              │ 2. Selects tools
                                              │ 3. Executes via MCP
                                              ▼
                                         ┌─────────────┐
                                         │  Claude AI  │
                                         │  (LLM)      │
                                         └─────┬───────┘
                                               │
                                               │ Tool Calls
                                               ▼
                                         ┌─────────────┐
                                         │ MCP Server  │
                                         │ (48+ tools) │
                                         └─────┬───────┘
                                               │
                                               │ SDK Calls
                                               ▼
                                         ┌─────────────┐
                                         │ Databricks  │
                                         │  Workspace  │
                                         └─────────────┘
```

## Configuration

### Environment Variables

```bash
# Required
export ANTHROPIC_API_KEY='sk-ant-...'
export DATABRICKS_HOST='https://your-workspace.cloud.databricks.com'
export DATABRICKS_TOKEN='dapi...'

# Optional
export SERVER_URL='http://localhost:8000/mcp/'  # MCP server URL
```

### Using Different LLM Providers

The chat agent uses Claude by default, but you can modify it to use:

- **OpenAI GPT-4**: Replace Anthropic client with OpenAI client
- **Local LLMs**: Use Ollama or similar for on-premises deployments
- **Other Providers**: Any LLM with function/tool calling support

Example for OpenAI:

```python
from openai import OpenAI

llm_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

response = llm_client.chat.completions.create(
    model="gpt-4-turbo",
    messages=self.conversation_history,
    tools=self.format_tools_for_llm(),
)
```

## Advanced Usage

### Custom System Prompts

Modify the `system_prompt` in `chat_agent.py` to customize the agent's behavior:

```python
self.system_prompt = """You are a senior data engineer specializing in Databricks.
You help teams optimize their data pipelines and resolve production issues.

Focus on:
- Performance optimization
- Cost efficiency
- Best practices
- Proactive monitoring"""
```

### Integration with CI/CD

Use the chat agent programmatically:

```python
from chat_agent import DatabricksAgent

async def automated_check():
    agent = DatabricksAgent(mcp_client, llm_client)
    await agent.initialize()
    
    # Check system health
    response = await agent.chat("Check if any jobs failed in the last hour")
    
    # Parse response and alert if needed
    if "FAILED" in response:
        send_slack_alert(response)
```

### Multi-Step Workflows

The agent maintains context, so you can have multi-step conversations:

```
You: Create a new cluster for machine learning
Agent: I'll create a cluster with ML runtime... [creates cluster]

You: Now import the training notebook from my repo
Agent: Which repo should I use?

You: The ml-experiments repo
Agent: Got it, importing from ml-experiments... [imports notebook]

You: Run it on the cluster we just created
Agent: Starting notebook execution... [runs notebook]
```

## Tips for Best Results

1. **Be Specific**: "List jobs that failed today" is better than "show me jobs"
2. **Ask Follow-ups**: The agent remembers context - use it!
3. **Request Clarifications**: The agent will ask if it needs more info
4. **Use Natural Language**: No need to memorize commands or syntax
5. **Combine Operations**: "Start my ML cluster and run the training notebook"

## Troubleshooting

### API Key Issues

```
❌ Error: ANTHROPIC_API_KEY environment variable not set
```

**Solution**: Set your API key:
```bash
export ANTHROPIC_API_KEY='sk-ant-...'
```

### MCP Connection Issues

```
❌ Error: Cannot connect to MCP server
```

**Solution**: Ensure the server is running:
```bash
python server.py --port 8000
```

### Databricks Authentication

```
❌ Error: Missing Databricks credentials
```

**Solution**: Set credentials:
```bash
export DATABRICKS_HOST='https://your-workspace.cloud.databricks.com'
export DATABRICKS_TOKEN='dapi...'
```

## Cost Considerations

- **Anthropic Pricing**: ~$0.01 per query (varies with complexity)
- **Token Usage**: The agent uses Claude 3.5 Sonnet for optimal balance
- **Optimization**: Tool results are truncated to reduce token costs

For high-volume usage, consider:
- Caching frequently accessed data
- Using Claude Haiku for simpler queries
- Implementing rate limiting

## Deployment Options

### Option 1: Local Development

Run the agent on your laptop for development and testing.

### Option 2: Team Server

Deploy the agent on a shared server for team access:

```bash
# On server
nohup python chat_agent.py --host 0.0.0.0 --port 8080 &
```

### Option 3: Databricks App

Package the chat agent as a Databricks App for integrated deployment.

### Option 4: Slack Bot

Wrap the agent with Slack integration for team-wide access:

```python
from slack_bolt import App

@app.message()
async def handle_message(message, say):
    response = await agent.chat(message['text'])
    await say(response)
```

## Next Steps

- ✅ Try example conversations
- 🔧 Customize the system prompt for your use case
- 🚀 Integrate with your workflow automation
- 📊 Build dashboards using the agent's capabilities
- 🤝 Share with your team

## Support

- **Documentation**: [Main README](./README.md)
- **Issues**: Report bugs or request features on GitHub
- **Databricks Docs**: [docs.databricks.com](https://docs.databricks.com)
- **Anthropic Docs**: [docs.anthropic.com](https://docs.anthropic.com)

