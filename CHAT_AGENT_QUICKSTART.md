# 🚀 Chat Agent Quickstart

Get started with the Databricks Chat Agent in 5 minutes!

## Prerequisites

1. **Python 3.8+** installed
2. **Anthropic API key** from [console.anthropic.com](https://console.anthropic.com/)
3. **Databricks workspace** credentials

## Step 1: Install Dependencies

```bash
cd databricks_cli_mcp
pip install anthropic
```

## Step 2: Set Environment Variables

```bash
# Anthropic API Key (required)
export ANTHROPIC_API_KEY='sk-ant-your-api-key-here'

# Databricks credentials (required)
export DATABRICKS_HOST='https://your-workspace.cloud.databricks.com'
export DATABRICKS_TOKEN='dapi-your-personal-access-token'
```

## Step 3: Start the MCP Server

In **Terminal 1**:

```bash
python server.py --port 8000
```

You should see:
```
✓ Connected to MCP server
Server running on http://0.0.0.0:8000/mcp
```

## Step 4: Run the Chat Agent

In **Terminal 2**:

```bash
python chat_agent.py
```

## Step 5: Start Chatting!

```
You: Show me all my clusters

Agent: I found 3 clusters in your workspace...
[detailed cluster information]

You: Start the ML cluster

Agent: Starting ml-cluster... Done!

You: Run a query to count rows in samples.nyctaxi.trips

Agent: [executes query and shows results]
```

## Example Conversations

### 📊 Data Exploration

```
You: What tables are in the main catalog?

Agent: Let me check... I found 23 tables across 3 schemas:
- default (15 tables)
- analytics (5 tables)
- ml (3 tables)

You: Show me the schema of customers table

Agent: [displays table schema with column names, types, and descriptions]
```

### 🔧 Cluster Management

```
You: Which clusters are running right now?

Agent: Currently 2 clusters are running:
1. ml-cluster (8 workers)
2. dev-cluster (2 workers)

You: Stop the dev cluster to save costs

Agent: Stopping dev-cluster... Done! The cluster is now stopped.
```

### 📝 Job Operations

```
You: Show me jobs that failed today

Agent: I found 2 failed jobs:
1. daily-etl (failed 4 hours ago)
   Error: OutOfMemoryError
2. data-quality-check (failed 1 hour ago)
   Error: Connection timeout

Would you like me to investigate the logs?

You: Check the logs for daily-etl

Agent: [retrieves and summarizes error logs]
```

### 🔄 Multi-Step Workflows

```
You: Create a new job to run my cleanup notebook daily at midnight

Agent: I'll create that job for you...
[creates job with schedule]
Done! Job ID: 789
- Name: cleanup-job
- Schedule: Daily at 00:00 UTC
- Notebook: /Workspace/cleanup.py

You: Run it now for testing

Agent: Starting test run... Job run ID: 12345
[waits for completion]
✓ Run completed successfully in 45 seconds!
```

## Quick Tips

1. **Be Specific**: "Start my ML cluster" is clearer than "start something"
2. **Ask Follow-ups**: The agent remembers context
3. **Use Natural Language**: No need for exact commands
4. **Combine Operations**: "Start cluster and run notebook" works!
5. **Ask for Help**: "What can you do?" shows capabilities

## Troubleshooting

### "ANTHROPIC_API_KEY not set"

```bash
export ANTHROPIC_API_KEY='sk-ant-...'
```

Get your key at: https://console.anthropic.com/

### "Cannot connect to MCP server"

Make sure the server is running:
```bash
# In another terminal
python server.py --port 8000
```

### "Missing Databricks credentials"

```bash
export DATABRICKS_HOST='https://your-workspace.cloud.databricks.com'
export DATABRICKS_TOKEN='dapi...'
```

Get PAT at: Databricks → Settings → Developer → Access Tokens

## One-Command Demo

Run the full demo with:

```bash
./demo_chat.sh
```

This script will:
1. Check prerequisites
2. Prompt for API keys if needed
3. Start the MCP server
4. Launch the chat agent
5. Clean up on exit

## Advanced Usage

### Custom System Prompt

Edit `chat_agent.py`:

```python
self.system_prompt = """You are a Databricks expert specializing in:
- Cost optimization
- Performance tuning
- Security best practices"""
```

### Different LLM Provider

Switch to GPT-4:

```python
from openai import OpenAI
llm_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
```

### Programmatic Usage

```python
from chat_agent import DatabricksAgent

agent = DatabricksAgent(mcp_client, llm_client)
response = await agent.chat("List all clusters")
print(response)
```

## What's Next?

- 📖 Read [CHAT_AGENT.md](./CHAT_AGENT.md) for detailed documentation
- 🔧 See [AGENT_IMPLEMENTATION.md](./AGENT_IMPLEMENTATION.md) for technical details
- 🚀 Deploy as Databricks App (see [DEPLOYMENT.md](./DEPLOYMENT.md))
- 🤝 Integrate with Slack/Teams for team access

## Cost Estimate

- **Anthropic Claude**: ~$0.01-0.05 per query
- **Databricks**: Standard workspace costs apply
- **Typical Usage**: $5-20/month for moderate use

## Support

- Issues: Check [README.md](./README.md) troubleshooting
- Examples: Run `python test_chat_agent.py`
- Docs: https://docs.databricks.com

---

🎉 **You're ready!** Start chatting with your Databricks workspace!

