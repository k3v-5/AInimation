import hashlib
import json
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from .permission_manager import Permission, RiskLevel

@dataclass
class AgentContractV2:
    agent_id: str
    agent_type: str
    contract_version: str = "2.0.0"
    implementation_version: str = "1.0.0"

    input_schema: Dict[str, Any] = field(default_factory=dict)
    output_schema: Dict[str, Any] = field(default_factory=dict)

    capabilities: List[str] = field(default_factory=list)
    permissions: List[Permission] = field(default_factory=list)

    allowed_tools: List[str] = field(default_factory=list)
    forbidden_tools: List[str] = field(default_factory=list)

    allowed_resources: List[str] = field(default_factory=lambda: ["*"])
    forbidden_resources: List[str] = field(default_factory=list)

    allowed_asset_types: List[str] = field(default_factory=lambda: ["*"])
    forbidden_asset_types: List[str] = field(default_factory=list)

    allowed_operations: List[str] = field(default_factory=lambda: ["*"])
    forbidden_operations: List[str] = field(default_factory=list)

    required_context: List[str] = field(default_factory=list)
    optional_context: List[str] = field(default_factory=list)

    side_effects: List[str] = field(default_factory=list)

    read_scope: List[str] = field(default_factory=lambda: ["*"])
    write_scope: List[str] = field(default_factory=list)

    max_execution_time: float = 60.0
    max_retries: int = 3
    max_concurrency: int = 2

    failure_policy: str = "RETRY"
    rollback_policy: str = "AUTO"
    validation_policy: str = "STRICT"
    audit_policy: str = "FULL"
    
    contract_hash: str = ""

    def __post_init__(self):
        if not self.contract_hash:
            self.contract_hash = self.compute_hash()

    def compute_hash(self) -> str:
        data = {
            "agent_id": self.agent_id,
            "agent_type": self.agent_type,
            "contract_version": self.contract_version,
            "capabilities": sorted(self.capabilities),
            "permissions": sorted([p.value for p in self.permissions]),
            "allowed_tools": sorted(self.allowed_tools),
            "forbidden_tools": sorted(self.forbidden_tools),
            "allowed_resources": sorted(self.allowed_resources),
            "forbidden_resources": sorted(self.forbidden_resources),
            "allowed_operations": sorted(self.allowed_operations),
            "forbidden_operations": sorted(self.forbidden_operations),
            "write_scope": sorted(self.write_scope),
            "max_execution_time": self.max_execution_time,
            "max_retries": self.max_retries
        }
        raw = json.dumps(data, sort_keys=True)
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    def verify_integrity(self) -> bool:
        return self.compute_hash() == self.contract_hash

    def validate_tool_access(self, tool_name: str) -> bool:
        if tool_name in self.forbidden_tools:
            return False
        if not self.allowed_tools:
            return True
        return tool_name in self.allowed_tools or "*" in self.allowed_tools

    def has_permission(self, permission: Permission) -> bool:
        return permission in self.permissions
