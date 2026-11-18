import copy
import time
from typing import Dict, Any, List, Set, Optional
from ..core.gateway_types import DriftType
from ..core.gateway_schema import ObjectStateRecord, SceneStateSnapshot

class SceneStateTracker:
    def __init__(self):
        self.scene_version: int = 1
        self.objects: Dict[str, ObjectStateRecord] = {}

    def get_snapshot(self) -> SceneStateSnapshot:
        return SceneStateSnapshot(
            scene_version=self.scene_version,
            objects=copy.deepcopy(self.objects),
            timestamp=time.time()
        )

    def validate_optimistic_concurrency(self, expected_version: Optional[int]):
        if expected_version is not None and expected_version != self.scene_version:
            raise RuntimeError(f"STATE_CONFLICT: Expected scene version {expected_version} but current scene version is {self.scene_version}. Refresh required.")

    def register_object(self, obj_id: str, name: str, owner_asset: str = None) -> ObjectStateRecord:
        record = ObjectStateRecord(object_id=obj_id, name=name, owner_asset=owner_asset)
        self.objects[obj_id] = record
        self.scene_version += 1
        return record

    def unregister_object(self, obj_id: str):
        if obj_id in self.objects:
            del self.objects[obj_id]
            self.scene_version += 1

    def detect_drift(self, actual_scene_objects: Set[str]) -> Optional[str]:
        expected = set(self.objects.keys())
        if expected != actual_scene_objects:
            diff_extra = actual_scene_objects - expected
            diff_missing = expected - actual_scene_objects
            return f"DRIFT_DETECTED: Scene has {len(diff_missing)} missing and {len(diff_extra)} extra objects compared to state tracker."
        return None

class LockController:
    def __init__(self):
        self.active_locks: Set[str] = set()

    def acquire_lock(self, resource_id: str):
        if resource_id in self.active_locks:
            raise RuntimeError(f"LOCK_CONFLICT: Resource '{resource_id}' is currently locked by another operation.")
        self.active_locks.add(resource_id)

    def release_lock(self, resource_id: str):
        self.active_locks.discard(resource_id)
