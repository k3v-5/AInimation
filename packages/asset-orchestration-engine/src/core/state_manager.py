from typing import Dict, Optional, Any
from .scene_graph import SceneGraph
from ..specification.asset_schema import AssetSpecification, AssetStatus

class StateManager:
    def __init__(self):
        self.active_specifications: Dict[str, AssetSpecification] = {}
        self.active_scene_graphs: Dict[str, SceneGraph] = {}
        self.asset_statuses: Dict[str, AssetStatus] = {}
        self.component_locks: Dict[str, str] = {}

    def register_asset(self, spec: AssetSpecification, graph: SceneGraph):
        self.active_specifications[spec.asset_id] = spec
        self.active_scene_graphs[spec.asset_id] = graph
        self.asset_statuses[spec.asset_id] = AssetStatus.DRAFT

    def get_spec(self, asset_id: str) -> Optional[AssetSpecification]:
        return self.active_specifications.get(asset_id)

    def get_graph(self, asset_id: str) -> Optional[SceneGraph]:
        return self.active_scene_graphs.get(asset_id)

    def get_status(self, asset_id: str) -> AssetStatus:
        return self.asset_statuses.get(asset_id, AssetStatus.FAILED)

    def set_status(self, asset_id: str, status: AssetStatus):
        self.asset_statuses[asset_id] = status

    def acquire_lock(self, component_id: str, task_id: str) -> bool:
        if component_id in self.component_locks:
            return self.component_locks[component_id] == task_id
        self.component_locks[component_id] = task_id
        return True

    def release_lock(self, component_id: str, task_id: str) -> bool:
        if self.component_locks.get(component_id) == task_id:
            del self.component_locks[component_id]
            return True
        return False
