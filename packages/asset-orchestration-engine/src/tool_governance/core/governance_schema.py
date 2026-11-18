import time
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from .governance_status import ToolRisk, PermissionType, ActionScope, ActionLifecycle

@dataclass
class ToolDefinition:
    tool_id: str
    name: str
    risk_level: ToolRisk
    required_permission: PermissionType
    cost: int = 1

@dataclass
class ActionProposal:
    proposal_id: str
    task_id: str
    action_name: str # modify_asset, rebuild_asset, delete_asset
    target_entity: str # house_003
    scope: ActionScope = ActionScope.PARAMETER
    parameters: Dict[str, Any] = field(default_factory=dict)
    reason: str = ""
    evidence_id: Optional[str] = None
    confidence: float = 0.95

@dataclass
class ExecutionBudget:
    max_tool_calls: int = 30
    max_asset_rebuilds: int = 3
    max_scene_rebuilds: int = 0
    used_tool_calls: int = 0
    used_asset_rebuilds: int = 0
    used_scene_rebuilds: int = 0

    def can_consume_tool_call(self) -> bool:
        return self.used_tool_calls < self.max_tool_calls

    def can_consume_rebuild(self) -> bool:
        return self.used_asset_rebuilds < self.max_asset_rebuilds

    def consume_tool_call(self):
        self.used_tool_calls += 1

    def consume_rebuild(self):
        self.used_asset_rebuilds += 1

@dataclass
class NormalizedToolResult:
    tool_call_id: str
    status: ActionLifecycle
    target_entity: str
    modified_parameters: Dict[str, Any] = field(default_factory=dict)
    verification_passed: bool = True
    message: str = ""

@dataclass
class StateSnapshot:
    snapshot_id: str
    timestamp: float = field(default_factory=time.time)
    assets_data: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ExecutionReport:
    task_id: str
    status: str
    total_proposals: int
    executed_actions: int
    rejected_actions: int
    rolled_back_actions: int
    budget_used: Dict[str, int] = field(default_factory=dict)
    logs: List[str] = field(default_factory=list)
