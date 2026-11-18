from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Tuple
from .guardrail_types import (
    GuardrailSeverity, SkeletalDiscrepancyType,
    SpatialViolationType, CoplanarConflictType, RemediationStrategy
)

@dataclass
class BoneNode:
    name: str
    parent: Optional[str] = None
    head: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    tail: Tuple[float, float, float] = (0.0, 0.0, 1.0)
    roll: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class SkeletalHierarchySpec:
    skeleton_id: str
    bones: Dict[str, BoneNode] = field(default_factory=dict)
    root_bone: str = "root"

    def add_bone(self, bone: BoneNode) -> None:
        self.bones[bone.name] = bone

    def has_bone(self, name: str) -> bool:
        return name in self.bones

    def get_bone_names(self) -> List[str]:
        return list(self.bones.keys())

@dataclass
class SkeletalDiscrepancy:
    discrepancy_type: SkeletalDiscrepancyType
    bone_name: str
    source: str
    message: str
    expected_parent: Optional[str] = None
    suggested_remediation: RemediationStrategy = RemediationStrategy.AUTO_SYNTHESIZE

@dataclass
class SkeletalReconciliationResult:
    is_valid: bool
    discrepancies: List[SkeletalDiscrepancy] = field(default_factory=list)
    reconciled_skeleton: Optional[SkeletalHierarchySpec] = None
    mutations_applied: List[str] = field(default_factory=list)
    auto_save_required: bool = False

@dataclass
class EntitySpatialSpec:
    entity_id: str
    position: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    rotation: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    capsule_radius: float = 40.0
    capsule_half_height: float = 96.0
    mesh_bottom_offset_z: float = -96.0
    mesh_height: float = 192.0
    is_grounded: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class SpatialClearanceViolation:
    violation_type: SpatialViolationType
    entity_a_id: str
    entity_b_id: Optional[str] = None
    overlap_distance: float = 0.0
    message: str = ""
    suggested_remediation: RemediationStrategy = RemediationStrategy.REPULSION_DISPERSION

@dataclass
class SpatialClearanceResult:
    is_valid: bool
    violations: List[SpatialClearanceViolation] = field(default_factory=list)
    adjusted_entities: List[EntitySpatialSpec] = field(default_factory=list)
    remediations_applied: List[str] = field(default_factory=list)

@dataclass
class SurfacePlaneSpec:
    surface_id: str
    normal: Tuple[float, float, float]
    distance: float
    vertices: List[Tuple[float, float, float]] = field(default_factory=list)
    material_slot: int = 0
    is_culled: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class CoplanarConflict:
    conflict_type: CoplanarConflictType
    surface_a_id: str
    surface_b_id: str
    normal_dot: float
    distance_delta: float
    overlap_area: float = 0.0
    message: str = ""
    suggested_remediation: RemediationStrategy = RemediationStrategy.MICRO_LAYERING_OFFSET

@dataclass
class CoplanarRemediationResult:
    is_valid: bool
    conflicts: List[CoplanarConflict] = field(default_factory=list)
    adjusted_surfaces: List[SurfacePlaneSpec] = field(default_factory=list)
    faces_culled: int = 0
    micro_offsets_applied: int = 0
    remediations_applied: List[str] = field(default_factory=list)
