"""Async task management for long-running operations."""
import asyncio
import uuid
from typing import Dict, Any, Callable, Optional
from datetime import datetime, timedelta
from enum import Enum

class TaskStatus(str, Enum):
    """Task execution status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class Task:
    """Represents an async task."""
    
    def __init__(self, task_id: str, operation: str):
        """Initialize a task.
        
        Args:
            task_id: Unique task identifier
            operation: Description of the operation
        """
        self.task_id = task_id
        self.operation = operation
        self.status = TaskStatus.PENDING
        self.progress = 0
        self.result = None
        self.error = None
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        self.poll_after_ms = 2000  # Recommended polling interval
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert task to dictionary for JSON serialization."""
        return {
            "task_id": self.task_id,
            "operation": self.operation,
            "status": self.status.value,
            "progress": self.progress,
            "result": self.result,
            "error": self.error,
            "poll_after_ms": self.poll_after_ms,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }

class TaskManager:
    """Manages async tasks with in-memory storage."""
    
    def __init__(self):
        """Initialize task manager."""
        self.tasks: Dict[str, Task] = {}
        self.cleanup_interval = 3600  # Clean up tasks after 1 hour
        self._cleanup_task = None
    
    async def start(self):
        """Start background cleanup task."""
        if not self._cleanup_task:
            self._cleanup_task = asyncio.create_task(self._periodic_cleanup())
    
    async def stop(self):
        """Stop background cleanup task."""
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
    
    async def create_task(
        self, 
        operation: str, 
        executor: Callable,
        *args,
        **kwargs
    ) -> Task:
        """Create and start a background task.
        
        Args:
            operation: Description of the operation
            executor: Async function to execute
            *args: Positional arguments for executor
            **kwargs: Keyword arguments for executor
            
        Returns:
            Task object with task_id for tracking
        """
        task_id = str(uuid.uuid4())
        task = Task(task_id, operation)
        self.tasks[task_id] = task
        
        # Run in background
        asyncio.create_task(self._execute_task(task, executor, *args, **kwargs))
        
        return task
    
    async def _execute_task(self, task: Task, executor: Callable, *args, **kwargs):
        """Execute task in background.
        
        Args:
            task: Task object to update
            executor: Async function to execute
            *args: Positional arguments for executor
            **kwargs: Keyword arguments for executor
        """
        try:
            task.status = TaskStatus.RUNNING
            task.updated_at = datetime.utcnow()
            
            # Execute the operation
            result = await executor(*args, **kwargs)
            
            # Task completed successfully
            task.status = TaskStatus.COMPLETED
            task.progress = 100
            task.result = result
            
        except asyncio.CancelledError:
            task.status = TaskStatus.CANCELLED
            task.error = "Task was cancelled"
            
        except Exception as e:
            task.status = TaskStatus.FAILED
            task.error = str(e)
            
        finally:
            task.updated_at = datetime.utcnow()
    
    def get_task(self, task_id: str) -> Optional[Task]:
        """Get task by ID.
        
        Args:
            task_id: Task identifier
            
        Returns:
            Task object or None if not found
        """
        return self.tasks.get(task_id)
    
    async def cancel_task(self, task_id: str) -> bool:
        """Cancel a running task.
        
        Args:
            task_id: Task identifier
            
        Returns:
            True if task was cancelled, False otherwise
        """
        task = self.tasks.get(task_id)
        if task and task.status in [TaskStatus.PENDING, TaskStatus.RUNNING]:
            task.status = TaskStatus.CANCELLED
            task.updated_at = datetime.utcnow()
            return True
        return False
    
    async def _periodic_cleanup(self):
        """Periodically clean up old completed tasks."""
        while True:
            try:
                await asyncio.sleep(300)  # Run every 5 minutes
                await self.cleanup_old_tasks()
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"Error in cleanup task: {e}")
    
    async def cleanup_old_tasks(self):
        """Remove completed/failed tasks older than cleanup_interval."""
        cutoff = datetime.utcnow() - timedelta(seconds=self.cleanup_interval)
        to_remove = [
            tid for tid, task in self.tasks.items()
            if task.status in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED]
            and task.updated_at < cutoff
        ]
        for tid in to_remove:
            del self.tasks[tid]

# Global task manager instance
task_manager = TaskManager()

