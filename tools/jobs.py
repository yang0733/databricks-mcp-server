"""Job management tools for Databricks."""

from typing import Optional, Dict, Any, List


def register_tools(mcp, get_wrapper):
    """Register job management tools with the MCP server."""
    
    @mcp.tool()
    def create_job(
        job_name: str,
        tasks: List[Dict[str, Any]],
        schedule: Optional[Dict[str, str]] = None,
        max_concurrent_runs: int = 1,
        timeout_seconds: Optional[int] = None,
        context=None
    ) -> dict:
        """Create a new Databricks job with one or more tasks.
        
        Args:
            job_name: Name for the job
            tasks: List of task configurations (each with task_key, notebook_task/spark_jar_task, etc.)
            schedule: Optional schedule configuration with quartz_cron_expression and timezone_id
            max_concurrent_runs: Maximum number of concurrent runs
            timeout_seconds: Optional timeout for the job
            
        Returns:
            Dictionary with job_id and creation details
            
        Example tasks format:
        [
            {
                "task_key": "my_task",
                "notebook_task": {
                    "notebook_path": "/Workspace/MyNotebook",
                    "source": "WORKSPACE"
                },
                "new_cluster": {...}
            }
        ]
        """
        wrapper = get_wrapper(context)
        
        job_config = {
            "name": job_name,
            "tasks": tasks,
            "max_concurrent_runs": max_concurrent_runs,
        }
        
        if schedule:
            job_config["schedule"] = schedule
        if timeout_seconds:
            job_config["timeout_seconds"] = timeout_seconds
        
        response = wrapper.client.jobs.create(**job_config)
        job_id = response.job_id
        
        # Set as current job in context
        if wrapper.context:
            wrapper.context.set_job(str(job_id))
        
        return {
            "job_id": job_id,
            "job_name": job_name,
            "status": "created",
            "message": f"Job {job_id} created successfully. Set as current job."
        }
    
    @mcp.tool()
    def run_job(
        job_id: Optional[int] = None,
        notebook_params: Optional[Dict[str, str]] = None,
        jar_params: Optional[List[str]] = None,
        python_params: Optional[List[str]] = None,
        context=None
    ) -> dict:
        """Trigger a job run.
        
        Args:
            job_id: Job ID to run (uses current job if not provided)
            notebook_params: Parameters for notebook tasks
            jar_params: Parameters for JAR tasks
            python_params: Parameters for Python tasks
            
        Returns:
            Dictionary with run_id and status
        """
        wrapper = get_wrapper(context)
        
        jid = job_id or (int(wrapper.get_current_job_id()) if wrapper.get_current_job_id() else None)
        if not jid:
            return {"error": "No job_id provided and no current job set"}
        
        run_config = {"job_id": jid}
        if notebook_params:
            run_config["notebook_params"] = notebook_params
        if jar_params:
            run_config["jar_params"] = jar_params
        if python_params:
            run_config["python_params"] = python_params
        
        response = wrapper.client.jobs.run_now(**run_config)
        
        return {
            "run_id": response.run_id,
            "job_id": jid,
            "status": "running",
            "message": f"Job run {response.run_id} started for job {jid}"
        }
    
    @mcp.tool()
    def list_jobs(
        limit: int = 25,
        offset: int = 0,
        expand_tasks: bool = False,
        context=None
    ) -> dict:
        """List all jobs in the workspace.
        
        Args:
            limit: Maximum number of jobs to return
            offset: Offset for pagination
            expand_tasks: Whether to include task details
            
        Returns:
            Dictionary with list of jobs
        """
        wrapper = get_wrapper(context)
        
        jobs = wrapper.client.jobs.list(
            limit=limit,
            offset=offset,
            expand_tasks=expand_tasks
        )
        
        job_list = []
        for job in jobs:
            job_list.append({
                "job_id": job.job_id,
                "name": job.settings.name if job.settings else None,
                "creator_user_name": job.creator_user_name,
                "created_time": job.created_time,
            })
        
        return {
            "jobs": job_list,
            "count": len(job_list),
            "has_more": len(job_list) == limit
        }
    
    @mcp.tool()
    def get_job(job_id: Optional[int] = None, context=None) -> dict:
        """Get detailed information about a specific job.
        
        Args:
            job_id: Job ID to query (uses current job if not provided)
            
        Returns:
            Dictionary with detailed job configuration
        """
        wrapper = get_wrapper(context)
        
        jid = job_id or (int(wrapper.get_current_job_id()) if wrapper.get_current_job_id() else None)
        if not jid:
            return {"error": "No job_id provided and no current job set"}
        
        job = wrapper.client.jobs.get(jid)
        
        return {
            "job_id": job.job_id,
            "name": job.settings.name if job.settings else None,
            "creator_user_name": job.creator_user_name,
            "created_time": job.created_time,
            "settings": {
                "name": job.settings.name,
                "max_concurrent_runs": job.settings.max_concurrent_runs,
                "timeout_seconds": job.settings.timeout_seconds,
                "schedule": {
                    "quartz_cron_expression": job.settings.schedule.quartz_cron_expression,
                    "timezone_id": job.settings.schedule.timezone_id,
                    "pause_status": job.settings.schedule.pause_status.value if job.settings.schedule.pause_status else None
                } if job.settings.schedule else None,
                "tasks": [
                    {
                        "task_key": task.task_key,
                        "description": task.description,
                    }
                    for task in (job.settings.tasks or [])
                ]
            } if job.settings else None
        }
    
    @mcp.tool()
    def get_run(run_id: int, context=None) -> dict:
        """Get information about a specific job run.
        
        Args:
            run_id: Run ID to query
            
        Returns:
            Dictionary with run details and status
        """
        wrapper = get_wrapper(context)
        
        run = wrapper.client.jobs.get_run(run_id)
        
        return {
            "run_id": run.run_id,
            "job_id": run.job_id,
            "run_name": run.run_name,
            "state": {
                "life_cycle_state": run.state.life_cycle_state.value if run.state and run.state.life_cycle_state else None,
                "result_state": run.state.result_state.value if run.state and run.state.result_state else None,
                "state_message": run.state.state_message if run.state else None,
            },
            "start_time": run.start_time,
            "end_time": run.end_time,
            "setup_duration": run.setup_duration,
            "execution_duration": run.execution_duration,
            "cleanup_duration": run.cleanup_duration,
        }
    
    @mcp.tool()
    def cancel_run(run_id: int, context=None) -> dict:
        """Cancel a running job.
        
        Args:
            run_id: Run ID to cancel
            
        Returns:
            Dictionary with cancellation status
        """
        wrapper = get_wrapper(context)
        
        wrapper.client.jobs.cancel_run(run_id)
        
        return {
            "run_id": run_id,
            "status": "canceling",
            "message": f"Run {run_id} is being canceled"
        }
    
    @mcp.tool()
    def delete_job(job_id: Optional[int] = None, context=None) -> dict:
        """Delete a job.
        
        Args:
            job_id: Job ID to delete (uses current job if not provided)
            
        Returns:
            Dictionary with deletion status
        """
        wrapper = get_wrapper(context)
        
        jid = job_id or (int(wrapper.get_current_job_id()) if wrapper.get_current_job_id() else None)
        if not jid:
            return {"error": "No job_id provided and no current job set"}
        
        wrapper.client.jobs.delete(jid)
        
        # Clear from context if it was current
        if wrapper.context and wrapper.context.current_job_id == str(jid):
            wrapper.context.current_job_id = None
        
        return {
            "job_id": jid,
            "status": "deleted",
            "message": f"Job {jid} has been deleted"
        }

