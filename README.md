# Databricks MCP Server

A comprehensive MCP (Model Context Protocol) server for Databricks CLI with 48 tools + Natural language chat agent powered by Claude Sonnet 4.5.

## 🎯 Features

- **48 Databricks Tools**: Clusters, Jobs, Notebooks, SQL, Unity Catalog, Repos, Secrets, Workspace
- **Stateful Sessions**: Maintains context across requests
- **Chat Agent**: Natural language interface using Claude Sonnet 4.5
- **3 LLM Options**: Databricks Claude, Claude API, or Local Ollama
- **Production Ready**: Deployable as Databricks App

## 🚀 Quick Start

### Deploy to Databricks Apps

```bash
# 1. Clone this repo
git clone https://github.com/yang0733/databricks-mcp-server.git
cd databricks-mcp-server

# 2. Link to Databricks
databricks repos create \
  --url https://github.com/yang0733/databricks-mcp-server \
  --provider github \
  --path /Repos/YOUR_EMAIL/databricks-mcp-server

# 3. Deploy
databricks apps deploy databricks-mcp-server \
  --source-code-path /Repos/YOUR_EMAIL/databricks-mcp-server \
  --mode AUTO_SYNC
```

### Run Locally

```bash
# Install dependencies
pip install -r requirements.txt

# Start MCP server
python server.py --port 8000

# Run chat agent (local LLM - free!)
python chat_agent_ollama.py
```

## 💬 Chat Agent Examples

```
You: Show me all my clusters
Agent: I found 3 clusters in your workspace...

You: Run a SQL query to get 5 rows from samples.nyctaxi.trips
Agent: [executes query and shows results]

You: List my recent jobs
Agent: You have 8 jobs configured...
```

## 🔧 Available Tools (48)

- **Clusters** (7): create, start, stop, delete, list, get, set_current
- **Jobs** (7): create, run, cancel, delete, list, get, get_run
- **SQL** (5): warehouses, queries, results
- **Notebooks** (4): import, export, list, run
- **Unity Catalog** (6): catalogs, schemas, tables, volumes
- **Workspace** (5): list, import, export, delete, mkdirs
- **Git Repos** (5): create, update, delete, list, get
- **Secrets** (5): scopes, secrets management
- **Context** (3): session state management

## 📖 Documentation

- [Complete Documentation](./README.md)
- [Chat Agent Guide](./CHAT_AGENT.md)
- [Ollama Setup](./OLLAMA_SETUP.md)
- [Databricks Apps Deployment](./DATABRICKS_APPS_DEPLOYMENT.md)

## 🎓 Architecture

```
User → Chat Agent (Claude) → MCP Server (48 tools) → Databricks API
```

## 🔐 Configuration

Set environment variables:
```bash
export DATABRICKS_HOST='https://your-workspace.cloud.databricks.com'
export DATABRICKS_TOKEN='dapi...'
export ANTHROPIC_API_KEY='sk-ant-...'  # For Claude API
```

## 📊 Tech Stack

- **FastMCP**: MCP server framework
- **Databricks SDK**: Python SDK for Databricks
- **Claude Sonnet 4.5**: LLM via Databricks Model Serving
- **Ollama**: Local LLM option (free)

## 🤝 Contributing

Contributions welcome! This project provides a complete reference implementation for:
- MCP server development
- Databricks CLI automation
- LLM-powered chat agents
- Databricks Apps deployment

## 📝 License

MIT

## 👤 Author

Cliff Yang ([@yang0733](https://github.com/yang0733))

---

**Built with**: FastMCP • Databricks SDK • Claude AI • Ollama

