"""Databricks client wrapper with stateful context management."""

from typing import Any, Optional, Dict
from databricks.sdk import WorkspaceClient
from datetime import datetime


class SessionContext:
    """Maintains stateful context for a Databricks session."""
    
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.created_at = datetime.now()
        self.workspace_path: Optional[str] = "/Workspace"
        self.current_cluster_id: Optional[str] = None
        self.current_job_id: Optional[str] = None
        self.current_warehouse_id: Optional[str] = None
        self.metadata: Dict[str, Any] = {}
        
    def set_workspace_path(self, path: str):
        """Set current workspace path for relative operations."""
        self.workspace_path = path
        
    def set_cluster(self, cluster_id: str):
        """Set current cluster for operations."""
        self.current_cluster_id = cluster_id
        
    def set_job(self, job_id: str):
        """Set current job for operations."""
        self.current_job_id = job_id
        
    def set_warehouse(self, warehouse_id: str):
        """Set current warehouse for SQL operations."""
        self.current_warehouse_id = warehouse_id
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert context to dictionary for serialization."""
        return {
            "session_id": self.session_id,
            "workspace_path": self.workspace_path,
            "current_cluster_id": self.current_cluster_id,
            "current_job_id": self.current_job_id,
            "current_warehouse_id": self.current_warehouse_id,
            "metadata": self.metadata,
        }


class ContextManager:
    """Manages session contexts for stateful operations."""
    
    def __init__(self):
        self.contexts: Dict[str, SessionContext] = {}
        
    def get_or_create_context(self, session_id: str) -> SessionContext:
        """Get existing context or create new one."""
        if session_id not in self.contexts:
            self.contexts[session_id] = SessionContext(session_id)
        return self.contexts[session_id]
        
    def get_context(self, session_id: str) -> Optional[SessionContext]:
        """Get existing context without creating."""
        return self.contexts.get(session_id)
        
    def clear_context(self, session_id: str):
        """Remove session context."""
        if session_id in self.contexts:
            del self.contexts[session_id]


# Global context manager instance
context_manager = ContextManager()


class DatabricksClientWrapper:
    """Wrapper around Databricks SDK client with convenience methods."""
    
    def __init__(self, client: WorkspaceClient, session_context: Optional[SessionContext] = None):
        self.client = client
        self.context = session_context
        
    def resolve_workspace_path(self, path: str) -> str:
        """Resolve path relative to context workspace path if not absolute."""
        if path.startswith('/'):
            return path
        if self.context and self.context.workspace_path:
            base = self.context.workspace_path
            return f"{base.rstrip('/')}/{path.lstrip('/')}"
        return path
        
    def get_current_cluster_id(self) -> Optional[str]:
        """Get current cluster ID from context."""
        return self.context.current_cluster_id if self.context else None
        
    def get_current_job_id(self) -> Optional[str]:
        """Get current job ID from context."""
        return self.context.current_job_id if self.context else None
        
    def get_current_warehouse_id(self) -> Optional[str]:
        """Get current warehouse ID from context."""
        return self.context.current_warehouse_id if self.context else None


