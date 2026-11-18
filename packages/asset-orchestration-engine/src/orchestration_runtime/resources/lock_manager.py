import time
from typing import Dict, List, Optional
from ..core.runtime_types import RuntimeLockType, RuntimeEventType
from ..core.runtime_schema import LockLease
from ..events.event_bus import EventBus

class LockManager:
    def __init__(self, event_bus: Optional[EventBus] = None):
        self.event_bus = event_bus
        self.locks: Dict[str, LockLease] = {} # resource_id -> LockLease
        self.wait_graph: Dict[str, str] = {}  # task_id -> waiting_for_task_id

    def acquire_lock(self, resource_id: str, task_id: str, lock_type: RuntimeLockType = RuntimeLockType.EXCLUSIVE, lease_seconds: float = 30.0) -> LockLease:
        now = time.time()
        # Limpiar locks expirados
        if resource_id in self.locks:
            current = self.locks[resource_id]
            if current.expires_at <= now:
                del self.locks[resource_id]

        if resource_id in self.locks:
            current = self.locks[resource_id]
            if current.task_id != task_id:
                # Comprobar deadlock
                self.wait_graph[task_id] = current.task_id
                if self._detect_cycle(task_id):
                    del self.wait_graph[task_id]
                    raise RuntimeError(f"DEADLOCK_DETECTED: Task '{task_id}' and '{current.task_id}' are in circular lock dependency.")

                raise RuntimeError(f"LOCK_CONFLICT: Resource '{resource_id}' is locked by task '{current.task_id}'.")

        lease = LockLease(
            lock_id=f"LOCK_{int(now*1000)}",
            resource_id=resource_id,
            task_id=task_id,
            lock_type=lock_type,
            acquired_at=now,
            expires_at=now + lease_seconds
        )
        self.locks[resource_id] = lease
        if task_id in self.wait_graph:
            del self.wait_graph[task_id]

        if self.event_bus:
            self.event_bus.publish(RuntimeEventType.LOCK_ACQUIRED, task_id=task_id, asset_id=resource_id, payload={"lock_id": lease.lock_id})
        return lease

    def release_lock(self, resource_id: str, task_id: str):
        if resource_id in self.locks:
            current = self.locks[resource_id]
            if current.task_id == task_id:
                del self.locks[resource_id]
                if self.event_bus:
                    self.event_bus.publish(RuntimeEventType.LOCK_RELEASED, task_id=task_id, asset_id=resource_id, payload={"lock_id": current.lock_id})

    def _detect_cycle(self, start_task: str) -> bool:
        visited = set()
        curr = start_task
        while curr in self.wait_graph:
            if curr in visited:
                return True
            visited.add(curr)
            curr = self.wait_graph[curr]
        return False
