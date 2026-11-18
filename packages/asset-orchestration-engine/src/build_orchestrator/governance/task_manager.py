import time
from typing import Dict, Any, List, Optional, Set
from ..core.orchestrator_types import TaskState, LockType
from ..core.orchestrator_schema import Task

class TaskManager:
    def __init__(self):
        self.tasks: Dict[str, Task] = {}
        self.dependencies: Dict[str, List[str]] = {} # child_task_id -> [parent_task_ids]

    def create_task(
        self,
        task_id: str,
        task_type: str,
        target_asset_id: str,
        parameters: Dict[str, Any] = None,
        parent_task_id: Optional[str] = None
    ) -> Task:
        task = Task(
            task_id=task_id,
            task_type=task_type,
            target_asset_id=target_asset_id,
            parent_task_id=parent_task_id,
            parameters=parameters or {}
        )
        self.tasks[task_id] = task
        return task

    def add_dependency(self, child_task_id: str, parent_task_id: str):
        if child_task_id not in self.dependencies:
            self.dependencies[child_task_id] = []
        self.dependencies[child_task_id].append(parent_task_id)

    def can_execute_task(self, task_id: str) -> bool:
        task = self.tasks.get(task_id)
        if not task or task.state in [TaskState.COMPLETED, TaskState.CANCELLED]:
            return False

        # Verificar que todos los padres estén COMPLETED o PASSED
        parents = self.dependencies.get(task_id, [])
        for p_id in parents:
            p_task = self.tasks.get(p_id)
            if not p_task or p_task.state not in [TaskState.COMPLETED, TaskState.PASSED]:
                return False
        return True

    def transition_state(self, task_id: str, new_state: TaskState):
        if task_id in self.tasks:
            self.tasks[task_id].state = new_state
            self.tasks[task_id].updated_at = time.time()

class AssetLockManager:
    def __init__(self):
        self.locks: Dict[str, Tuple[str, LockType, float]] = {} # asset_id -> (agent_id, lock_type, expiry)

    def acquire_lock(self, asset_id: str, agent_id: str, lock_type: LockType = LockType.WRITE, timeout_sec: float = 30.0) -> bool:
        now = time.time()
        if asset_id in self.locks:
            owner, l_type, expiry = self.locks[asset_id]
            if now < expiry and owner != agent_id:
                if l_type == LockType.EXCLUSIVE or lock_type == LockType.EXCLUSIVE:
                    return False
        self.locks[asset_id] = (agent_id, lock_type, now + timeout_sec)
        return True

    def release_lock(self, asset_id: str, agent_id: str) -> bool:
        if asset_id in self.locks:
            owner, _, _ = self.locks[asset_id]
            if owner == agent_id:
                del self.locks[asset_id]
                return True
        return False
