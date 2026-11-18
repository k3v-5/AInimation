"""
NaturalBiomeType51, TerrainType51, ErosionModel51, NaturalTerrainDimensions51, NaturalEcosystemSpecification models.
UAF-81.51 Sections 5, 6, 17, 21, 135, 142.
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from ...core.hashing.canonical_hasher import CanonicalHasher


class NaturalBiomeType51(str, Enum):
    FOREST = "FOREST"
    DESERT = "DESERT"
    MOUNTAIN = "MOUNTAIN"
    SWAMP = "SWAMP"
    COASTAL = "COASTAL"
    HYBRID = "HYBRID"
    TUNDRA = "TUNDRA"
    VOLCANIC = "VOLCANIC"


class TerrainType51(str, Enum):
    FLAT = "FLAT"
    ROLLING = "ROLLING"
    HILLY = "HILLY"
    MOUNTAINOUS = "MOUNTAINOUS"
    ALPINE = "ALPINE"
    CANYON = "CANYON"
    CLIFF = "CLIFF"
    VALLEY = "VALLEY"
    PLATEAU = "PLATEAU"
    DESERT = "DESERT"
    COASTAL = "COASTAL"
    VOLCANIC = "VOLCANIC"
    TUNDRA = "TUNDRA"
    SWAMP = "SWAMP"
    CUSTOM = "CUSTOM"


class ErosionModel51(str, Enum):
    HYDRAULIC = "HYDRAULIC"
    THERMAL = "THERMAL"
    WIND = "WIND"
    SEDIMENT = "SEDIMENT"
    CUSTOM = "CUSTOM"


@dataclass
class NaturalTerrainDimensions51:
    width_m: float = 2000.0
    length_m: float = 2000.0
    height_scale_m: float = 300.0

    @property
    def is_valid(self) -> bool:
        return self.width_m > 0.0 and self.length_m > 0.0 and self.height_scale_m >= 10.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "width_m": self.width_m,
            "length_m": self.length_m,
            "height_scale_m": self.height_scale_m,
        }


@dataclass
class NaturalEcosystemSpecification:
    ecosystem_id: str
    biome: NaturalBiomeType51
    terrain_type: TerrainType51
    dimensions: NaturalTerrainDimensions51 = field(default_factory=NaturalTerrainDimensions51)
    has_erosion: bool = True
    has_vegetation: bool = True
    has_rocks: bool = True
    has_water: bool = True
    has_poi: bool = True
    has_navigation: bool = True
    has_streaming: bool = True
    seed: int = 42

    @property
    def is_valid_ecosystem(self) -> bool:
        return (
            self.dimensions.is_valid and
            self.has_erosion and
            self.has_vegetation and
            self.has_rocks and
            self.has_water and
            self.has_poi and
            self.has_navigation and
            self.has_streaming
        )

    @property
    def definition_hash(self) -> str:
        return CanonicalHasher.compute_hash(self.to_dict())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "ecosystem_id": self.ecosystem_id,
            "biome": self.biome.value,
            "terrain_type": self.terrain_type.value,
            "dimensions": self.dimensions.to_dict(),
            "has_erosion": self.has_erosion,
            "has_vegetation": self.has_vegetation,
            "has_rocks": self.has_rocks,
            "has_water": self.has_water,
            "has_poi": self.has_poi,
            "has_navigation": self.has_navigation,
            "has_streaming": self.has_streaming,
            "seed": self.seed,
        }
