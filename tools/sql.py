"""SQL warehouse and query execution tools for Databricks."""

from typing import Optional, Dict, Any
import time


def register_tools(mcp, get_wrapper):
    """Register SQL tools with the MCP server."""
    
    @mcp.tool()
    def list_warehouses(context=None) -> dict:
        """List all SQL warehouses in the workspace.
        
        Returns:
            Dictionary with list of warehouses
        """
        wrapper = get_wrapper(context)
        
        warehouses = wrapper.client.warehouses.list()
        
        warehouse_list = []
        for wh in warehouses:
            warehouse_list.append({
                "id": wh.id,
                "name": wh.name,
                "state": wh.state.value if wh.state else None,
                "cluster_size": wh.cluster_size,
                "min_num_clusters": wh.min_num_clusters,
                "max_num_clusters": wh.max_num_clusters,
                "num_clusters": wh.num_clusters,
                "enable_photon": wh.enable_photon,
                "warehouse_type": wh.warehouse_type.value if wh.warehouse_type else None,
            })
        
        return {
            "warehouses": warehouse_list,
            "count": len(warehouse_list)
        }
    
    @mcp.tool()
    def start_warehouse(
        warehouse_id: Optional[str] = None,
        context=None
    ) -> dict:
        """Start a SQL warehouse.
        
        Args:
            warehouse_id: Warehouse ID to start (uses current warehouse if not provided)
            
        Returns:
            Dictionary with start status
        """
        wrapper = get_wrapper(context)
        
        wid = warehouse_id or wrapper.get_current_warehouse_id()
        if not wid:
            return {"error": "No warehouse_id provided and no current warehouse set"}
        
        wrapper.client.warehouses.start(wid)
        
        return {
            "warehouse_id": wid,
            "status": "starting",
            "message": f"Warehouse {wid} is starting"
        }
    
    @mcp.tool()
    def stop_warehouse(
        warehouse_id: Optional[str] = None,
        context=None
    ) -> dict:
        """Stop a SQL warehouse.
        
        Args:
            warehouse_id: Warehouse ID to stop (uses current warehouse if not provided)
            
        Returns:
            Dictionary with stop status
        """
        wrapper = get_wrapper(context)
        
        wid = warehouse_id or wrapper.get_current_warehouse_id()
        if not wid:
            return {"error": "No warehouse_id provided and no current warehouse set"}
        
        wrapper.client.warehouses.stop(wid)
        
        return {
            "warehouse_id": wid,
            "status": "stopping",
            "message": f"Warehouse {wid} is stopping"
        }
    
    @mcp.tool()
    def execute_query(
        query: str,
        warehouse_id: Optional[str] = None,
        wait_timeout: str = "30s",
        context=None
    ) -> dict:
        """Execute a SQL query on a warehouse.
        
        Args:
            query: SQL query to execute
            warehouse_id: Warehouse ID to use (uses current warehouse if not provided)
            wait_timeout: How long to wait for results (e.g., "30s", "5m")
            
        Returns:
            Dictionary with query execution details and statement ID
        """
        wrapper = get_wrapper(context)
        
        wid = warehouse_id or wrapper.get_current_warehouse_id()
        if not wid:
            return {"error": "No warehouse_id provided and no current warehouse set"}
        
        # Execute statement
        response = wrapper.client.statement_execution.execute_statement(
            warehouse_id=wid,
            statement=query,
            wait_timeout=wait_timeout
        )
        
        result = {
            "statement_id": response.statement_id,
            "status": response.status.state.value if response.status and response.status.state else None,
            "warehouse_id": wid,
        }
        
        # Include results if available
        if response.result:
            result["row_count"] = response.result.row_count
            result["data_array"] = response.result.data_array if response.result.data_array else []
            result["truncated"] = response.result.truncated
            
        result["message"] = f"Query executed. Statement ID: {response.statement_id}"
        
        return result
    
    @mcp.tool()
    def get_query_results(
        statement_id: str,
        context=None
    ) -> dict:
        """Get results from a previously executed query.
        
        Args:
            statement_id: Statement ID from execute_query
            
        Returns:
            Dictionary with query results
        """
        wrapper = get_wrapper(context)
        
        # Get statement status and results
        response = wrapper.client.statement_execution.get_statement(statement_id)
        
        result = {
            "statement_id": statement_id,
            "status": response.status.state.value if response.status and response.status.state else None,
        }
        
        # Include results if available
        if response.result:
            result["row_count"] = response.result.row_count
            result["data_array"] = response.result.data_array if response.result.data_array else []
            result["truncated"] = response.result.truncated
            result["chunk_index"] = response.result.chunk_index
            result["has_more_chunks"] = response.result.next_chunk_index is not None
            
            # Include schema information
            if response.manifest and response.manifest.schema:
                result["schema"] = [
                    {
                        "name": col.name,
                        "type": col.type_name.value if col.type_name else None,
                    }
                    for col in response.manifest.schema.columns
                ]
        
        return result

