"""
MeshCategory53, TopologyType53, MeshDimensions53, UniversalMeshSpecification models.
UAF-81.53 Sections 3, 4, 5, 6, 164, 166.
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from ...core.hashing.canonical_hasher import CanonicalHasher


class MeshCategory53(str, Enum):
    CHARACTER = "CHARACTER"
    ROBOT = "ROBOT"
    CREATURE = "CREATURE"
    WEAPON = "WEAPON"
    PROP = "PROP"
    ARCHITECTURE = "ARCHITECTURE"
    ROCK = "ROCK"
    TREE = "TREE"
    MODULAR_KIT = "MODULAR_KIT"
    COMPLEX_MESH = "COMPLEX_MESH"
    VEHICLE = "VEHICLE"
    TERRAIN = "TERRAIN"
    VFX_MESH = "VFX_MESH"


class TopologyType53(str, Enum):
    TRIANGLES = "TRIANGLES"
    QUADS = "QUADS"
    N_GONS = "N_GONS"
    HYBRID = "HYBRID"


@dataclass
class MeshDimensions53:
    width_cm: float = 100.0
    length_cm: float = 100.0
    height_cm: float = 100.0

    @property
    def is_valid(self) -> bool:
        return self.width_cm > 0.0 and self.length_cm > 0.0 and self.height_cm > 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "width_cm": self.width_cm,
            "length_cm": self.length_cm,
            "height_cm": self.height_cm,
        }


@dataclass
class UniversalMeshSpecification:
    mesh_id: str
    category: MeshCategory53
    topology: TopologyType53 = TopologyType53.TRIANGLES
    dimensions: MeshDimensions53 = field(default_factory=MeshDimensions53)
    vertex_count: int = 1200
    triangle_count: int = 2400
    has_normals: bool = True
    has_tangents: bool = True
    has_uv: bool = True
    has_collision: bool = True
    has_lod: bool = True
    is_nanite_ready: bool = True
    seed: int = 42

    @property
    def is_valid_mesh(self) -> bool:
        return (
            self.dimensions.is_valid and
            self.vertex_count >= 3 and
            self.triangle_count >= 1 and
            self.has_normals and
            self.has_tangents and
            self.has_uv and
            self.has_collision and
            self.has_lod
        )

    @property
    def definition_hash(self) -> str:
        return CanonicalHasher.compute_hash(self.to_dict())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "mesh_id": self.mesh_id,
            "category": self.category.value,
            "topology": self.topology.value,
            "dimensions": self.dimensions.to_dict(),
            "vertex_count": self.vertex_count,
            "triangle_count": self.triangle_count,
            "has_normals": self.has_normals,
            "has_tangents": self.has_tangents,
            "has_uv": self.has_uv,
            "has_collision": self.has_collision,
            "has_lod": self.has_lod,
            "is_nanite_ready": self.is_nanite_ready,
            "seed": self.seed,
        }
