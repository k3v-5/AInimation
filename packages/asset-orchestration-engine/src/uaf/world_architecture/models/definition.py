"""
BiomeType24, WorldBoundaryBounds, WorldGridCell, and WorldDefinition24 models.
UAF-81.24 Sections 3, 4, 8, 10, 14, 32, 33.
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Tuple
from ...core.hashing.canonical_hasher import CanonicalHasher


class BiomeType24(str, Enum):
    FOREST = "FOREST"
    DESERT = "DESERT"
    TUNDRA = "TUNDRA"
    JUNGLE = "JUNGLE"
    SWAMP = "SWAMP"
    ROCKY = "ROCKY"
    URBAN = "URBAN"
    INDUSTRIAL = "INDUSTRIAL"
    ALIEN = "ALIEN"
    SCI_FI = "SCI_FI"
    CUSTOM = "CUSTOM"


@dataclass
class WorldBoundaryBounds:
    min_x: float = -50000.0  # cm (-500m)
    max_x: float = 50000.0   # cm (+500m)
    min_y: float = -50000.0
    max_y: float = 50000.0
    min_z: float = -5000.0   # cm (-50m)
    max_z: float = 15000.0   # cm (+150m)

    @property
    def is_valid(self) -> bool:
        return (
            self.max_x > self.min_x and
            self.max_y > self.min_y and
            self.max_z > self.min_z
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "min_x": self.min_x,
            "max_x": self.max_x,
            "min_y": self.min_y,
            "max_y": self.max_y,
            "min_z": self.min_z,
            "max_z": self.max_z,
        }


@dataclass
class WorldGridCell:
    cell_id: str
    grid_x: int
    grid_y: int
    world_pos_xyz: List[float] = field(default_factory=lambda: [0.0, 0.0, 0.0])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "cell_id": self.cell_id,
            "grid_x": self.grid_x,
            "grid_y": self.grid_y,
            "world_pos_xyz": self.world_pos_xyz,
        }


@dataclass
class WorldDefinition24:
    world_id: str
    bounds: WorldBoundaryBounds = field(default_factory=WorldBoundaryBounds)
    primary_biome: BiomeType24 = BiomeType24.URBAN
    cell_size: float = 10000.0  # 100m
    seed: int = 42

    @property
    def definition_hash(self) -> str:
        return CanonicalHasher.compute_hash(self.to_dict())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "world_id": self.world_id,
            "bounds": self.bounds.to_dict(),
            "primary_biome": self.primary_biome.value,
            "cell_size": self.cell_size,
            "seed": self.seed,
        }
