import copy
import hashlib
import json
import time
from dataclasses import dataclass, field
from typing import Dict, Any, Optional

@dataclass
class AssetSnapshot:
    snapshot_id: str
    asset_id: str
    operation_id: str
    timestamp: float
    state_data: Dict[str, Any]
    integrity_hash: str

class SnapshotManager:
    def __init__(self):
        self.snapshots: Dict[str, AssetSnapshot] = {}

    def create_snapshot(self, asset_id: str, operation_id: str, state_data: Dict[str, Any]) -> AssetSnapshot:
        snap_id = f"snap_{asset_id}_{int(time.time()*1000)}"
        state_copy = copy.deepcopy(state_data)
        serialized = json.dumps(state_copy, sort_keys=True)
        h = hashlib.sha256(serialized.encode("utf-8")).hexdigest()

        snapshot = AssetSnapshot(
            snapshot_id=snap_id,
            asset_id=asset_id,
            operation_id=operation_id,
            timestamp=time.time(),
            state_data=state_copy,
            integrity_hash=h
        )
        self.snapshots[snap_id] = snapshot
        return snapshot

    def get_snapshot(self, snapshot_id: str) -> Optional[AssetSnapshot]:
        return self.snapshots.get(snapshot_id)
