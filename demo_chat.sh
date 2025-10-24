#!/bin/bash
# Demo script for the Databricks Chat Agent

set -e

echo "============================================"
echo "   Databricks Chat Agent Demo"
echo "============================================"
echo

# Check prerequisites
echo "Checking prerequisites..."
echo

# Check Python
if ! command -v python &> /dev/null; then
    echo "❌ Python not found. Please install Python 3.8+"
    exit 1
fi
echo "✓ Python: $(python --version)"

# Check if anthropic is installed
if ! python -c "import anthropic" 2>/dev/null; then
    echo "⚠️  anthropic package not installed"
    echo
    read -p "Install anthropic? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        pip install anthropic
    else
        echo "❌ anthropic is required. Install with: pip install anthropic"
        exit 1
    fi
fi
echo "✓ anthropic package installed"

# Check environment variables
echo
echo "Checking configuration..."
echo

if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo "⚠️  ANTHROPIC_API_KEY not set"
    echo
    read -p "Enter your Anthropic API key: " api_key
    export ANTHROPIC_API_KEY="$api_key"
fi
echo "✓ ANTHROPIC_API_KEY configured"

if [ -z "$DATABRICKS_HOST" ]; then
    echo "⚠️  DATABRICKS_HOST not set"
    echo
    read -p "Enter your Databricks workspace URL: " db_host
    export DATABRICKS_HOST="$db_host"
fi
echo "✓ DATABRICKS_HOST: $DATABRICKS_HOST"

if [ -z "$DATABRICKS_TOKEN" ]; then
    echo "⚠️  DATABRICKS_TOKEN not set"
    echo
    read -s -p "Enter your Databricks personal access token: " db_token
    export DATABRICKS_TOKEN="$db_token"
    echo
fi
echo "✓ DATABRICKS_TOKEN configured"

# Check if server is running
echo
echo "Checking MCP server..."
if ! curl -s http://localhost:8000/mcp/ > /dev/null 2>&1; then
    echo "⚠️  MCP server not running on localhost:8000"
    echo
    echo "Starting MCP server..."
    python server.py --port 8000 > /tmp/mcp_server.log 2>&1 &
    SERVER_PID=$!
    echo "✓ Server started (PID: $SERVER_PID)"
    echo "  Logs: /tmp/mcp_server.log"
    echo
    echo "Waiting for server to start..."
    sleep 3
else
    echo "✓ MCP server is running"
    SERVER_PID=""
fi

echo
echo "============================================"
echo "   Starting Chat Agent..."
echo "============================================"
echo

# Run the chat agent
python chat_agent.py

# Cleanup
if [ -n "$SERVER_PID" ]; then
    echo
    echo "Stopping MCP server (PID: $SERVER_PID)..."
    kill $SERVER_PID 2>/dev/null || true
    echo "✓ Server stopped"
fi

echo
echo "============================================"
echo "   Demo Complete!"
echo "============================================"

