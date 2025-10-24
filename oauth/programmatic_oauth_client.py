"""
Programmatic OAuth M2M client for Databricks MCP Server.

This client uses OAuth 2.0 Machine-to-Machine (M2M) authentication
with a service principal to access the deployed Databricks App
without any browser-based authentication.
"""

import os
import requests
from typing import Optional
from datetime import datetime, timedelta
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import httpx
import json
import asyncio


class DatabricksOAuthClient:
    """Handles OAuth M2M authentication for Databricks Apps."""
    
    def __init__(
        self,
        workspace_url: str,
        client_id: str,
        client_secret: str,
        token_cache_file: Optional[str] = None
    ):
        """
        Initialize OAuth client.
        
        Args:
            workspace_url: Databricks workspace URL (e.g., https://your-workspace.cloud.databricks.com)
            client_id: Service principal application ID (UUID)
            client_secret: OAuth client secret
            token_cache_file: Optional file to cache tokens (default: ~/.databricks_oauth_token)
        """
        self.workspace_url = workspace_url.rstrip('/')
        self.client_id = client_id
        self.client_secret = client_secret
        self.token_cache_file = token_cache_file or os.path.expanduser("~/.databricks_oauth_token")
        
        self._access_token: Optional[str] = None
        self._token_expiry: Optional[datetime] = None
    
    def get_token_endpoint(self) -> str:
        """Get the OAuth token endpoint."""
        return f"{self.workspace_url}/oidc/v1/token"
    
    def _load_cached_token(self) -> bool:
        """Load token from cache file if valid."""
        if not os.path.exists(self.token_cache_file):
            return False
        
        try:
            with open(self.token_cache_file, 'r') as f:
                data = json.load(f)
            
            expiry = datetime.fromisoformat(data['expiry'])
            if expiry > datetime.now() + timedelta(minutes=5):  # 5 min buffer
                self._access_token = data['access_token']
                self._token_expiry = expiry
                return True
        except Exception:
            pass
        
        return False
    
    def _save_token_to_cache(self):
        """Save token to cache file."""
        if not self._access_token or not self._token_expiry:
            return
        
        try:
            os.makedirs(os.path.dirname(self.token_cache_file), exist_ok=True)
            with open(self.token_cache_file, 'w') as f:
                json.dump({
                    'access_token': self._access_token,
                    'expiry': self._token_expiry.isoformat()
                }, f)
            os.chmod(self.token_cache_file, 0o600)  # Secure permissions
        except Exception as e:
            print(f"Warning: Could not cache token: {e}")
    
    def get_access_token(self) -> str:
        """
        Get a valid OAuth access token.
        
        Returns:
            Access token string
            
        Raises:
            Exception: If token acquisition fails
        """
        # Check cache first
        if self._load_cached_token():
            print("✅ Using cached OAuth token")
            return self._access_token
        
        # Request new token using client credentials flow
        print("🔐 Requesting new OAuth token via M2M flow...")
        
        token_url = self.get_token_endpoint()
        
        response = requests.post(
            token_url,
            data={
                'grant_type': 'client_credentials',
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'scope': 'all-apis'  # Request access to all APIs
            },
            headers={'Content-Type': 'application/x-www-form-urlencoded'}
        )
        
        if response.status_code != 200:
            raise Exception(f"OAuth token request failed: {response.status_code} - {response.text}")
        
        token_data = response.json()
        self._access_token = token_data['access_token']
        
        # Calculate expiry (typically 3600 seconds)
        expires_in = token_data.get('expires_in', 3600)
        self._token_expiry = datetime.now() + timedelta(seconds=expires_in)
        
        # Cache the token
        self._save_token_to_cache()
        
        print(f"✅ OAuth token acquired (expires in {expires_in}s)")
        return self._access_token


class DatabricksMCPClient:
    """MCP client that uses OAuth M2M authentication."""
    
    def __init__(
        self,
        app_url: str,
        workspace_url: str,
        client_id: str,
        client_secret: str
    ):
        """
        Initialize MCP client with OAuth.
        
        Args:
            app_url: Databricks App URL (e.g., https://your-app.databricksapps.com)
            workspace_url: Databricks workspace URL
            client_id: Service principal application ID
            client_secret: OAuth client secret
        """
        self.app_url = app_url.rstrip('/')
        self.oauth_client = DatabricksOAuthClient(workspace_url, client_id, client_secret)
    
    async def call_tool(self, tool_name: str, arguments: dict) -> dict:
        """
        Call an MCP tool on the deployed server.
        
        Args:
            tool_name: Name of the tool to call
            arguments: Tool arguments
            
        Returns:
            Tool result
        """
        token = self.oauth_client.get_access_token()
        
        async with httpx.AsyncClient() as client:
            # Make authenticated request to MCP server
            response = await client.post(
                f"{self.app_url}/mcp",
                json={
                    "jsonrpc": "2.0",
                    "method": "tools/call",
                    "params": {
                        "name": tool_name,
                        "arguments": arguments
                    },
                    "id": 1
                },
                headers={
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json"
                },
                timeout=30.0
            )
            
            if response.status_code != 200:
                raise Exception(f"MCP call failed: {response.status_code} - {response.text}")
            
            return response.json()


async def main():
    """Demo usage of programmatic OAuth client."""
    
    # Get configuration from environment
    APP_URL = os.getenv("DATABRICKS_APP_URL")
    WORKSPACE_URL = os.getenv("DATABRICKS_HOST")
    CLIENT_ID = os.getenv("DATABRICKS_CLIENT_ID")
    CLIENT_SECRET = os.getenv("DATABRICKS_CLIENT_SECRET")
    
    if not all([APP_URL, WORKSPACE_URL, CLIENT_ID, CLIENT_SECRET]):
        print("❌ Missing required environment variables:")
        print("   - DATABRICKS_APP_URL: Your Databricks App URL")
        print("   - DATABRICKS_HOST: Your workspace URL")
        print("   - DATABRICKS_CLIENT_ID: Service principal application ID")
        print("   - DATABRICKS_CLIENT_SECRET: OAuth client secret")
        return
    
    # Create MCP client
    client = DatabricksMCPClient(
        app_url=APP_URL,
        workspace_url=WORKSPACE_URL,
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET
    )
    
    # Test: List clusters
    print("\n📋 Listing clusters...")
    result = await client.call_tool("list_clusters", {})
    print(f"Result: {json.dumps(result, indent=2)}")


if __name__ == "__main__":
    asyncio.run(main())

