"""Base transport interface for MCP protocol."""
from abc import ABC, abstractmethod
from typing import Dict, Any, AsyncIterator

class Transport(ABC):
    """Abstract base class for MCP transports."""
    
    @abstractmethod
    async def receive_message(self) -> Dict[str, Any]:
        """Receive a JSON-RPC message from the client."""
        pass
    
    @abstractmethod
    async def send_message(self, message: Dict[str, Any]) -> None:
        """Send a JSON-RPC message to the client."""
        pass
    
    async def send_stream(self, messages: AsyncIterator[Dict[str, Any]]) -> None:
        """Stream multiple messages (e.g., for progress updates).
        
        Default implementation sends messages one by one.
        Transports can override for optimized streaming.
        """
        async for message in messages:
            await self.send_message(message)
    
    async def close(self) -> None:
        """Close the transport connection."""
        pass

