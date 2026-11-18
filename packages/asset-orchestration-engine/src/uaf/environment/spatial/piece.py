"""
ModularPiece models reusable structural environmental building blocks.
UAF-81.12 Sections 6, 7, 203.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from .grid import SnapPoint, SnapCategory
from ...core.hashing.canonical_hasher import CanonicalHasher


@dataclass
class ModularPiece:
    piece_id: str
    module_type: str  # "WALL", "FLOOR", "CEILING", "DOOR", "CORNER", "STAIR"
    dimensions: List[float] = field(default_factory=lambda: [2.0, 0.2, 3.0])  # width, depth, height meters
    snap_points: List[SnapPoint] = field(default_factory=list)
    collision_shape: str = "UBX_Piece_01"
    material_id: str = "M_SciFi_Wall"

    @property
    def piece_hash(self) -> str:
        return CanonicalHasher.compute_hash(self.to_dict())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "piece_id": self.piece_id,
            "module_type": self.module_type,
            "dimensions": self.dimensions,
            "snap_points": [s.to_dict() for s in self.snap_points],
            "collision_shape": self.collision_shape,
            "material_id": self.material_id,
        }

    @classmethod
    def create_standard_wall(cls, piece_id: str = "SM_SciFi_Wall_2x3") -> "ModularPiece":
        snaps = [
            SnapPoint("snap_L", [-1.0, 0.0, 1.5], [0.0, 0.0, 0.0], [-1.0, 0.0, 0.0], SnapCategory.WALL),
            SnapPoint("snap_R", [1.0, 0.0, 1.5], [0.0, 0.0, 0.0], [1.0, 0.0, 0.0], SnapCategory.WALL),
        ]
        return cls(
            piece_id=piece_id,
            module_type="WALL",
            dimensions=[2.0, 0.2, 3.0],
            snap_points=snaps,
            collision_shape="UBX_SciFi_Wall_2x3",
            material_id="M_SciFi_Wall",
        )

    @classmethod
    def create_standard_floor(cls, piece_id: str = "SM_SciFi_Floor_2x2") -> "ModularPiece":
        snaps = [
            SnapPoint("snap_N", [0.0, 1.0, 0.0], [0.0, 0.0, 0.0], [0.0, 1.0, 0.0], SnapCategory.FLOOR),
            SnapPoint("snap_S", [0.0, -1.0, 0.0], [0.0, 0.0, 0.0], [0.0, -1.0, 0.0], SnapCategory.FLOOR),
            SnapPoint("snap_E", [1.0, 0.0, 0.0], [0.0, 0.0, 0.0], [1.0, 0.0, 0.0], SnapCategory.FLOOR),
            SnapPoint("snap_W", [-1.0, 0.0, 0.0], [0.0, 0.0, 0.0], [-1.0, 0.0, 0.0], SnapCategory.FLOOR),
        ]
        return cls(
            piece_id=piece_id,
            module_type="FLOOR",
            dimensions=[2.0, 2.0, 0.2],
            snap_points=snaps,
            collision_shape="UBX_SciFi_Floor_2x2",
            material_id="M_SciFi_Floor",
        )
