"""
OAuth M2M Proxy for Cursor.

This proxy sits between Cursor and the Databricks MCP Server,
automatically handling OAuth M2M authentication so Cursor can
access the deployed app without any manual OAuth flow.
"""

import os
import json
import asyncio
from fastapi import FastAPI, Request, Response
from fastapi.responses import StreamingResponse
import httpx
from programmatic_oauth_client import DatabricksOAuthClient

app = FastAPI()

# Configuration from environment
DATABRICKS_APP_URL = os.getenv("DATABRICKS_APP_URL", "").rstrip('/')
WORKSPACE_URL = os.getenv("DATABRICKS_HOST", "").rstrip('/')
CLIENT_ID = os.getenv("DATABRICKS_CLIENT_ID", "")
CLIENT_SECRET = os.getenv("DATABRICKS_CLIENT_SECRET", "")

if not all([DATABRICKS_APP_URL, WORKSPACE_URL, CLIENT_ID, CLIENT_SECRET]):
    print("❌ Missing configuration! Set these environment variables:")
    print("   - DATABRICKS_APP_URL")
    print("   - DATABRICKS_HOST")
    print("   - DATABRICKS_CLIENT_ID")
    print("   - DATABRICKS_CLIENT_SECRET")
    exit(1)

# OAuth client
oauth_client = DatabricksOAuthClient(
    workspace_url=WORKSPACE_URL,
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET
)

print(f"""
╔════════════════════════════════════════════════════════════════╗
║  Databricks MCP OAuth Proxy (M2M Authentication)               ║
╚════════════════════════════════════════════════════════════════╝

✅ OAuth M2M Configuration:
   Workspace: {WORKSPACE_URL}
   Client ID: {CLIENT_ID[:8]}...
   App URL:   {DATABRICKS_APP_URL}

🚀 Proxy running at: http://localhost:8080/mcp

📝 Configure Cursor:
   Add this to your MCP settings:
   {{"url": "http://localhost:8080/mcp"}}

🔐 Authentication:
   - Programmatic OAuth (no browser needed!)
   - Tokens auto-refresh
   - Fully automated
""")


@app.api_route("/mcp", methods=["GET", "POST", "OPTIONS"])
async def proxy_mcp(request: Request):
    """
    Proxy all /mcp requests to Databricks App with OAuth token.
    """
    try:
        # Get OAuth token (automatically refreshed if needed)
        access_token = oauth_client.get_access_token()
        
        # Get request body
        body = await request.body()
        
        # Forward to Databricks App with OAuth token
        async with httpx.AsyncClient() as client:
            response = await client.request(
                method=request.method,
                url=f"{DATABRICKS_APP_URL}/mcp",
                content=body,
                headers={
                    **dict(request.headers),
                    "Authorization": f"Bearer {access_token}",
                    "Host": DATABRICKS_APP_URL.split("//")[1]  # Fix Host header
                },
                timeout=30.0
            )
        
        # Return response
        return Response(
            content=response.content,
            status_code=response.status_code,
            headers=dict(response.headers)
        )
    
    except Exception as e:
        print(f"❌ Proxy error: {e}")
        return Response(
            content=json.dumps({"error": str(e)}),
            status_code=500,
            media_type="application/json"
        )


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {
        "status": "ok",
        "oauth": "m2m",
        "app_url": DATABRICKS_APP_URL,
        "workspace": WORKSPACE_URL
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080, log_level="info")

