import time
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from .agent_types import (
    ToolCategory, PermissionLevel, AgentOperationStatus,
    AgentDecision, AgentAssetStatus, AgentComponentStatus, AgentErrorCode
)

@dataclass
class ToolDefinition:
    name: str
    category: ToolCategory
    permission_level: PermissionLevel = PermissionLevel.READ
    description: str = ""
    parameters_schema: Dict[str, Any] = field(default_factory=dict)

@dataclass
class AgentToolResponse:
    status: AgentOperationStatus
    operation_id: str
    summary: str
    affected_assets: List[str] = field(default_factory=list)
    affected_components: List[str] = field(default_factory=list)
    validation: Dict[str, Any] = field(default_factory=dict)
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    next_action: AgentDecision = AgentDecision.ACCEPT
    output_data: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)

@dataclass
class AgentPlan:
    plan_id: str
    plan_hash: str
    expected_state_hash: str
    operations: List[Dict[str, Any]] = field(default_factory=list)
    estimated_mcp_calls: int = 1
    estimated_duration: float = 0.5
    risk: str = "LOW"

@dataclass
class AgentAssetContext:
    asset_id: str
    asset_type: str
    version: int = 1
    status: AgentAssetStatus = AgentAssetStatus.VALID
    parameters: Dict[str, Any] = field(default_factory=dict)
    components: Dict[str, AgentComponentStatus] = field(default_factory=dict)
    validation_summary: Dict[str, Any] = field(default_factory=dict)

@dataclass
class AgentDiagnostic:
    code: str
    severity: str
    location: str
    measured: Any
    target: Any
    confidence: float
    candidate_parameters: List[str] = field(default_factory=list)

@dataclass
class AgentCorrectionItem:
    parameter: str
    old_value: Any
    proposed_value: Any
    reason: str
    confidence: float = 0.90
    affected_components: List[str] = field(default_factory=list)

@dataclass
class AgentTaskBudget:
    max_mcp_calls: int = 10
    remaining_calls: int = 10
    max_iterations: int = 5
    current_iteration: int = 0
