from typing import List, Optional, Dict, Set
from ..tasks.task import Task
from ..tasks.task_graph import TaskGraph
from ..core.agent_state import TaskStatus, TaskPriority
from ..core.agent_registry import AgentRegistry
from ..core.agent import Agent

class TaskScheduler:
    """
    TaskScheduler scheduling tasks based on DAG readiness, priorities, agent capabilities and locks.
    """
    def __init__(self, registry: AgentRegistry, max_concurrency: int = 4):
        self.registry = registry
        self.max_concurrency = max_concurrency
        self._active_locks: Set[str] = set()

    def get_schedulable_tasks(self, graph: TaskGraph) -> List[Task]:
        ready_tasks = graph.get_ready_tasks()
        
        # Sort by priority
        priority_order = {
            TaskPriority.CRITICAL: 1,
            TaskPriority.HIGH: 2,
            TaskPriority.NORMAL: 3,
            TaskPriority.LOW: 4,
            TaskPriority.BACKGROUND: 5
        }
        ready_tasks.sort(key=lambda t: priority_order.get(t.priority, 3))
        
        schedulable = []
        for task in ready_tasks:
            # Check resource locks
            task_locks = task.metadata.get("required_locks", [])
            has_lock_conflict = any(l in self._active_locks for l in task_locks)
            if not has_lock_conflict:
                schedulable.append(task)
        
        return schedulable[:self.max_concurrency]

    def acquire_locks_for_task(self, task: Task):
        for lock in task.metadata.get("required_locks", []):
            self._active_locks.add(lock)

    def release_locks_for_task(self, task: Task):
        for lock in task.metadata.get("required_locks", []):
            self._active_locks.discard(lock)

    def assign_agent(self, task: Task) -> Agent:
        if task.owner_agent_id:
            return self.registry.get(task.owner_agent_id)
        
        # Match by capabilities
        for cap in task.required_capabilities:
            matching = self.registry.find_by_capability(cap)
            if matching:
                task.owner_agent_id = matching[0].agent_id
                return matching[0]
        
        # Match by type
        by_type = self.registry.find_by_type(task.task_type)
        if by_type:
            task.owner_agent_id = by_type[0].agent_id
            return by_type[0]
        
        raise ValueError(f"No suitable agent found for task {task.task_id} with capabilities {task.required_capabilities}")
