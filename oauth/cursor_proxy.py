#!/usr/bin/env python3
"""
MCP Proxy for Cursor - Handles Databricks Apps OAuth authentication.

This proxy runs locally and allows Cursor to access your Databricks MCP server
without dealing with OAuth complexity.

Usage:
    python cursor_proxy.py
    
Then add to Cursor settings:
    MCP Server URL: http://localhost:8080/mcp
"""

import asyncio
import json
import os
import webbrowser
from urllib.parse import urlencode, parse_qs
from typing import Optional

import httpx
from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse, HTMLResponse
import uvicorn

# Configuration
DATABRICKS_HOST = os.getenv("DATABRICKS_HOST", "https://your-workspace.cloud.databricks.com")
DATABRICKS_APP_URL = os.getenv("DATABRICKS_APP_URL", "https://databricks-mcp-server-2556758628403379.aws.databricksapps.com")
MCP_ENDPOINT = f"{DATABRICKS_APP_URL}/mcp"
PROXY_PORT = int(os.getenv("PROXY_PORT", "8080"))

# OAuth session storage (in production, use secure storage)
oauth_session = {
    "cookies": None,
    "authenticated": False
}

app = FastAPI(title="Databricks MCP Proxy for Cursor")


@app.get("/")
async def home():
    """Home page with setup instructions."""
    status = "✅ Authenticated" if oauth_session["authenticated"] else "❌ Not authenticated"
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Databricks MCP Proxy</title>
        <style>
            body {{ font-family: system-ui; max-width: 800px; margin: 50px auto; padding: 20px; }}
            .status {{ padding: 20px; border-radius: 8px; margin: 20px 0; }}
            .success {{ background: #d4edda; border: 1px solid #c3e6cb; color: #155724; }}
            .warning {{ background: #fff3cd; border: 1px solid #ffeaa7; color: #856404; }}
            code {{ background: #f4f4f4; padding: 2px 6px; border-radius: 3px; }}
            pre {{ background: #f4f4f4; padding: 15px; border-radius: 5px; overflow-x: auto; }}
            .button {{ display: inline-block; padding: 10px 20px; background: #007bff; 
                      color: white; text-decoration: none; border-radius: 5px; margin: 10px 0; }}
            .button:hover {{ background: #0056b3; }}
        </style>
    </head>
    <body>
        <h1>🚀 Databricks MCP Proxy for Cursor</h1>
        
        <div class="status {'success' if oauth_session['authenticated'] else 'warning'}">
            <strong>Status:</strong> {status}
        </div>
        
        <h2>Configuration</h2>
        <ul>
            <li><strong>Databricks Host:</strong> {DATABRICKS_HOST}</li>
            <li><strong>MCP Server:</strong> {DATABRICKS_APP_URL}</li>
            <li><strong>Proxy URL:</strong> http://localhost:{PROXY_PORT}</li>
        </ul>
        
        {'<a href="/auth/login" class="button">🔐 Login to Databricks</a>' if not oauth_session['authenticated'] else ''}
        
        <h2>Setup in Cursor</h2>
        <p>Add this MCP server to your Cursor settings:</p>
        
        <pre>{{
  "mcp": {{
    "servers": {{
      "databricks": {{
        "url": "http://localhost:{PROXY_PORT}/mcp"
      }}
    }}
  }}
}}</pre>
        
        <h2>Usage</h2>
        <ol>
            <li>Click "Login to Databricks" above (if not authenticated)</li>
            <li>Complete OAuth flow in browser</li>
            <li>Add MCP server to Cursor settings</li>
            <li>Use natural language in Cursor: "List my Databricks clusters"</li>
        </ol>
        
        <h2>Testing</h2>
        <p>Test the proxy: <a href="/mcp/test">/mcp/test</a></p>
        
        <hr>
        <p><small>Proxy running on port {PROXY_PORT} | MCP endpoint: /mcp</small></p>
    </body>
    </html>
    """
    return HTMLResponse(content=html)


@app.get("/auth/login")
async def login():
    """Initiate OAuth flow with Databricks."""
    # Redirect to Databricks App which will trigger OAuth
    return Response(
        status_code=302,
        headers={"Location": MCP_ENDPOINT}
    )


@app.get("/auth/callback")
async def auth_callback(request: Request):
    """Handle OAuth callback from Databricks."""
    # Store cookies from the callback
    oauth_session["cookies"] = dict(request.cookies)
    oauth_session["authenticated"] = True
    
    return HTMLResponse(content="""
        <!DOCTYPE html>
        <html>
        <head><title>Authentication Success</title></head>
        <body style="font-family: system-ui; text-align: center; padding: 50px;">
            <h1>✅ Authentication Successful!</h1>
            <p>You can now use the MCP server in Cursor.</p>
            <p><a href="/">← Back to Proxy Home</a></p>
        </body>
        </html>
    """)


@app.get("/mcp/test")
async def test_mcp():
    """Test endpoint to verify MCP connection."""
    if not oauth_session["authenticated"]:
        return JSONResponse(
            status_code=401,
            content={
                "error": "Not authenticated",
                "message": "Please visit /auth/login to authenticate"
            }
        )
    
    try:
        async with httpx.AsyncClient(cookies=oauth_session["cookies"]) as client:
            response = await client.post(
                MCP_ENDPOINT,
                json={
                    "jsonrpc": "2.0",
                    "method": "initialize",
                    "params": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {},
                        "clientInfo": {"name": "cursor-proxy", "version": "1.0"}
                    },
                    "id": 1
                },
                timeout=30.0
            )
            
            return JSONResponse(
                status_code=response.status_code,
                content={
                    "status": response.status_code,
                    "response": response.json() if response.status_code == 200 else response.text
                }
            )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )


@app.post("/mcp")
@app.get("/mcp")
async def mcp_proxy(request: Request):
    """
    Main MCP proxy endpoint that forwards requests to Databricks MCP server.
    
    This endpoint:
    1. Receives MCP requests from Cursor
    2. Adds OAuth session cookies
    3. Forwards to Databricks MCP server
    4. Returns response to Cursor
    """
    
    # Check authentication
    if not oauth_session["authenticated"]:
        # Return error in MCP format
        return JSONResponse(
            status_code=200,  # MCP errors are still 200 OK
            content={
                "jsonrpc": "2.0",
                "error": {
                    "code": -32001,
                    "message": "Not authenticated. Visit http://localhost:8080/auth/login to authenticate."
                },
                "id": None
            }
        )
    
    try:
        # Get request body
        if request.method == "POST":
            body = await request.json()
        else:
            body = {"jsonrpc": "2.0", "method": "ping", "id": 1}
        
        # Forward to Databricks MCP server with OAuth cookies
        async with httpx.AsyncClient(
            cookies=oauth_session["cookies"],
            timeout=60.0
        ) as client:
            response = await client.post(
                MCP_ENDPOINT,
                json=body,
                headers={
                    "Content-Type": "application/json",
                    "User-Agent": "Cursor-MCP-Proxy/1.0"
                }
            )
            
            # Return response to Cursor
            return Response(
                content=response.content,
                status_code=response.status_code,
                headers=dict(response.headers)
            )
            
    except httpx.TimeoutException:
        return JSONResponse(
            status_code=200,
            content={
                "jsonrpc": "2.0",
                "error": {
                    "code": -32002,
                    "message": "Request to Databricks MCP server timed out"
                },
                "id": None
            }
        )
    except Exception as e:
        return JSONResponse(
            status_code=200,
            content={
                "jsonrpc": "2.0",
                "error": {
                    "code": -32003,
                    "message": f"Proxy error: {str(e)}"
                },
                "id": None
            }
        )


@app.on_event("startup")
async def startup():
    """Print startup information."""
    print("=" * 80)
    print("🚀 Databricks MCP Proxy for Cursor")
    print("=" * 80)
    print(f"Proxy URL: http://localhost:{PROXY_PORT}")
    print(f"MCP Endpoint: http://localhost:{PROXY_PORT}/mcp")
    print(f"Databricks Host: {DATABRICKS_HOST}")
    print(f"MCP Server: {DATABRICKS_APP_URL}")
    print("=" * 80)
    print()
    print("Next steps:")
    print(f"1. Open http://localhost:{PROXY_PORT} in your browser")
    print("2. Click 'Login to Databricks' and complete OAuth")
    print("3. Add MCP server to Cursor settings")
    print("=" * 80)
    
    # Auto-open browser
    import threading
    def open_browser():
        import time
        time.sleep(1)
        webbrowser.open(f"http://localhost:{PROXY_PORT}")
    
    threading.Thread(target=open_browser, daemon=True).start()


if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=PROXY_PORT,
        log_level="info"
    )

