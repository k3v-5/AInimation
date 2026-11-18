import hashlib
import json
import time
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Tuple
from .procedural_types import PrimitiveType, QualityLevel, ConstructionPass

@dataclass
class GeometryPrimitive:
    primitive_id: str
    primitive_type: PrimitiveType
    position: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    rotation: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    dimensions: Tuple[float, float, float] = (1.0, 1.0, 1.0) # (w, d, h)
    material: str = "DEFAULT"
    tags: List[str] = field(default_factory=list)

@dataclass
class GraphNode:
    node_id: str
    node_type: str # FOUNDATION, WALL, DOOR, WINDOW, STAIR, ROOF, COLLISION, NAVIGATION
    parent_id: Optional[str] = None
    primitives: List[GeometryPrimitive] = field(default_factory=list)
    parameters: Dict[str, Any] = field(default_factory=dict)
    pass_level: ConstructionPass = ConstructionPass.STRUCTURAL
    builder_owner: str = "ProceduralBuilder"

@dataclass
class AssetDNA:
    spec_reference: str
    generator_version: str = "v1.0.0"
    structural_seed: int = 42
    detail_seed: int = 1001
    surface_seed: int = 9999
    parameters: Dict[str, Any] = field(default_factory=dict)

@dataclass
class AssetConstructionGraph:
    asset_id: str
    dna: AssetDNA
    quality_level: QualityLevel = QualityLevel.FINAL
    nodes: Dict[str, GraphNode] = field(default_factory=dict)

    def compute_geometry_hash(self) -> str:
        payload = {
            "asset_id": self.asset_id,
            "structural_seed": self.dna.structural_seed,
            "params": self.dna.parameters,
            "nodes": {
                k: [
                    {
                        "type": p.primitive_type.value,
                        "pos": [round(x, 2) for x in p.position],
                        "dim": [round(x, 2) for x in p.dimensions],
                        "mat": p.material
                    }
                    for p in v.primitives
                ]
                for k, v in sorted(self.nodes.items())
            }
        }
        serialized = json.dumps(payload, sort_keys=True)
        return hashlib.sha256(serialized.encode("utf-8")).hexdigest()[:16]

@dataclass
class GeometryReport:
    asset_id: str
    triangle_count: int
    vertex_count: int
    object_count: int
    materials: List[str]
    bounds: Dict[str, float]
    quality_level: QualityLevel
    is_valid: bool = True

@dataclass
class BuildManifest:
    asset_id: str
    spec_hash: str
    geometry_hash: str
    generator_version: str
    timestamp: float = field(default_factory=time.time)
