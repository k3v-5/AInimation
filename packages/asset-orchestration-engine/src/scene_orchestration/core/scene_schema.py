import time
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Tuple
from .scene_status import SceneStatus, NodeDirtyState

@dataclass
class ProxyBounds:
    min_point: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    max_point: Tuple[float, float, float] = (1.0, 1.0, 1.0)
    radius: float = 1.0

    def intersects(self, other: 'ProxyBounds') -> bool:
        # AABB overlap test
        return (self.min_point[0] <= other.max_point[0] and self.max_point[0] >= other.min_point[0] and
                self.min_point[1] <= other.max_point[1] and self.max_point[1] >= other.min_point[1] and
                self.min_point[2] <= other.max_point[2] and self.max_point[2] >= other.min_point[2])

@dataclass
class AssetRequest:
    request_id: str
    asset_type: str # house, blacksmith, tower, plaza, road
    count: int = 1
    template_id: str = "generic"
    variant_id: Optional[str] = None
    role: str = "SECONDARY" # LANDMARK, PRIMARY, SECONDARY, DECORATION
    dimensions: Tuple[float, float, float] = (4.0, 4.0, 4.0)

@dataclass
class SceneIntent:
    scene_id: str
    theme: str # medieval_village
    style: str # stylized
    size: str = "SMALL" # SMALL, MEDIUM, LARGE
    requirements: Dict[str, int] = field(default_factory=dict)
    terrain: str = "FLAT"
    roads: str = "DIRT"
    seed: int = 42

@dataclass
class SceneNode:
    node_id: str # e.g. house_001
    asset_type: str
    template_id: str
    variant_id: str
    role: str
    location: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    rotation: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    scale: Tuple[float, float, float] = (1.0, 1.0, 1.0)
    bounds: ProxyBounds = field(default_factory=ProxyBounds)
    dirty_state: NodeDirtyState = NodeDirtyState.DIRTY
    dependencies: List[str] = field(default_factory=list)

@dataclass
class ScenePlan:
    scene_id: str
    intent: SceneIntent
    nodes: Dict[str, SceneNode] = field(default_factory=dict)
    regions: List[str] = field(default_factory=list)
    seed: int = 42
    created_at: float = field(default_factory=time.time)

@dataclass
class SceneSummary:
    scene_id: str
    status: SceneStatus
    total_assets: int
    landmarks: int
    structures: int
    triangles_estimate: int
    validation_score: float = 1.0
