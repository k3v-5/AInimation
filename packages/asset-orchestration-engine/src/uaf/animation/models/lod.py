"""
AnimationLODProfile and distance-based rig evaluation scaling.
UAF-81.9 Sections 112, 113, 114, 115.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any


@dataclass
class AnimationLODLevel:
    lod_index: int
    distance_meters: float
    skip_facial: bool = False
    skip_ik: bool = False
    skip_physics: bool = False
    update_rate_divisor: int = 1  # 1 = every frame, 2 = half frame, etc.

    def to_dict(self) -> Dict[str, Any]:
        return {
            "lod_index": self.lod_index,
            "distance_meters": self.distance_meters,
            "skip_facial": self.skip_facial,
            "skip_ik": self.skip_ik,
            "skip_physics": self.skip_physics,
            "update_rate_divisor": self.update_rate_divisor,
        }


@dataclass
class AnimationLODProfile:
    profile_id: str
    lods: List[AnimationLODLevel] = field(default_factory=list)

    @classmethod
    def create_standard_profile(cls, profile_id: str = "AnimLOD_Hero") -> "AnimationLODProfile":
        levels = [
            AnimationLODLevel(lod_index=0, distance_meters=0.0, skip_facial=False, skip_ik=False),
            AnimationLODLevel(lod_index=1, distance_meters=15.0, skip_facial=False, skip_ik=True),
            AnimationLODLevel(lod_index=2, distance_meters=35.0, skip_facial=True, skip_ik=True, skip_physics=True, update_rate_divisor=2),
        ]
        return cls(profile_id=profile_id, lods=levels)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "profile_id": self.profile_id,
            "lods": [l.to_dict() for l in self.lods],
        }
