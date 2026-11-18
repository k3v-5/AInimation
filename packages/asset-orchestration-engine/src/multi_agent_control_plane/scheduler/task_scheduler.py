from typing import Dict, Any, List, Optional
from ..core.control_types import TaskState, AgentRole
from ..core.control_schema import Task

class TaskScheduler:
    def __init__(self):
        self.queue: List[Task] = []

    def enqueue(self, task: Task):
        self.queue.append(task)
        # Ordenar por prioridad (mayor prioridad primero)
        self.queue.sort(key=lambda t: t.priority, reverse=True)

    def dequeue(self) -> Optional[Task]:
        if self.queue:
            return self.queue.pop(0)
        return None

    def get_queue_depth(self) -> int:
        return len(self.queue)
