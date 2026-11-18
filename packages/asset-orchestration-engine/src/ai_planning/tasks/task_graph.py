from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional

class TaskStatus(str, Enum):
    PENDING = "PENDING"
    READY = "READY"
    RUNNING = "RUNNING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    ROLLED_BACK = "ROLLED_BACK"

@dataclass
class PlannedTask:
    task_id: str
    task_type: str
    target: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)
    status: TaskStatus = TaskStatus.PENDING
    attempts: int = 0

class TaskGraph:
    def __init__(self):
        self.tasks: Dict[str, PlannedTask] = {} # task_id -> PlannedTask

    def add_task(self, task: PlannedTask):
        self.tasks[task.task_id] = task

    def get_ready_tasks(self) -> List[PlannedTask]:
        ready = []
        for t in self.tasks.values():
            if t.status == TaskStatus.PENDING:
                # Comprobar si todas las dependencias fueron SUCCESS
                deps_met = True
                for dep_id in t.dependencies:
                    dep_task = self.tasks.get(dep_id)
                    if not dep_task or dep_task.status != TaskStatus.SUCCESS:
                        deps_met = False
                        break
                if deps_met:
                    ready.append(t)
        return ready

    def list_tasks(self) -> List[PlannedTask]:
        return list(self.tasks.values())
