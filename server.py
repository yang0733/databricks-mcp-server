"""Databricks CLI MCP Server with stateful context management."""

import sys
import argparse
from typing import Optional, Annotated
from fastmcp import FastMCP, Context
from databricks.sdk import WorkspaceClient

from auth import get_client_from_context, AuthenticationError
from databricks_client import (
    DatabricksClientWrapper,
    context_manager,
    SessionContext
)

# Import all tool modules
from tools import clusters, jobs, notebooks, workspace, repos, secrets, sql, unity_catalog


# Initialize FastMCP server
# Note: stateless_http is deprecated, will be set in run() call
mcp = FastMCP(
    name="DatabricksCLI",
)


def get_session_id(context) -> str:
    """Extract or generate session ID from context."""
    metadata = getattr(context, 'metadata', {}) or {}
    session_id = metadata.get('session-id') or metadata.get('x-session-id') or 'default'
    return session_id


def get_databricks_wrapper(context) -> DatabricksClientWrapper:
    """Get Databricks client wrapper with session context.
    
    Args:
        context: MCP context object
        
    Returns:
        DatabricksClientWrapper with authenticated client and session context
        
    Raises:
        AuthenticationError: If authentication fails
    """
    # Get authenticated client
    client = get_client_from_context(context)
    
    # Get or create session context
    session_id = get_session_id(context)
    session_context = context_manager.get_or_create_context(session_id)
    
    # Return wrapper
    return DatabricksClientWrapper(client, session_context)


# Register all tools from modules
clusters.register_tools(mcp, get_databricks_wrapper)
jobs.register_tools(mcp, get_databricks_wrapper)
notebooks.register_tools(mcp, get_databricks_wrapper)
workspace.register_tools(mcp, get_databricks_wrapper)
repos.register_tools(mcp, get_databricks_wrapper)
secrets.register_tools(mcp, get_databricks_wrapper)
sql.register_tools(mcp, get_databricks_wrapper)
unity_catalog.register_tools(mcp, get_databricks_wrapper)


# Context management tools
@mcp.tool()
def get_session_context(context: Annotated[Context, "MCP context"]) -> dict:
    """Get current session context including workspace path, cluster, job, and warehouse IDs.
    
    Returns a dictionary with the current session state that persists across tool calls.
    """
    session_id = get_session_id(context)
    session_context = context_manager.get_context(session_id)
    
    if session_context:
        return session_context.to_dict()
    else:
        return {
            "session_id": session_id,
            "message": "No context found for this session"
        }


@mcp.tool()
def set_workspace_path(path: str, context: Annotated[Context, "MCP context"]) -> str:
    """Set the current workspace path for subsequent operations.
    
    Args:
        path: Workspace path to set as current (e.g., /Workspace/Users/me)
        
    Returns:
        Confirmation message with the new path
    """
    session_id = get_session_id(context)
    session_context = context_manager.get_or_create_context(session_id)
    session_context.set_workspace_path(path)
    return f"Workspace path set to: {path}"


@mcp.tool()
def set_current_cluster(cluster_id: str, context: Annotated[Context, "MCP context"]) -> str:
    """Set the current cluster ID for subsequent operations.
    
    Args:
        cluster_id: Cluster ID to set as current
        
    Returns:
        Confirmation message
    """
    session_id = get_session_id(context)
    session_context = context_manager.get_or_create_context(session_id)
    session_context.set_cluster(cluster_id)
    return f"Current cluster set to: {cluster_id}"


@mcp.tool()
def set_current_warehouse(warehouse_id: str, context: Annotated[Context, "MCP context"]) -> str:
    """Set the current SQL warehouse ID for subsequent operations.
    
    Args:
        warehouse_id: Warehouse ID to set as current
        
    Returns:
        Confirmation message
    """
    session_id = get_session_id(context)
    session_context = context_manager.get_or_create_context(session_id)
    session_context.set_warehouse(warehouse_id)
    return f"Current warehouse set to: {warehouse_id}"


@mcp.tool()
def clear_session_context(context: Annotated[Context, "MCP context"]) -> str:
    """Clear the current session context and reset all stateful settings.
    
    Returns:
        Confirmation message
    """
    session_id = get_session_id(context)
    context_manager.clear_context(session_id)
    return f"Session context cleared for: {session_id}"


def main():
    """Main entry point for the server."""
    parser = argparse.ArgumentParser(description='Databricks CLI MCP Server')
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind to')
    parser.add_argument('--port', type=int, default=8000, help='Port to bind to')
    args = parser.parse_args()
    
    print(f"Starting Databricks CLI MCP Server on {args.host}:{args.port}")
    print("Server maintains session context across requests")
    print("Provide 'x-databricks-host' and 'x-databricks-token' headers for authentication")
    
    # Run server in HTTP mode
    # Use stateless mode so headers are sent with each request
    mcp.run(transport='http', host=args.host, port=args.port, stateless_http=True)


if __name__ == '__main__':
    main()


