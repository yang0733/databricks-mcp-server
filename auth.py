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
    # Try to get from context metadata/headers
    metadata = getattr(context, 'metadata', {}) or {}
    
    # Check for custom headers
    host = metadata.get('x-databricks-host')
    token = metadata.get('x-databricks-token')
    
    # Also check standard authorization header formats
    if not host:
        host = metadata.get('databricks-host')
    if not token:
        token = metadata.get('databricks-token')
        
    if not host or not token:
        raise AuthenticationError(
            "Missing Databricks credentials. Please provide 'x-databricks-host' "
            "and 'x-databricks-token' headers."
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


