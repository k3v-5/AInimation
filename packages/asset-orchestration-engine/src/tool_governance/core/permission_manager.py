from typing import Set, Dict
from .governance_status import PermissionType

class AgentPermissionProfile:
    def __init__(self, agent_id: str, permissions: Set[PermissionType]):
        self.agent_id = agent_id
        self.permissions = set(permissions)

    def has_permission(self, perm: PermissionType) -> bool:
        return perm in self.permissions

class PermissionManager:
    def __init__(self):
        self.profiles: Dict[str, AgentPermissionProfile] = {}
        self._init_defaults()

    def register_profile(self, profile: AgentPermissionProfile):
        self.profiles[profile.agent_id] = profile

    def is_authorized(self, agent_id: str, permission: PermissionType) -> bool:
        profile = self.profiles.get(agent_id)
        if not profile:
            return False
        return profile.has_permission(permission)

    def _init_defaults(self):
        # Perfil estándar de diseñador
        self.register_profile(AgentPermissionProfile(
            "designer_agent",
            {
                PermissionType.READ_SCENE,
                PermissionType.CREATE_ASSET,
                PermissionType.MODIFY_ASSET,
                PermissionType.MODIFY_MATERIAL,
                PermissionType.REBUILD_ASSET
            }
        ))
        # Perfil de sólo lectura
        self.register_profile(AgentPermissionProfile(
            "inspector_agent",
            {PermissionType.READ_SCENE}
        ))
