import time
from dataclasses import dataclass, field
from typing import Dict, Any, Optional

@dataclass
class PolicySnapshot:
    snapshot_id: str
    created_at: float = field(default_factory=time.time)
    policy_version: str = "2.0.0"
    contract_versions: Dict[str, str] = field(default_factory=dict)
    tool_registry_version: str = "1.0.0"
    capability_registry_version: str = "1.0.0"
    emergency_stop_active: bool = False

class EmergencyStopController:
    """Administrative switch capable of halting all mutating operations project-wide."""
    def __init__(self):
        self._emergency_stop: bool = False
        self._reason: str = ""

    def activate(self, reason: str = "ADMIN_EMERGENCY_HALT"):
        self._emergency_stop = True
        self._reason = reason

    def deactivate(self):
        self._emergency_stop = False
        self._reason = ""

    @property
    def is_active(self) -> bool:
        return self._emergency_stop

    @property
    def reason(self) -> str:
        return self._reason
