import time
from typing import Dict, Any, List, Optional
from ..core.context_models import ContextSnapshot
from ...memory.core.exceptions import MemoryError

class ContextSnapshotService:
    """Creates, persists and restores immutable ContextSnapshots (F70 / F73 integration)."""
    def __init__(self):
        self._snapshots: Dict[str, ContextSnapshot] = {}

    def create_snapshot(
        self,
        snapshot_id: str,
        context_data: Dict[str, Any],
        parent_snapshot_id: Optional[str] = None,
        version: int = 1
    ) -> ContextSnapshot:
        snap = ContextSnapshot(
            snapshot_id=snapshot_id,
            version=version,
            parent_snapshot_id=parent_snapshot_id,
            context_data=context_data
        )
        self._snapshots[snapshot_id] = snap
        return snap

    def get_snapshot(self, snapshot_id: str) -> Optional[ContextSnapshot]:
        return self._snapshots.get(snapshot_id)

    def restore_snapshot(self, snapshot_id: str) -> Dict[str, Any]:
        snap = self._snapshots.get(snapshot_id)
        if not snap:
            raise MemoryError(f"ContextSnapshot {snapshot_id} not found.")
        if not snap.verify_integrity():
            raise MemoryError(f"ContextSnapshot {snapshot_id} failed cryptographic integrity verification.")
        return dict(snap.context_data)
