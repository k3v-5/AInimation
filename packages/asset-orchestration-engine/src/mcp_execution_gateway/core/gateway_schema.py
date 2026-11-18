import time
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from .gateway_types import (
    CommandType, RiskLevel, GatewayState, ExecutionStatus,
    DriftType, ReconciliationMode, GatewayErrorType
)

@dataclass
class GatewayCommand:
    command_id: str
    operation_id: str
    type: CommandType
    target: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    preconditions: Dict[str, Any] = field(default_factory=dict)
    postconditions: Dict[str, Any] = field(default_factory=dict)
    timeout_seconds: float = 5.0
    idempotency_key: Optional[str] = None
    risk_level: RiskLevel = RiskLevel.LOW
    expected_scene_version: Optional[int] = None

@dataclass
class ObjectStateRecord:
    object_id: str
    name: str
    type: str = "MESH"
    transform: Dict[str, Any] = field(default_factory=lambda: {"loc": [0,0,0], "rot": [0,0,0], "scale": [1,1,1]})
    material_ids: List[str] = field(default_factory=list)
    owner_asset: Optional[str] = None

@dataclass
class SceneStateSnapshot:
    scene_version: int = 1
    objects: Dict[str, ObjectStateRecord] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)

@dataclass
class TransactionRecord:
    transaction_id: str
    operation_id: str
    created_objects: List[str] = field(default_factory=list)
    snapshot_before: Optional[SceneStateSnapshot] = None
    committed: bool = False

@dataclass
class VerificationResult:
    verified: bool
    expected_objects_present: bool
    details: str = ""

@dataclass
class ExecutionResult:
    execution_id: str
    command_id: str
    status: ExecutionStatus
    mcp_calls_made: int = 1
    output: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None

@dataclass
class CommandPlan:
    plan_id: str
    commands: List[GatewayCommand] = field(default_factory=list)
    estimated_mcp_calls: int = 0
    estimated_duration: float = 0.5
    overall_risk: RiskLevel = RiskLevel.LOW

@dataclass
class GatewayPolicy:
    max_mcp_calls_per_operation: int = 10
    max_same_command_retries: int = 3
    allow_destructive: bool = False
