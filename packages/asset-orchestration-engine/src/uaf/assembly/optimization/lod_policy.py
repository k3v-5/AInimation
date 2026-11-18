"""
LODPolicy, LODLevel, LODChain, and NanitePolicy models.
UAF-81.8 Sections 20, 21, 23, 28, 29, 30.
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional


class NanitePolicy(str, Enum):
    ENABLED = "ENABLED"
    DISABLED = "DISABLED"
    AUTO = "AUTO"

    @classmethod
    def evaluate_nanite_eligibility(
        cls,
        is_static: bool,
        triangle_count: int,
        has_skinning: bool,
    ) -> bool:
        # Nanite primarily targets static opaque meshes with substantial triangle density (> 2000 tris)
        if has_skinning or not is_static:
            return False
        return triangle_count >= 1500


@dataclass
class LODLevel:
    lod_index: int
    screen_size: float           # Screen size threshold (e.g. 1.0 for LOD0, 0.5 for LOD1, etc.)
    triangle_ratio: float        # Relative to base LOD0 (e.g. 1.0, 0.5, 0.25)
    triangle_count: int = 1000
    material_slot_count: int = 1

    def to_dict(self) -> Dict[str, Any]:
        return {
            "lod_index": self.lod_index,
            "screen_size": self.screen_size,
            "triangle_ratio": self.triangle_ratio,
            "triangle_count": self.triangle_count,
            "material_slot_count": self.material_slot_count,
        }


@dataclass
class LODChain:
    lods: List[LODLevel] = field(default_factory=list)

    @classmethod
    def create_standard_chain(cls, base_triangles: int, lod_count: int = 4) -> "LODChain":
        # Standard exponential reduction: 100%, 50%, 25%, 12%
        screen_sizes = [1.0, 0.5, 0.25, 0.12, 0.05]
        ratios = [1.0, 0.5, 0.25, 0.12, 0.05]

        chain = []
        for i in range(min(lod_count, 5)):
            chain.append(
                LODLevel(
                    lod_index=i,
                    screen_size=screen_sizes[i],
                    triangle_ratio=ratios[i],
                    triangle_count=max(24, int(base_triangles * ratios[i])),
                )
            )
        return cls(lods=chain)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "lod_count": len(self.lods),
            "lods": [l.to_dict() for l in self.lods],
        }
