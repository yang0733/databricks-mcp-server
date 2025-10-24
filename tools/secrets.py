"""Secrets management tools for Databricks."""

from typing import Optional


def register_tools(mcp, get_wrapper):
    """Register secrets management tools with the MCP server."""
    
    @mcp.tool()
    def list_secret_scopes(context=None) -> dict:
        """List all secret scopes in the workspace.
        
        Returns:
            Dictionary with list of secret scopes
        """
        wrapper = get_wrapper(context)
        
        scopes = wrapper.client.secrets.list_scopes()
        
        scope_list = []
        for scope in scopes:
            scope_list.append({
                "name": scope.name,
                "backend_type": scope.backend_type.value if scope.backend_type else None,
            })
        
        return {
            "scopes": scope_list,
            "count": len(scope_list)
        }
    
    @mcp.tool()
    def create_secret_scope(
        scope: str,
        initial_manage_principal: Optional[str] = None,
        context=None
    ) -> dict:
        """Create a new secret scope.
        
        Args:
            scope: Name for the secret scope
            initial_manage_principal: Optional principal to grant MANAGE permission
            
        Returns:
            Dictionary with creation status
        """
        wrapper = get_wrapper(context)
        
        scope_config = {"scope": scope}
        if initial_manage_principal:
            scope_config["initial_manage_principal"] = initial_manage_principal
        
        wrapper.client.secrets.create_scope(**scope_config)
        
        return {
            "scope": scope,
            "status": "created",
            "message": f"Secret scope '{scope}' has been created"
        }
    
    @mcp.tool()
    def list_secrets(
        scope: str,
        context=None
    ) -> dict:
        """List secrets in a scope (names only, values are never returned).
        
        Args:
            scope: Secret scope name
            
        Returns:
            Dictionary with list of secret names
        """
        wrapper = get_wrapper(context)
        
        secrets = wrapper.client.secrets.list_secrets(scope)
        
        secret_list = []
        for secret in secrets:
            secret_list.append({
                "key": secret.key,
                "last_updated_timestamp": secret.last_updated_timestamp,
            })
        
        return {
            "scope": scope,
            "secrets": secret_list,
            "count": len(secret_list),
            "message": "Secret values are never returned for security reasons"
        }
    
    @mcp.tool()
    def put_secret(
        scope: str,
        key: str,
        string_value: str,
        context=None
    ) -> dict:
        """Store a secret value.
        
        Args:
            scope: Secret scope name
            key: Secret key name
            string_value: Secret value to store
            
        Returns:
            Dictionary with storage status
        """
        wrapper = get_wrapper(context)
        
        wrapper.client.secrets.put_secret(
            scope=scope,
            key=key,
            string_value=string_value
        )
        
        return {
            "scope": scope,
            "key": key,
            "status": "stored",
            "message": f"Secret '{key}' has been stored in scope '{scope}'"
        }
    
    @mcp.tool()
    def delete_secret(
        scope: str,
        key: str,
        context=None
    ) -> dict:
        """Delete a secret.
        
        Args:
            scope: Secret scope name
            key: Secret key name
            
        Returns:
            Dictionary with deletion status
        """
        wrapper = get_wrapper(context)
        
        wrapper.client.secrets.delete_secret(
            scope=scope,
            key=key
        )
        
        return {
            "scope": scope,
            "key": key,
            "status": "deleted",
            "message": f"Secret '{key}' has been deleted from scope '{scope}'"
        }

