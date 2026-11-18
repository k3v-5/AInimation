from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Tuple
from .qa_types import (
    GeometricDefectCategory, DefectSeverity, ValidationStatus,
    ValidationProfileType, CorrectionSafetyLevel, MeshWatertightMode,
    NgonPolicy
)

@dataclass
class GeometricCorrectionHint:
    target: str
    operation: str # "MERGE_VERTICES", "RECALCULATE_NORMALS", "REPAIR_BOUNDARY", "APPLY_TRANSFORM", "REDUCE_DENSITY"
    parameter: Optional[str] = None
    direction: Optional[str] = None
    magnitude: float = 0.0
    safety_level: CorrectionSafetyLevel = CorrectionSafetyLevel.SAFE_AUTOMATION
    confidence: float = 0.95

@dataclass
class GeometricDefect:
    defect_id: str
    category: GeometricDefectCategory
    severity: DefectSeverity = DefectSeverity.MODERATE
    location: str = "mesh.root"
    semantic_id: str = "asset.root"
    component_id: Optional[str] = None
    affected_elements: List[str] = field(default_factory=list) # e.g. ["v_12", "f_45"]
    measurement: Any = None
    threshold: Any = None
    expected: Any = None
    actual: Any = None
    confidence: float = 0.95
    probable_cause: str = "GEOMETRIC_DISCREPANCY"
    correction_hint: Optional[GeometricCorrectionHint] = None

@dataclass
class MeshInventory:
    object_count: int = 1
    mesh_count: int = 1
    vertex_count: int = 48
    edge_count: int = 72
    face_count: int = 40
    triangle_count: int = 80
    quad_count: int = 0
    ngon_count: int = 0
    material_slot_count: int = 2
    dimensions: Dict[str, float] = field(default_factory=lambda: {"x": 1.0, "y": 1.0, "z": 1.0})
    bounds: Dict[str, Any] = field(default_factory=dict)
    volume: float = 0.85
    surface_area: float = 4.25

@dataclass
class TopologyStatistics:
    is_manifold: bool = True
    open_boundary_count: int = 0
    non_manifold_edge_count: int = 0
    degenerate_face_count: int = 0
    duplicate_vertex_count: int = 0
    quad_ratio: float = 0.0

@dataclass
class UnrealReadinessReport:
    geometry_ready: bool = True
    collision_ready: bool = True
    lod_ready: bool = True
    uv_ready: bool = True
    transform_ready: bool = True
    semantic_ready: bool = True
    is_export_ready: bool = True

@dataclass
class GeometryValidationConfiguration:
    profile: ValidationProfileType = ValidationProfileType.PRODUCTION
    asset_class: str = "PROP.BARREL"
    watertight_mode: MeshWatertightMode = MeshWatertightMode.WATERTIGHT_REQUIRED
    ngon_policy: NgonPolicy = NgonPolicy.WARNING
    min_triangles: int = 10
    target_triangles: int = 12000
    max_triangles: int = 50000
    allow_unapplied_transforms: bool = False
    enabled_checks: List[str] = field(default_factory=lambda: [
        "TOPOLOGY", "DEGENERACY", "NORMALS", "TRANSFORMS", "DIMENSIONS", "DENSITY", "COLLISION", "UV"
    ])

@dataclass
class GeometricValidationResult:
    validation_id: str = "GEOVAL_DEFAULT"
    semantic_id: str = "asset.root"
    asset_id: str = "asset.root"
    geometry_id: str = "GEN_DEFAULT"
    mesh_inventory: MeshInventory = field(default_factory=MeshInventory)
    topology_statistics: TopologyStatistics = field(default_factory=TopologyStatistics)
    unreal_readiness: UnrealReadinessReport = field(default_factory=UnrealReadinessReport)
    quality_scores: Dict[str, float] = field(default_factory=lambda: {
        "topology_score": 1.0,
        "geometry_score": 1.0,
        "normal_score": 1.0,
        "transform_score": 1.0,
        "uv_score": 1.0,
        "collision_score": 1.0,
        "overall_geometry_score": 1.0
    })
    defects: List[GeometricDefect] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    validation_status: ValidationStatus = ValidationStatus.PASS
    confidence: float = 0.98
    correction_hints: List[GeometricCorrectionHint] = field(default_factory=list)
    validation_hash: str = ""
    execution_trace: List[Dict[str, Any]] = field(default_factory=list)
    generation_metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class QAValidationResult:
    is_valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
