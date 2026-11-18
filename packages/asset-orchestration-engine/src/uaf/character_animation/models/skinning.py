"""
SkinningMethod and SkinningWeightData models for vertex deformation.
UAF-81.17 Sections 35, 36, 37, 38, 39.
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional


class SkinningMethod(str, Enum):
    LINEAR_BLEND = "LINEAR_BLEND"
    DUAL_QUATERNION = "DUAL_QUATERNION"


@dataclass
class SkinningWeightData:
    vertex_count: int = 12000
    max_influences_per_vertex: int = 4
    skinning_method: SkinningMethod = SkinningMethod.DUAL_QUATERNION
    weights_sum_normalized: bool = True
    unweighted_vertices_count: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "vertex_count": self.vertex_count,
            "max_influences_per_vertex": self.max_influences_per_vertex,
            "skinning_method": self.skinning_method.value,
            "weights_sum_normalized": self.weights_sum_normalized,
            "unweighted_vertices_count": self.unweighted_vertices_count,
        }
