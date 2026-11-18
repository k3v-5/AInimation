from typing import Dict, Any, Optional
from ..core.scene_graph import SceneGraph

class SnapshotManager:
    def __init__(self):
        self.snapshots: Dict[str, Dict[str, Any]] = {}

    def capture_snapshot(self, asset_id: str, version: int, graph: SceneGraph):
        key = f"{asset_id}_v{version}"
        self.snapshots[key] = graph.to_dict()

    def restore_snapshot(self, asset_id: str, version: int) -> Optional[SceneGraph]:
        key = f"{asset_id}_v{version}"
        data = self.snapshots.get(key)
        if data:
            return SceneGraph.from_dict(data)
        return None
