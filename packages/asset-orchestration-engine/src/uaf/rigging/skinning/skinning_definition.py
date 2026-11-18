"""
SkinningDefinition and VertexWeights models for skeletal mesh binding.
UAF-81.5 Sections 26, 27, 29, 30.
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from ...core.hashing.canonical_hasher import CanonicalHasher


class WeightMethod(str, Enum):
    AUTOMATIC = "AUTOMATIC"
    DISTANCE = "DISTANCE"
    HEAT = "HEAT"
    VOXEL = "VOXEL"
    ENVELOPE = "ENVELOPE"
    GEODESIC = "GEODESIC"
    SEMANTIC = "SEMANTIC"
    HYBRID = "HYBRID"


@dataclass
class VertexWeights:
    vertex_index: int
    influences: Dict[str, float] = field(default_factory=dict)  # bone_id -> weight (0.0 to 1.0)

    @property
    def total_weight(self) -> float:
        return sum(self.influences.values())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "vertex_index": self.vertex_index,
            "influences": {k: round(v, 6) for k, v in self.influences.items()},
        }


@dataclass
class SkinningDefinition:
    mesh_id: str
    skeleton_id: str
    weight_method: WeightMethod = WeightMethod.AUTOMATIC
    max_influences_per_vertex: int = 4
    weights: Dict[int, VertexWeights] = field(default_factory=dict)  # vertex_index -> VertexWeights
    version: str = "1.0.0"

    @property
    def vertex_count(self) -> int:
        return len(self.weights)

    @property
    def skinning_hash(self) -> str:
        return CanonicalHasher.compute_hash(self.to_dict())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "mesh_id": self.mesh_id,
            "skeleton_id": self.skeleton_id,
            "weight_method": self.weight_method.value,
            "max_influences_per_vertex": self.max_influences_per_vertex,
            "weights": {str(k): v.to_dict() for k, v in sorted(self.weights.items())},
            "version": self.version,
        }
