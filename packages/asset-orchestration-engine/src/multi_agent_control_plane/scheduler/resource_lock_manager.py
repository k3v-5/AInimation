import time
from typing import Dict, Any, List, Optional
from ..core.control_types import LockType
from ..core.control_schema import ResourceLock

class ResourceLockManager:
    def __init__(self):
        self._locks: Dict[str, ResourceLock] = {}

    def acquire_lock(self, lock_type: LockType, resource_id: str, owner_task_id: str) -> ResourceLock:
        key = f"{lock_type.value}_{resource_id}"
        if key in self._locks:
            existing = self._locks[key]
            # Si el lock ha expirado, liberarlo
            if time.time() - existing.acquired_at > existing.timeout_sec:
                self.release_lock(lock_type, resource_id, existing.owner_task_id)
            elif existing.owner_task_id != owner_task_id:
                raise BlockingIOError(f"RESOURCE_LOCKED: Resource '{resource_id}' ({lock_type.value}) is already locked by task '{existing.owner_task_id}'. Access serialized.")

        lock = ResourceLock(
            lock_id=f"LOCK_{int(time.time()*1000)}",
            lock_type=lock_type,
            resource_id=resource_id,
            owner_task_id=owner_task_id,
            acquired_at=time.time()
        )
        self._locks[key] = lock
        return lock

    def release_lock(self, lock_type: LockType, resource_id: str, owner_task_id: str) -> bool:
        key = f"{lock_type.value}_{resource_id}"
        if key in self._locks:
            if self._locks[key].owner_task_id == owner_task_id:
                del self._locks[key]
                return True
        return False

    def is_locked(self, lock_type: LockType, resource_id: str) -> bool:
        key = f"{lock_type.value}_{resource_id}"
        return key in self._locks
