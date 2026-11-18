from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from .agent_state import AgentPermission, FailureAction

@dataclass
class AgentContract:
    agent_id: str
    version: str = "1.0.0"
    capabilities: List[str] = field(default_factory=list)
    permissions: List[AgentPermission] = field(default_factory=list)
    required_context: List[str] = field(default_factory=list)
    produces: List[str] = field(default_factory=list)
    consumes: List[str] = field(default_factory=list)
    allowed_tools: List[str] = field(default_factory=list)
    forbidden_tools: List[str] = field(default_factory=list)
    timeout_sec: float = 60.0
    failure_policy: FailureAction = FailureAction.RETRY

    def validate_tool_access(self, tool_name: str) -> bool:
        if tool_name in self.forbidden_tools:
            return False
        if not self.allowed_tools: # wildcard if empty
            return True
        return tool_name in self.allowed_tools or "*" in self.allowed_tools

    def has_permission(self, permission: AgentPermission) -> bool:
        return permission in self.permissions
