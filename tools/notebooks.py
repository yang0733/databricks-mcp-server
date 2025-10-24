"""Notebook management tools for Databricks."""

from typing import Optional, Dict, Any
import base64


def register_tools(mcp, get_wrapper):
    """Register notebook management tools with the MCP server."""
    
    @mcp.tool()
    def import_notebook(
        path: str,
        content: str,
        language: str = "PYTHON",
        format: str = "SOURCE",
        overwrite: bool = False,
        context=None
    ) -> dict:
        """Import a notebook to the workspace.
        
        Args:
            path: Workspace path for the notebook (e.g., /Workspace/Users/me/MyNotebook)
            content: Notebook content (will be base64 encoded if format is SOURCE)
            language: Notebook language (PYTHON, SCALA, SQL, R)
            format: Import format (SOURCE, HTML, JUPYTER, DBC)
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
            language=language,
            format=format,
            overwrite=overwrite
        )
        
        return {
            "path": full_path,
            "status": "imported",
            "message": f"Notebook imported to {full_path}"
        }
    
    @mcp.tool()
    def export_notebook(
        path: str,
        format: str = "SOURCE",
        context=None
    ) -> dict:
        """Export a notebook from the workspace.
        
        Args:
            path: Workspace path of the notebook
            format: Export format (SOURCE, HTML, JUPYTER, DBC)
            
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
            "message": f"Notebook exported from {full_path}. Content is base64 encoded."
        }
    
    @mcp.tool()
    def list_notebooks(
        path: str = "/Workspace",
        recursive: bool = False,
        context=None
    ) -> dict:
        """List notebooks in a workspace directory.
        
        Args:
            path: Workspace directory path
            recursive: Whether to list recursively
            
        Returns:
            Dictionary with list of notebooks
        """
        wrapper = get_wrapper(context)
        
        # Resolve path relative to context if needed
        full_path = wrapper.resolve_workspace_path(path)
        
        objects = wrapper.client.workspace.list(full_path)
        
        notebook_list = []
        for obj in objects:
            if obj.object_type and obj.object_type.value == "NOTEBOOK":
                notebook_list.append({
                    "path": obj.path,
                    "language": obj.language.value if obj.language else None,
                    "created_at": obj.created_at,
                    "modified_at": obj.modified_at,
                })
        
        return {
            "notebooks": notebook_list,
            "count": len(notebook_list),
            "base_path": full_path
        }
    
    @mcp.tool()
    def run_notebook(
        path: str,
        cluster_id: Optional[str] = None,
        timeout_seconds: int = 3600,
        notebook_params: Optional[Dict[str, str]] = None,
        context=None
    ) -> dict:
        """Run a notebook and return results.
        
        Args:
            path: Workspace path of the notebook
            cluster_id: Cluster to run on (uses current cluster if not provided)
            timeout_seconds: Timeout in seconds (default 1 hour)
            notebook_params: Parameters to pass to the notebook
            
        Returns:
            Dictionary with run results
        """
        wrapper = get_wrapper(context)
        
        # Resolve path and cluster
        full_path = wrapper.resolve_workspace_path(path)
        cid = cluster_id or wrapper.get_current_cluster_id()
        
        if not cid:
            return {"error": "No cluster_id provided and no current cluster set"}
        
        # Submit one-time run
        run_config = {
            "run_name": f"Notebook run: {full_path}",
            "notebook_task": {
                "notebook_path": full_path,
                "source": "WORKSPACE"
            },
            "existing_cluster_id": cid,
            "timeout_seconds": timeout_seconds,
        }
        
        if notebook_params:
            run_config["notebook_task"]["base_parameters"] = notebook_params
        
        response = wrapper.client.jobs.submit(**run_config)
        run_id = response.run_id
        
        return {
            "run_id": run_id,
            "path": full_path,
            "cluster_id": cid,
            "status": "submitted",
            "message": f"Notebook run submitted with ID {run_id}. Use get_run tool to check status."
        }

