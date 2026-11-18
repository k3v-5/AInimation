import time
import hashlib
import json
from typing import Dict, Any, Optional
from ..core.correction_schema import AssetSnapshot

class SnapshotManager:
    @classmethod
    def create_snapshot(
        cls,
        asset_id: str,
        iteration_id: int,
        parameters: Dict[str, Any],
        geometry_state: Dict[str, Any],
        material_state: Optional[Dict[str, Any]] = None
    ) -> AssetSnapshot:
        m_state = material_state or {}
        raw = {
            "asset_id": asset_id,
            "iteration_id": iteration_id,
            "params": parameters,
            "geom": geometry_state,
            "mat": m_state
        }
        h = hashlib.sha256(json.dumps(raw, sort_keys=True, default=str).encode("utf-8")).hexdigest()
        
        return AssetSnapshot(
            snapshot_id=f"SNAP_{asset_id}_{iteration_id}_{int(time.time()*1000)%100000}",
            asset_id=asset_id,
            iteration_id=iteration_id,
            timestamp=time.time(),
            state_hash=h,
            parameters=dict(parameters),
            transforms={},
            geometry_state=dict(geometry_state),
            material_state=dict(m_state)
        )
