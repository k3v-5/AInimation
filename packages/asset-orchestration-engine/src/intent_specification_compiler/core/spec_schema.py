import hashlib
import json
import time
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from .spec_types import ConstraintType, ValueType, UnitType, SpecStatus, ApprovalState, RequirementStatus

@dataclass
class RequirementEntry:
    req_id: str
    description: str
    constraint_type: ConstraintType = ConstraintType.HARD
    status: RequirementStatus = RequirementStatus.NOT_IMPLEMENTED
    affects: List[str] = field(default_factory=list) # ["door", "collision", "navigation"]

@dataclass
class AssumptionEntry:
    assumption_id: str
    description: str
    source: str = "PROJECT_DEFAULT"
    confidence: str = "HIGH" # LOW, MEDIUM, HIGH
    impact: str = "LOW" # LOW, MEDIUM, HIGH

@dataclass
class StyleSpec:
    period: str = "MEDIEVAL"
    architecture: str = "MEDIEVAL_RURAL"
    condition: str = "AGED"
    forbidden_styles: List[str] = field(default_factory=lambda: ["FANTASY"])

@dataclass
class VisualIntent:
    silhouette: str = "RURAL_COTTAGE"
    lean_angle_deg: float = 2.5 # Ligeramente inclinada
    scale: str = "SMALL"

@dataclass
class DoorSpec:
    required: bool = True
    material: str = "WOOD"
    width_m: float = 0.90
    height_m: float = 2.10
    player_passable: bool = True

@dataclass
class WindowSpec:
    count: int = 2
    style: str = "NARROW"

@dataclass
class StairSpec:
    required: bool = True
    location: str = "INTERNAL"
    destination: str = "SECOND_FLOOR"

@dataclass
class SpecBudget:
    max_triangles: int = 40000
    max_materials: int = 5

@dataclass
class AssetSpec:
    spec_id: str
    spec_version: str = "1.0.0"
    asset_type: str = "HOUSE"
    style: StyleSpec = field(default_factory=StyleSpec)
    visual: VisualIntent = field(default_factory=VisualIntent)
    door: DoorSpec = field(default_factory=DoorSpec)
    windows: WindowSpec = field(default_factory=WindowSpec)
    stairs: StairSpec = field(default_factory=StairSpec)
    budget: SpecBudget = field(default_factory=SpecBudget)
    requirements: List[RequirementEntry] = field(default_factory=list)
    assumptions: List[AssumptionEntry] = field(default_factory=list)
    status: SpecStatus = SpecStatus.DRAFT
    approval: ApprovalState = ApprovalState.PENDING
    created_at: float = field(default_factory=time.time)

    def compute_spec_hash(self) -> str:
        payload = {
            "spec_id": self.spec_id,
            "version": self.spec_version,
            "type": self.asset_type,
            "style": self.style.architecture,
            "condition": self.style.condition,
            "door_w": self.door.width_m,
            "windows": self.windows.count,
            "stairs": self.stairs.required,
            "lean": self.visual.lean_angle_deg
        }
        serialized = json.dumps(payload, sort_keys=True)
        return hashlib.sha256(serialized.encode("utf-8")).hexdigest()[:16]

AISpec = AssetSpec

@dataclass
class SpecDiffResult:
    spec_id: str
    old_version: str
    new_version: str
    modified_fields: Dict[str, Tuple[Any, Any]] = field(default_factory=dict)
    affected_subtrees: List[str] = field(default_factory=list)

@dataclass
class ImpactAnalysisResult:
    affected_components: List[str]
    unaffected_components: List[str]
    rebuild_scope: str # SUBTREE vs FULL_ASSET
