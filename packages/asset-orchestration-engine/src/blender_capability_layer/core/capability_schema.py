from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from .capability_types import (
    OperationStatus, CapabilityCategory, ErrorTaxonomy,
    ErrorSeverity, CircuitState, LockScope, PermissionLevel
)

@dataclass
class CapabilityContract:
    capability_id: str
    category: CapabilityCategory
    version: str = "v1"
    required_parameters: List[str] = field(default_factory=list)
    idempotency_support: bool = True
    rollback_support: bool = True

@dataclass
class OperationRequest:
    operation_id: str
    capability_id: str
    parameters: Dict[str, Any]
    asset_id: str = "GLOBAL"
    idempotency_key: Optional[str] = None
    timeout_sec: float = 30.0
    is_dry_run: bool = False

@dataclass
class OperationResponse:
    operation_id: str
    status: OperationStatus
    result: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    duration_ms: float = 0.0
    adapter_name: str = "AhujasidBlenderAdapter"

@dataclass
class BlenderObjectState:
    object_id: str
    semantic_id: str
    name: str
    type_name: str = "MESH"
    transform: Dict[str, Any] = field(default_factory=lambda: {"location": (0,0,0), "rotation": (0,0,0), "scale": (1,1,1)})
    materials: List[str] = field(default_factory=list)
    modifiers: List[str] = field(default_factory=list)
    custom_metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class BlenderSceneState:
    scene_id: str
    revision: int = 1
    objects: Dict[str, BlenderObjectState] = field(default_factory=dict)
    collections: List[str] = field(default_factory=lambda: ["AI_GENERATED"])
    materials: List[str] = field(default_factory=list)

@dataclass
class TransactionRecord:
    transaction_id: str
    operations: List[OperationRequest] = field(default_factory=list)
    compensations: List[OperationRequest] = field(default_factory=list)
    status: str = "OPEN"

@dataclass
class HealthReport:
    status: str
    circuit_state: CircuitState
    latency_ms: float
    error_rate: float
