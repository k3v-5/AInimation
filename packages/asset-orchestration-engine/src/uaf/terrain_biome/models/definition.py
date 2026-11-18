"""
BiomeType36, VegetationCategory36, SlopeClassification36, TerrainBounds36, TerrainBiomeSpecification models.
UAF-81.36 Sections 4, 14, 16, 20, 21, 27, 28, 123.
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from ...core.hashing.canonical_hasher import CanonicalHasher


class BiomeType36(str, Enum):
    FOREST = "FOREST"
    JUNGLE = "JUNGLE"
    DESERT = "DESERT"
    TUNDRA = "TUNDRA"
    SNOW = "SNOW"
    SWAMP = "SWAMP"
    GRASSLAND = "GRASSLAND"
    ROCKY = "ROCKY"
    VOLCANIC = "VOLCANIC"
    ALIEN = "ALIEN"
    URBAN = "URBAN"
    INDUSTRIAL = "INDUSTRIAL"
    CUSTOM = "CUSTOM"


class VegetationCategory36(str, Enum):
    TREE = "TREE"
    BUSH = "BUSH"
    GRASS = "GRASS"
    FERN = "FERN"
    FLOWER = "FLOWER"
    MUSHROOM = "MUSHROOM"
    VINE = "VINE"
    ROOT = "ROOT"
    ALIEN_PLANT = "ALIEN_PLANT"
    CUSTOM = "CUSTOM"


class SlopeClassification36(str, Enum):
    FLAT = "FLAT"
    GENTLE = "GENTLE"
    MODERATE = "MODERATE"
    STEEP = "STEEP"
    CLIFF = "CLIFF"
    IMPASSABLE = "IMPASSABLE"


@dataclass
class TerrainBounds36:
    min_height_m: float = 0.0
    max_height_m: float = 100.0
    width_m: float = 1000.0
    length_m: float = 1000.0

    @property
    def is_valid(self) -> bool:
        return (
            self.width_m > 0.0 and
            self.length_m > 0.0 and
            (self.max_height_m - self.min_height_m) >= 10.0
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "min_height_m": self.min_height_m,
            "max_height_m": self.max_height_m,
            "width_m": self.width_m,
            "length_m": self.length_m,
        }


@dataclass
class TerrainBiomeSpecification:
    terrain_id: str
    primary_biome: BiomeType36
    bounds: TerrainBounds36 = field(default_factory=TerrainBounds36)
    vegetation_categories: List[VegetationCategory36] = field(default_factory=list)
    water_body_count: int = 0
    road_segments_count: int = 0
    seed: int = 42

    @property
    def is_valid_scale(self) -> bool:
        return self.bounds.is_valid

    @property
    def definition_hash(self) -> str:
        return CanonicalHasher.compute_hash(self.to_dict())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "terrain_id": self.terrain_id,
            "primary_biome": self.primary_biome.value,
            "bounds": self.bounds.to_dict(),
            "vegetation_categories": [v.value for v in self.vegetation_categories],
            "water_body_count": self.water_body_count,
            "road_segments_count": self.road_segments_count,
            "seed": self.seed,
        }
