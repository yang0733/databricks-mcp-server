"""Cluster management tools for Databricks."""

from typing import Optional, Dict, Any, List


def register_tools(mcp, get_wrapper):
    """Register cluster management tools with the MCP server."""
    
    @mcp.tool()
    def create_cluster(
        cluster_name: str,
        spark_version: str,
        node_type_id: str,
        num_workers: int = 1,
        autoscale_min_workers: Optional[int] = None,
        autoscale_max_workers: Optional[int] = None,
        autotermination_minutes: int = 30,
        spark_conf: Optional[Dict[str, str]] = None,
        context=None
    ) -> dict:
        """Create a new Databricks cluster.
        
        Args:
            cluster_name: Name for the cluster
            spark_version: Spark version (e.g., "13.3.x-scala2.12")
            node_type_id: Node type (e.g., "i3.xlarge", "Standard_DS3_v2")
            num_workers: Number of workers (ignored if autoscale is set)
            autoscale_min_workers: Minimum workers for autoscaling
            autoscale_max_workers: Maximum workers for autoscaling
            autotermination_minutes: Auto-termination time in minutes
            spark_conf: Optional Spark configuration dictionary
            
        Returns:
            Dictionary with cluster_id and creation details
        """
        wrapper = get_wrapper(context)
        
        cluster_config = {
            "cluster_name": cluster_name,
            "spark_version": spark_version,
            "node_type_id": node_type_id,
            "autotermination_minutes": autotermination_minutes,
        }
        
        if autoscale_min_workers and autoscale_max_workers:
            cluster_config["autoscale"] = {
                "min_workers": autoscale_min_workers,
                "max_workers": autoscale_max_workers
            }
        else:
            cluster_config["num_workers"] = num_workers
            
        if spark_conf:
            cluster_config["spark_conf"] = spark_conf
        
        response = wrapper.client.clusters.create(**cluster_config)
        cluster_id = response.cluster_id
        
        # Set as current cluster in context
        if wrapper.context:
            wrapper.context.set_cluster(cluster_id)
        
        return {
            "cluster_id": cluster_id,
            "cluster_name": cluster_name,
            "status": "creating",
            "message": f"Cluster {cluster_id} is being created. Set as current cluster."
        }
    
    @mcp.tool()
    def start_cluster(cluster_id: Optional[str] = None, context=None) -> dict:
        """Start a stopped cluster.
        
        Args:
            cluster_id: Cluster ID to start (uses current cluster if not provided)
            
        Returns:
            Dictionary with cluster status
        """
        wrapper = get_wrapper(context)
        
        cid = cluster_id or wrapper.get_current_cluster_id()
        if not cid:
            return {"error": "No cluster_id provided and no current cluster set"}
        
        wrapper.client.clusters.start(cid)
        return {
            "cluster_id": cid,
            "status": "starting",
            "message": f"Cluster {cid} is starting"
        }
    
    @mcp.tool()
    def stop_cluster(cluster_id: Optional[str] = None, context=None) -> dict:
        """Stop a running cluster.
        
        Args:
            cluster_id: Cluster ID to stop (uses current cluster if not provided)
            
        Returns:
            Dictionary with cluster status
        """
        wrapper = get_wrapper(context)
        
        cid = cluster_id or wrapper.get_current_cluster_id()
        if not cid:
            return {"error": "No cluster_id provided and no current cluster set"}
        
        wrapper.client.clusters.delete(cid)
        return {
            "cluster_id": cid,
            "status": "stopping",
            "message": f"Cluster {cid} is stopping"
        }
    
    @mcp.tool()
    def delete_cluster(cluster_id: Optional[str] = None, context=None) -> dict:
        """Permanently delete a cluster.
        
        Args:
            cluster_id: Cluster ID to delete (uses current cluster if not provided)
            
        Returns:
            Dictionary with deletion status
        """
        wrapper = get_wrapper(context)
        
        cid = cluster_id or wrapper.get_current_cluster_id()
        if not cid:
            return {"error": "No cluster_id provided and no current cluster set"}
        
        wrapper.client.clusters.permanent_delete(cid)
        
        # Clear from context if it was current
        if wrapper.context and wrapper.context.current_cluster_id == cid:
            wrapper.context.current_cluster_id = None
        
        return {
            "cluster_id": cid,
            "status": "deleted",
            "message": f"Cluster {cid} has been permanently deleted"
        }
    
    @mcp.tool()
    def list_clusters(context=None) -> dict:
        """List all clusters in the workspace.
        
        Returns:
            Dictionary with list of clusters and their details
        """
        wrapper = get_wrapper(context)
        
        clusters = wrapper.client.clusters.list()
        cluster_list = []
        
        for cluster in clusters:
            cluster_list.append({
                "cluster_id": cluster.cluster_id,
                "cluster_name": cluster.cluster_name,
                "state": cluster.state.value if cluster.state else "UNKNOWN",
                "spark_version": cluster.spark_version,
                "node_type_id": cluster.node_type_id,
                "num_workers": cluster.num_workers,
                "creator_user_name": cluster.creator_user_name,
            })
        
        return {
            "clusters": cluster_list,
            "count": len(cluster_list)
        }
    
    @mcp.tool()
    def get_cluster(cluster_id: Optional[str] = None, context=None) -> dict:
        """Get detailed information about a specific cluster.
        
        Args:
            cluster_id: Cluster ID to query (uses current cluster if not provided)
            
        Returns:
            Dictionary with detailed cluster information
        """
        wrapper = get_wrapper(context)
        
        cid = cluster_id or wrapper.get_current_cluster_id()
        if not cid:
            return {"error": "No cluster_id provided and no current cluster set"}
        
        cluster = wrapper.client.clusters.get(cid)
        
        return {
            "cluster_id": cluster.cluster_id,
            "cluster_name": cluster.cluster_name,
            "state": cluster.state.value if cluster.state else "UNKNOWN",
            "spark_version": cluster.spark_version,
            "node_type_id": cluster.node_type_id,
            "driver_node_type_id": cluster.driver_node_type_id,
            "num_workers": cluster.num_workers,
            "autoscale": {
                "min_workers": cluster.autoscale.min_workers,
                "max_workers": cluster.autoscale.max_workers
            } if cluster.autoscale else None,
            "autotermination_minutes": cluster.autotermination_minutes,
            "creator_user_name": cluster.creator_user_name,
            "start_time": cluster.start_time,
            "terminated_time": cluster.terminated_time,
            "state_message": cluster.state_message,
        }


