"""
WorldScaleProfile40, RegionType40, TerrainSlopeClass40, WorldDimensions40, WorldBuildSpecification models.
UAF-81.40 Sections 4, 5, 6, 16, 33, 153.
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from ...core.hashing.canonical_hasher import CanonicalHasher


class WorldScaleProfile40(str, Enum):
    SMALL = "SMALL"
    MEDIUM = "MEDIUM"
    LARGE = "LARGE"
    OPEN_WORLD = "OPEN_WORLD"
    CUSTOM = "CUSTOM"


class RegionType40(str, Enum):
    URBAN = "URBAN"
    INDUSTRIAL = "INDUSTRIAL"
    FOREST = "FOREST"
    DESERT = "DESERT"
    MOUNTAIN = "MOUNTAIN"
    COASTAL = "COASTAL"
    SWAMP = "SWAMP"
    ARCTIC = "ARCTIC"
    UNDERGROUND = "UNDERGROUND"
    MILITARY = "MILITARY"
    RURAL = "RURAL"
    CUSTOM = "CUSTOM"


class TerrainSlopeClass40(str, Enum):
    FLAT = "FLAT"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    STEEP = "STEEP"
    CLIFF = "CLIFF"


@dataclass
class WorldDimensions40:
    width_m: float = 2000.0
    length_m: float = 2000.0
    height_m: float = 300.0

    @property
    def is_valid(self) -> bool:
        return self.width_m > 0.0 and self.length_m > 0.0 and self.height_m >= 10.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "width_m": self.width_m,
            "length_m": self.length_m,
            "height_m": self.height_m,
        }


@dataclass
class WorldBuildSpecification:
    world_id: str
    scale_profile: WorldScaleProfile40
    primary_region: RegionType40
    dimensions: WorldDimensions40 = field(default_factory=WorldDimensions40)
    cell_count: int = 4
    has_world_partition: bool = True
    has_hydrology: bool = True
    road_count: int = 2
    seed: int = 42

    @property
    def is_valid_scale(self) -> bool:
        if not self.dimensions.is_valid or self.cell_count < 1:
            return False
        # Large/OpenWorld worlds require World Partition for streaming stability (Section 76, 171)
        if (self.dimensions.width_m >= 2000.0 or self.dimensions.length_m >= 2000.0) and not self.has_world_partition:
            return False
        return True

    @property
    def definition_hash(self) -> str:
        return CanonicalHasher.compute_hash(self.to_dict())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "world_id": self.world_id,
            "scale_profile": self.scale_profile.value,
            "primary_region": self.primary_region.value,
            "dimensions": self.dimensions.to_dict(),
            "cell_count": self.cell_count,
            "has_world_partition": self.has_world_partition,
            "has_hydrology": self.has_hydrology,
            "road_count": self.road_count,
            "seed": self.seed,
        }
