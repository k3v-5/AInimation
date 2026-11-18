from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set
from ..core.permission_manager import ResourceClassification

@dataclass
class ResourceScope:
    resource_id: str
    classification: ResourceClassification
    allowed_agents: List[str] = field(default_factory=lambda: ["*"])
    owner_agent_id: Optional[str] = None
    active_task_id: Optional[str] = None

class ResourceManager:
    """Manages resource ownership, scopes and project protection."""
    def __init__(self):
        self._resources: Dict[str, ResourceScope] = {}
        self._init_project_resources()

    def _init_project_resources(self):
        # Default classifications
        self.register_resource("Art/Blender/DarX_Assets.blend", ResourceClassification.PROTECTED)
        self.register_resource("Art/", ResourceClassification.PROTECTED)
        self.register_resource("Source/", ResourceClassification.PROTECTED)
        self.register_resource("AOE_Generated", ResourceClassification.GENERATED)
        self.register_resource("TemporaryWorkspace", ResourceClassification.TEMPORARY)

    def register_resource(self, resource_id: str, classification: ResourceClassification):
        self._resources[resource_id] = ResourceScope(resource_id=resource_id, classification=classification)

    def get_scope(self, resource_id: str) -> ResourceScope:
        if resource_id in self._resources:
            return self._resources[resource_id]
        # Default fallback classification
        if resource_id.startswith("AOE_Generated") or resource_id.startswith("WP_"):
            return ResourceScope(resource_id=resource_id, classification=ResourceClassification.GENERATED)
        return ResourceScope(resource_id=resource_id, classification=ResourceClassification.PROTECTED)

    def acquire_ownership(self, resource_id: str, agent_id: str, task_id: str) -> bool:
        scope = self.get_scope(resource_id)
        if scope.owner_agent_id and scope.owner_agent_id != agent_id:
            return False
        scope.owner_agent_id = agent_id
        scope.active_task_id = task_id
        self._resources[resource_id] = scope
        return True

    def release_ownership(self, resource_id: str, agent_id: str):
        if resource_id in self._resources:
            if self._resources[resource_id].owner_agent_id == agent_id:
                self._resources[resource_id].owner_agent_id = None
                self._resources[resource_id].active_task_id = None
