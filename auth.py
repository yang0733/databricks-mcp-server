"""Authentication handler for Databricks MCP Server."""

from typing import Optional
from databricks.sdk import WorkspaceClient
from databricks.sdk.core import Config


class AuthenticationError(Exception):
    """Raised when authentication fails."""
    pass


def extract_auth_from_context(context) -> tuple[str, str]:
    """Extract Databricks host and token from MCP context.
    
    Args:
        context: MCP context object containing request metadata
        
    Returns:
        Tuple of (host, token)
        
    Raises:
        AuthenticationError: If required credentials are missing
    """
    import os
    
    # TEMPORARY WORKAROUND: Check environment variables first for local testing
    env_host = os.getenv('DATABRICKS_HOST')
    env_token = os.getenv('DATABRICKS_TOKEN')
    
    if env_host and env_token:
        # Use environment variables if set
        if not env_host.startswith('http'):
            env_host = f'https://{env_host}'
        return env_host, env_token
    
    # Try to get from context metadata/headers
    # FastMCP Context object may have metadata, meta, or direct header access
    metadata = {}
    
    # Try different ways to access metadata
    if hasattr(context, 'meta'):
        metadata = context.meta or {}
        print(f"DEBUG: Got meta: {metadata}", file=sys.stderr)
    elif hasattr(context, 'metadata'):
        metadata = context.metadata or {}
        print(f"DEBUG: Got metadata: {metadata}", file=sys.stderr)
    elif hasattr(context, 'request_context'):
        metadata = getattr(context.request_context, 'meta', {}) or {}
        print(f"DEBUG: Got request_context.meta: {metadata}", file=sys.stderr)
    
    # Also try to get headers directly from request if available
    if hasattr(context, 'request'):
        headers = getattr(context.request, 'headers', {}) or {}
        print(f"DEBUG: Got request.headers: {headers}", file=sys.stderr)
        metadata.update(headers)
    
    # Check for custom headers (case-insensitive)
    metadata_lower = {k.lower(): v for k, v in metadata.items()}
    
    host = (metadata_lower.get('x-databricks-host') or 
            metadata_lower.get('databricks-host') or
            metadata.get('x-databricks-host') or
            metadata.get('databricks-host'))
    
    token = (metadata_lower.get('x-databricks-token') or 
             metadata_lower.get('databricks-token') or
             metadata.get('x-databricks-token') or
             metadata.get('databricks-token'))
        
    if not host or not token:
        # Debug: print what we got
        import json
        available_keys = list(metadata.keys())
        raise AuthenticationError(
            f"Missing Databricks credentials. Please provide 'x-databricks-host' "
            f"and 'x-databricks-token' headers. Available keys: {available_keys}"
        )
    
    # Ensure host has proper format
    if not host.startswith('http'):
        host = f'https://{host}'
        
    return host, token


def create_client(host: str, token: str) -> WorkspaceClient:
    """Create a Databricks WorkspaceClient with provided credentials.
    
    Args:
        host: Databricks workspace URL (e.g., https://my-workspace.cloud.databricks.com)
        token: Personal access token
        
    Returns:
        Configured WorkspaceClient instance
    """
    config = Config(
        host=host,
        token=token
    )
    return WorkspaceClient(config=config)


def get_client_from_context(context) -> WorkspaceClient:
    """Get authenticated Databricks client from MCP context.
    
    Args:
        context: MCP context object
        
    Returns:
        Configured WorkspaceClient instance
        
    Raises:
        AuthenticationError: If authentication fails
    """
    host, token = extract_auth_from_context(context)
    return create_client(host, token)


