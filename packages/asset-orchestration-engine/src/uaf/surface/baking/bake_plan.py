"""
BakePlan and BakeResult models for high-to-low mesh surface projection.
UAF-81.4 Sections 28, 29, 30, 31.
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from ...core.hashing.canonical_hasher import CanonicalHasher


class BakeType(str, Enum):
    NORMAL = "NORMAL"
    AO = "AO"
    CURVATURE = "CURVATURE"
    POSITION = "POSITION"
    THICKNESS = "THICKNESS"
    MATERIAL_ID = "MATERIAL_ID"
    WORLD_NORMAL = "WORLD_NORMAL"
    HEIGHT = "HEIGHT"


@dataclass
class BakePlan:
    plan_id: str
    high_res_mesh_id: str
    low_res_mesh_id: str
    bake_types: List[BakeType] = field(
        default_factory=lambda: [BakeType.NORMAL, BakeType.AO, BakeType.CURVATURE]
    )
    resolution: int = 2048
    cage_extrusion_meters: float = 0.01
    anti_aliasing_samples: int = 4

    @property
    def plan_hash(self) -> str:
        return CanonicalHasher.compute_hash(self.to_dict())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "plan_id": self.plan_id,
            "high_res_mesh_id": self.high_res_mesh_id,
            "low_res_mesh_id": self.low_res_mesh_id,
            "bake_types": [b.value for b in self.bake_types],
            "resolution": self.resolution,
            "cage_extrusion_meters": self.cage_extrusion_meters,
            "anti_aliasing_samples": self.anti_aliasing_samples,
        }


@dataclass
class BakeResult:
    is_success: bool
    plan_id: str
    generated_maps: Dict[str, str] = field(default_factory=dict)  # bake_type -> texture_id / path
    validation_issues: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "is_success": self.is_success,
            "plan_id": self.plan_id,
            "generated_maps": self.generated_maps,
            "validation_issues": self.validation_issues,
        }
