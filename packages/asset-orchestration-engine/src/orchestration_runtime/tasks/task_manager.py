import time
from typing import Dict, List, Optional
from ..core.runtime_types import RuntimeTaskStatus, RuntimeTaskType, RuntimePriority, RuntimeEventType
from ..core.runtime_schema import Task
from .task_state_machine import TaskStateMachine
from ..events.event_bus import EventBus

class TaskQueue:
    def __init__(self, max_pending: int = 100):
        self.max_pending = max_pending
        self.queue: List[Task] = []

    def push(self, task: Task):
        if len(self.queue) >= self.max_pending:
            raise RuntimeError(f"QUEUE_BACKPRESSURE: Max pending tasks ({self.max_pending}) reached. Backpressure applied.")
        self.queue.append(task)
        # Ordenar por prioridad (CRITICAL > HIGH > NORMAL > LOW > BACKGROUND)
        prio_map = {
            RuntimePriority.CRITICAL: 0,
            RuntimePriority.HIGH: 1,
            RuntimePriority.NORMAL: 2,
            RuntimePriority.LOW: 3,
            RuntimePriority.BACKGROUND: 4
        }
        self.queue.sort(key=lambda t: prio_map.get(t.priority, 2))

    def pop_ready(self, completed_task_ids: List[str], failed_task_ids: List[str]) -> Optional[Task]:
        for i, task in enumerate(self.queue):
            # Comprobar dependencias fallidas
            if any(dep in failed_task_ids for dep in task.dependencies):
                task.status = RuntimeTaskStatus.BLOCKED
                continue

            # Comprobar si todas las dependencias requeridas están completadas
            if all(dep in completed_task_ids for dep in task.dependencies):
                return self.queue.pop(i)
        return None

class TaskManager:
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self.tasks: Dict[str, Task] = {}
        self.task_counter = 0

    def create_task(
        self,
        asset_id: str,
        task_type: RuntimeTaskType,
        parent_task_id: Optional[str] = None,
        priority: RuntimePriority = RuntimePriority.NORMAL,
        dependencies: Optional[List[str]] = None,
        inputs: Optional[Dict] = None
    ) -> Task:
        self.task_counter += 1
        task_id = f"TASK_2026_{self.task_counter:06d}"
        task = Task(
            task_id=task_id,
            asset_id=asset_id,
            type=task_type,
            parent_task_id=parent_task_id,
            priority=priority,
            status=RuntimeTaskStatus.CREATED,
            dependencies=dependencies or [],
            inputs=inputs or {}
        )
        self.tasks[task_id] = task
        self.event_bus.publish(
            RuntimeEventType.TASK_CREATED,
            task_id=task_id,
            asset_id=asset_id,
            payload={"type": task_type.value, "priority": priority.value}
        )
        return task

    def transition_task(self, task_id: str, new_status: RuntimeTaskStatus):
        if task_id not in self.tasks:
            raise KeyError(f"Task '{task_id}' not found.")
        task = self.tasks[task_id]
        TaskStateMachine.validate_transition(task.status, new_status)
        old_status = task.status
        task.status = new_status
        task.updated_at = time.time()
        self.event_bus.publish(
            RuntimeEventType.STATE_CHANGED,
            task_id=task_id,
            asset_id=task.asset_id,
            payload={"from": old_status.value, "to": new_status.value}
        )
