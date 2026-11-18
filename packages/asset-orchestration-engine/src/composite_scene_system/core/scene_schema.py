import time
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Tuple
from .scene_types import SceneType, LockState, SceneState, PlanningStage, CollisionSeverity

@dataclass
class SocketDefinition:
    socket_id: str
    socket_type: str # DOOR, ROAD, WALL, FENCE, PROP
    local_position: Tuple[float, float, float] # (x, y, z)
    local_rotation: Tuple[float, float, float] = (0.0, 0.0, 0.0) # (roll, pitch, yaw)
    compatibility: List[str] = field(default_factory=list)

@dataclass
class AssetInstance:
    instance_id: str
    asset_type: str # HOUSE, SHOP, CHURCH, TREE, PROP
    template_id: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    transform: Dict[str, float] = field(default_factory=lambda: {"x": 0.0, "y": 0.0, "z": 0.0, "rot_z": 0.0})
    dimensions: Dict[str, float] = field(default_factory=lambda: {"width": 4.0, "depth": 4.0, "height": 5.0})
    parent_id: Optional[str] = None
    region_id: str = "DEFAULT"
    area_id: str = "DEFAULT"
    sockets: List[SocketDefinition] = field(default_factory=list)
    material_overrides: Dict[str, str] = field(default_factory=dict)
    lock_state: LockState = LockState.UNLOCKED
    is_instance_of_id: Optional[str] = None # Para instanciación ligera de malla
    seed: int = 42

@dataclass
class SceneArea:
    area_id: str
    name: str
    region_id: str
    instance_ids: List[str] = field(default_factory=list)

@dataclass
class SceneRegion:
    region_id: str
    name: str
    areas: Dict[str, SceneArea] = field(default_factory=dict)

@dataclass
class SceneBudget:
    max_assets: int = 150
    max_unique_meshes: int = 20
    max_vertices: int = 50000
    max_triangles: int = 80000
    max_materials: int = 15

@dataclass
class SceneSpecification:
    scene_id: str
    scene_type: SceneType
    style: str = "medieval_stylized"
    scale: str = "small" # small, medium, large
    bounds: Dict[str, float] = field(default_factory=lambda: {"width": 100.0, "depth": 100.0, "height": 30.0})
    components_count: Dict[str, int] = field(default_factory=dict) # {"house": 8, "shop": 2, "church": 1, "plaza": 1}
    budget: SceneBudget = field(default_factory=SceneBudget)
    seed: int = 42

@dataclass
class SceneBuildPlan:
    scene_id: str
    build_order: List[str] = field(default_factory=list) # ["terrain", "roads", "plaza", "church", "houses", "props"]
    regions: Dict[str, SceneRegion] = field(default_factory=dict)
    instances: Dict[str, AssetInstance] = field(default_factory=dict)
    status: SceneState = SceneState.PLANNED
    stage: PlanningStage = PlanningStage.COMPLETED

@dataclass
class SceneDiagnosticReport:
    scene_id: str
    layout_errors: List[str] = field(default_factory=list)
    collision_errors: List[str] = field(default_factory=list)
    budget_errors: List[str] = field(default_factory=list)
    socket_errors: List[str] = field(default_factory=list)
    critical_errors: List[str] = field(default_factory=list)
    scene_quality_score: float = 1.00
    is_valid: bool = True

@dataclass
class SceneManifest:
    scene_id: str
    fingerprint: str
    instance_count: int
    instances: List[Dict[str, Any]] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)
