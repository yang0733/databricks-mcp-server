"""WebSocket transport for MCP protocol."""
import json
from typing import Dict, Any, AsyncIterator
from fastapi import WebSocket, WebSocketDisconnect
from .base import Transport

class WebSocketTransport(Transport):
    """WebSocket transport implementation for MCP."""
    
    def __init__(self, websocket: WebSocket):
        """Initialize WebSocket transport.
        
        Args:
            websocket: FastAPI WebSocket connection
        """
        self.ws = websocket
        self.connected = False
    
    async def connect(self) -> None:
        """Accept the WebSocket connection."""
        await self.ws.accept()
        self.connected = True
    
    async def receive_message(self) -> Dict[str, Any]:
        """Receive JSON-RPC message from client.
        
        Returns:
            Parsed JSON-RPC message
            
        Raises:
            WebSocketDisconnect: If connection is closed
        """
        if not self.connected:
            raise RuntimeError("WebSocket not connected")
        
        data = await self.ws.receive_text()
        return json.loads(data)
    
    async def send_message(self, message: Dict[str, Any]) -> None:
        """Send JSON-RPC message to client.
        
        Args:
            message: JSON-RPC message to send
        """
        if not self.connected:
            raise RuntimeError("WebSocket not connected")
        
        await self.ws.send_text(json.dumps(message))
    
    async def send_stream(self, messages: AsyncIterator[Dict[str, Any]]) -> None:
        """Stream multiple messages efficiently over WebSocket.
        
        Args:
            messages: Async iterator of messages to stream
        """
        async for message in messages:
            await self.send_message(message)
    
    async def close(self) -> None:
        """Close the WebSocket connection."""
        if self.connected:
            await self.ws.close()
            self.connected = False

