"""
BiomeType48, TerrainGenMethod48, ErosionType48, TerrainDimensions48, TerrainWorldSpecification models.
UAF-81.48 Sections 4, 10, 11, 15, 23, 126.
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from ...core.hashing.canonical_hasher import CanonicalHasher


class BiomeType48(str, Enum):
    DESERT = "DESERT"
    FOREST = "FOREST"
    MOUNTAIN = "MOUNTAIN"
    INDUSTRIAL = "INDUSTRIAL"
    SCI_FI = "SCI_FI"
    TUNDRA = "TUNDRA"
    SWAMP = "SWAMP"
    COASTAL = "COASTAL"


class TerrainGenMethod48(str, Enum):
    NOISE = "NOISE"
    FRACTAL_NOISE = "FRACTAL_NOISE"
    RIDGED_NOISE = "RIDGED_NOISE"
    VORONOI = "VORONOI"
    HEIGHTMAP = "HEIGHTMAP"
    EROSION = "EROSION"
    STAMP = "STAMP"
    HYBRID = "HYBRID"


class ErosionType48(str, Enum):
    HYDRAULIC = "HYDRAULIC"
    THERMAL = "THERMAL"
    WIND = "WIND"
    SEDIMENT = "SEDIMENT"
    CUSTOM = "CUSTOM"


@dataclass
class TerrainDimensions48:
    width_m: float = 2000.0
    length_m: float = 2000.0
    min_height_m: float = 0.0
    max_height_m: float = 350.0

    @property
    def height_delta_m(self) -> float:
        return self.max_height_m - self.min_height_m

    @property
    def is_valid(self) -> bool:
        return self.width_m > 0.0 and self.length_m > 0.0 and self.height_delta_m >= 10.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "width_m": self.width_m,
            "length_m": self.length_m,
            "min_height_m": self.min_height_m,
            "max_height_m": self.max_height_m,
        }


@dataclass
class TerrainWorldSpecification:
    world_id: str
    biome: BiomeType48
    method: TerrainGenMethod48 = TerrainGenMethod48.HYBRID
    dimensions: TerrainDimensions48 = field(default_factory=TerrainDimensions48)
    has_erosion: bool = True
    has_roads: bool = True
    has_poi: bool = True
    has_vegetation: bool = True
    has_navigation: bool = True
    has_streaming: bool = True
    seed: int = 42

    @property
    def is_valid_world(self) -> bool:
        return (
            self.dimensions.is_valid and
            self.has_erosion and
            self.has_roads and
            self.has_poi and
            self.has_vegetation and
            self.has_navigation and
            self.has_streaming
        )

    @property
    def definition_hash(self) -> str:
        return CanonicalHasher.compute_hash(self.to_dict())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "world_id": self.world_id,
            "biome": self.biome.value,
            "method": self.method.value,
            "dimensions": self.dimensions.to_dict(),
            "has_erosion": self.has_erosion,
            "has_roads": self.has_roads,
            "has_poi": self.has_poi,
            "has_vegetation": self.has_vegetation,
            "has_navigation": self.has_navigation,
            "has_streaming": self.has_streaming,
            "seed": self.seed,
        }
