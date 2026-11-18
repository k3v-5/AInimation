"""
TerrainMode, ErosionType, and TerritoryModel models.
UAF-81.13 Sections 4, 5, 6, 7, 8, 9, 27, 28.
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from ...core.hashing.canonical_hasher import CanonicalHasher


class TerrainMode(str, Enum):
    HEIGHTFIELD = "HEIGHTFIELD"
    PROCEDURAL_MESH = "PROCEDURAL_MESH"
    HYBRID_TERRAIN = "HYBRID_TERRAIN"


class ErosionType(str, Enum):
    HYDRAULIC = "HYDRAULIC"
    THERMAL = "THERMAL"
    WIND = "WIND"
    MANUAL_MASK = "MANUAL_MASK"


@dataclass
class TerritoryModel:
    territory_id: str
    world_width_m: float = 1000.0
    world_length_m: float = 1000.0
    min_height_m: float = 0.0
    max_height_m: float = 250.0
    terrain_mode: TerrainMode = TerrainMode.HYBRID_TERRAIN
    seed: int = 42

    @property
    def territory_hash(self) -> str:
        return CanonicalHasher.compute_hash(self.to_dict())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "territory_id": self.territory_id,
            "world_width_m": self.world_width_m,
            "world_length_m": self.world_length_m,
            "min_height_m": self.min_height_m,
            "max_height_m": self.max_height_m,
            "terrain_mode": self.terrain_mode.value,
            "seed": self.seed,
        }
