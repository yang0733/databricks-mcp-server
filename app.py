"""ASGI app wrapper for Databricks Apps deployment."""

from server import mcp

# Expose the ASGI app for uvicorn
app = mcp.streamable_http_app

if __name__ == "__main__":
    import uvicorn
    import os
    
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
