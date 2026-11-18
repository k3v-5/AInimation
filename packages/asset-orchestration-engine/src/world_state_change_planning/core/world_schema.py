import hashlib
import json
import time
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Tuple
from .world_types import (
    WorldAssetStatus, WorldChangeType, WorldChangeScope, WorldConstraintType,
    ReconciliationState, ContextLevel, TransactionStatus
)

@dataclass
class ComponentMetadata:
    semantic_id: str
    asset_id: str
    component_type: str
    builder_owner: str = "ProceduralBuilder"
    dependencies: List[str] = field(default_factory=list)

@dataclass
class AssetState:
    asset_id: str
    asset_type: str = "HOUSE"
    version: int = 1
    status: WorldAssetStatus = WorldAssetStatus.VALID
    transform: Dict[str, float] = field(default_factory=lambda: {"x": 0.0, "y": 0.0, "z": 0.0})
    bounds: Dict[str, float] = field(default_factory=lambda: {"w": 4.5, "d": 4.0, "h": 4.6})
    spec_hash: str = ""
    geometry_hash: str = ""
    parameters: Dict[str, Any] = field(default_factory=dict)
    components: List[str] = field(default_factory=list)
    locked_properties: List[str] = field(default_factory=list) # e.g. ["roof.shape"]

    def compute_state_hash(self) -> str:
        payload = {
            "asset_id": self.asset_id,
            "version": self.version,
            "params": self.parameters,
            "geo_hash": self.geometry_hash,
            "status": self.status.value
        }
        serialized = json.dumps(payload, sort_keys=True)
        return hashlib.sha256(serialized.encode("utf-8")).hexdigest()[:16]

WorldAssetState = AssetState

@dataclass
class ProjectState:
    project_id: str = "DARX_WORLD"
    project_version: str = "1.0.0"
    schema_version: str = "v33.0"
    default_grid: float = 0.25

@dataclass
class WorldState:
    project: ProjectState = field(default_factory=ProjectState)
    assets: Dict[str, AssetState] = field(default_factory=dict)
    active_selection: Optional[str] = None

@dataclass
class ChangeRequest:
    target_asset_id: Optional[str]
    operation: WorldChangeType
    property_path: str
    new_value: Any
    scope: WorldChangeScope = WorldChangeScope.PROPERTY

@dataclass
class ChangePlan:
    plan_id: str
    target_asset_id: str
    requested_changes: List[str]
    affected_components: List[str]
    unaffected_components: List[str]
    complexity_score: int = 15 # 0-20 trivial, 21-50 simple, 51-100 complex
    is_approved: bool = True
    plan_hash: str = ""

@dataclass
class DryRunResult:
    change_plan: ChangePlan
    what_will_change: List[str]
    what_will_not_change: List[str]
    warnings: List[str]
    estimated_cost_ms: float
    status: str = "PASS"

@dataclass
class SceneSnapshot:
    snapshot_id: str
    timestamp: float = field(default_factory=time.time)
    assets_state: Dict[str, AssetState] = field(default_factory=dict)

@dataclass
class TransactionRecord:
    transaction_id: str
    request: ChangeRequest
    plan: ChangePlan
    pre_state: SceneSnapshot
    post_state: Optional[SceneSnapshot] = None
    status: TransactionStatus = TransactionStatus.BEGIN
    created_at: float = field(default_factory=time.time)
