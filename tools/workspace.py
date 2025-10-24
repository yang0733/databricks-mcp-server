"""Workspace file management tools for Databricks."""

from typing import Optional
import base64


def register_tools(mcp, get_wrapper):
    """Register workspace management tools with the MCP server."""
    
    @mcp.tool()
    def list_workspace(
        path: str = "/Workspace",
        context=None
    ) -> dict:
        """List objects in a workspace directory.
        
        Args:
            path: Workspace directory path
            
        Returns:
            Dictionary with list of workspace objects
        """
        wrapper = get_wrapper(context)
        
        # Resolve path relative to context if needed
        full_path = wrapper.resolve_workspace_path(path)
        
        objects = wrapper.client.workspace.list(full_path)
        
        object_list = []
        for obj in objects:
            object_list.append({
                "path": obj.path,
                "object_type": obj.object_type.value if obj.object_type else None,
                "language": obj.language.value if obj.language else None,
                "created_at": obj.created_at,
                "modified_at": obj.modified_at,
                "size": obj.size,
            })
        
        return {
            "objects": object_list,
            "count": len(object_list),
            "base_path": full_path
        }
    
    @mcp.tool()
    def import_file(
        path: str,
        content: str,
        format: str = "AUTO",
        overwrite: bool = False,
        context=None
    ) -> dict:
        """Import a file to the workspace.
        
        Args:
            path: Workspace path for the file
            content: File content (will be base64 encoded)
            format: Import format (SOURCE, HTML, JUPYTER, DBC, AUTO)
            overwrite: Whether to overwrite if exists
            
        Returns:
            Dictionary with import status
        """
        wrapper = get_wrapper(context)
        
        # Resolve path relative to context if needed
        full_path = wrapper.resolve_workspace_path(path)
        
        # Base64 encode content if not already encoded
        try:
            base64.b64decode(content)
            encoded_content = content
        except:
            encoded_content = base64.b64encode(content.encode()).decode()
        
        wrapper.client.workspace.import_(
            path=full_path,
            content=encoded_content,
            format=format,
            overwrite=overwrite
        )
        
        return {
            "path": full_path,
            "status": "imported",
            "message": f"File imported to {full_path}"
        }
    
    @mcp.tool()
    def export_file(
        path: str,
        format: str = "SOURCE",
        context=None
    ) -> dict:
        """Export a file from the workspace.
        
        Args:
            path: Workspace path of the file
            format: Export format (SOURCE, HTML, JUPYTER, DBC, AUTO)
            
        Returns:
            Dictionary with exported content (base64 encoded)
        """
        wrapper = get_wrapper(context)
        
        # Resolve path relative to context if needed
        full_path = wrapper.resolve_workspace_path(path)
        
        result = wrapper.client.workspace.export(
            path=full_path,
            format=format
        )
        
        return {
            "path": full_path,
            "format": format,
            "content": result.content,
            "message": f"File exported from {full_path}. Content is base64 encoded."
        }
    
    @mcp.tool()
    def delete_path(
        path: str,
        recursive: bool = False,
        context=None
    ) -> dict:
        """Delete a workspace path (file or directory).
        
        Args:
            path: Workspace path to delete
            recursive: Whether to delete recursively (required for directories)
            
        Returns:
            Dictionary with deletion status
        """
        wrapper = get_wrapper(context)
        
        # Resolve path relative to context if needed
        full_path = wrapper.resolve_workspace_path(path)
        
        wrapper.client.workspace.delete(
            path=full_path,
            recursive=recursive
        )
        
        return {
            "path": full_path,
            "status": "deleted",
            "message": f"Path {full_path} has been deleted"
        }
    
    @mcp.tool()
    def mkdirs(
        path: str,
        context=None
    ) -> dict:
        """Create a directory in the workspace.
        
        Args:
            path: Workspace directory path to create
            
        Returns:
            Dictionary with creation status
        """
        wrapper = get_wrapper(context)
        
        # Resolve path relative to context if needed
        full_path = wrapper.resolve_workspace_path(path)
        
        wrapper.client.workspace.mkdirs(full_path)
        
        return {
            "path": full_path,
            "status": "created",
            "message": f"Directory {full_path} has been created"
        }

