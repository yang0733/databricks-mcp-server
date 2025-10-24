#!/usr/bin/env python3
"""
Local MCP Server for Cursor - Uses Databricks PAT for authentication.

This runs the MCP server locally on your Mac, authenticating with your
Databricks Personal Access Token. No OAuth required!

Usage:
    export DATABRICKS_HOST="https://your-workspace.cloud.databricks.com"
    export DATABRICKS_TOKEN="dapi..."
    python local_mcp_server.py
    
Then add to Cursor settings:
    MCP Server URL: http://localhost:8080
"""

import os
import sys

# Configuration from environment
DATABRICKS_HOST = os.getenv("DATABRICKS_HOST", "https://your-workspace.cloud.databricks.com")
DATABRICKS_TOKEN = os.getenv("DATABRICKS_TOKEN", "dapi1234567890abcdef1234567890abcdef")
PORT = int(os.getenv("PORT", "8080"))

# Set environment variables for the server
os.environ["DATABRICKS_HOST"] = DATABRICKS_HOST
os.environ["DATABRICKS_TOKEN"] = DATABRICKS_TOKEN

# Import our existing server
from server import mcp

if __name__ == "__main__":
    print("=" * 80)
    print("🚀 Databricks MCP Server (Local - PAT Auth)")
    print("=" * 80)
    print(f"Port: {PORT}")
    print(f"MCP Endpoint: http://localhost:{PORT}")
    print(f"Databricks Host: {DATABRICKS_HOST}")
    print(f"Token: {'✅ Configured' if DATABRICKS_TOKEN else '❌ Missing'}")
    print("=" * 80)
    print()
    print("Add to Cursor settings:")
    print()
    print('{')
    print('  "mcp": {')
    print('    "servers": {')
    print('      "databricks": {')
    print(f'        "url": "http://localhost:{PORT}"')
    print('      }')
    print('    }')
    print('  }')
    print('}')
    print()
    print("=" * 80)
    print()
    
    # Run FastMCP's streamable-http server directly
    mcp.run(transport='streamable-http', host='0.0.0.0', port=PORT)
