from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Tuple
from .geom_types import (
    OperationState, TransactionState, MeshTopologyType,
    ExportRole, ValidationSeverity, GenerationStatus
)

@dataclass
class GeometricVertex:
    x: float
    y: float
    z: float
    normal: Tuple[float, float, float] = (0.0, 0.0, 1.0)
    uv: Tuple[float, float] = (0.0, 0.0)

@dataclass
class GeometricFace:
    vertex_indices: List[int]
    material_slot: int = 0
    normal: Tuple[float, float, float] = (0.0, 0.0, 1.0)

@dataclass
class TopologySummary:
    vertex_count: int = 0
    edge_count: int = 0
    face_count: int = 0
    triangle_count: int = 0
    ngon_count: int = 0
    non_manifold_count: int = 0
    degenerate_face_count: int = 0
    is_manifold: bool = True

@dataclass
class GeometryObjectSpec:
    object_id: str
    semantic_component_id: str
    semantic_id: str
    name: str
    parent_id: Optional[str] = None
    geometry_type: MeshTopologyType = MeshTopologyType.TRIANGLE_MESH
    transform: Dict[str, Any] = field(default_factory=lambda: {"location": (0,0,0), "rotation": (0,0,0), "scale": (1,1,1)})
    dimensions: Dict[str, float] = field(default_factory=lambda: {"x": 1.0, "y": 1.0, "z": 1.0})
    bounds: Dict[str, Any] = field(default_factory=lambda: {"min": (-0.5, -0.5, 0.0), "max": (0.5, 0.5, 1.0)})
    topology: TopologySummary = field(default_factory=TopologySummary)
    material_slots: List[str] = field(default_factory=lambda: ["M_Default"])
    modifiers: List[Dict[str, Any]] = field(default_factory=list)
    export_role: ExportRole = ExportRole.RENDER_MESH

@dataclass
class ComponentGenerationResult:
    component_id: str
    semantic_id: str
    object_id: str
    topology: TopologySummary
    triangle_count: int
    status: GenerationStatus = GenerationStatus.SUCCESS
    errors: List[str] = field(default_factory=list)

@dataclass
class GenerationContext:
    generation_id: str
    strategy_plan: Any # ModelingStrategyPlan from F57
    project_config: Dict[str, Any] = field(default_factory=dict)
    generation_seed: int = 42
    capability_api: Optional[Any] = None # BlenderCapabilityAPI from F53
    target_components: Optional[List[str]] = None
    debug_mode: bool = False

@dataclass
class CheckpointSpec:
    checkpoint_id: str
    generation_id: str
    stage: str
    object_ids: List[str]
    geometry_hash: str
    topology_summary: TopologySummary
    bounds: Dict[str, Any]

@dataclass
class GeneratedGeometryResult:
    generation_id: str = "GEN_DEFAULT"
    semantic_id: str = "asset.root"
    specification_id: str = "VAS_DEFAULT"
    strategy_id: str = "MSP_DEFAULT"
    generation_version: str = "1.0.0"
    generation_hash: str = ""
    status: GenerationStatus = GenerationStatus.SUCCESS
    geometry_objects: List[GeometryObjectSpec] = field(default_factory=list)
    component_results: Dict[str, ComponentGenerationResult] = field(default_factory=dict)
    topology_summary: TopologySummary = field(default_factory=TopologySummary)
    dimensions: Dict[str, float] = field(default_factory=dict)
    bounds: Dict[str, Any] = field(default_factory=dict)
    triangle_count: int = 0
    vertex_count: int = 0
    material_slots: List[str] = field(default_factory=list)
    pivot_state: Dict[str, Any] = field(default_factory=dict)
    collision_geometry: Optional[GeometryObjectSpec] = None
    lod_geometry: Dict[str, GeometryObjectSpec] = field(default_factory=dict)
    execution_trace: List[Dict[str, Any]] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    generation_metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class GeometryValidationResult:
    is_valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

@dataclass
class CompensationResult:
    success: bool
    compensated_operations: List[str] = field(default_factory=list)
    message: str = ""
