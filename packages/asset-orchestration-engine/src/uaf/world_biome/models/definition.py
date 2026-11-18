"""
WorldType32, BiomeType32, WorldBounds32, BiomeDefinition32, and BiomeWorldDefinition models.
UAF-81.32 Sections 3, 4, 8, 9, 11, 15, 28, 29, 122.
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from ...core.hashing.canonical_hasher import CanonicalHasher


class WorldType32(str, Enum):
    ROOM_BASED = "ROOM_BASED"
    CORRIDOR_BASED = "CORRIDOR_BASED"
    DUNGEON = "DUNGEON"
    FACILITY = "FACILITY"
    URBAN = "URBAN"
    INDUSTRIAL = "INDUSTRIAL"
    OUTDOOR_COMBAT = "OUTDOOR_COMBAT"
    OPEN_WORLD = "OPEN_WORLD"
    HYBRID = "HYBRID"
    CUSTOM = "CUSTOM"


class BiomeType32(str, Enum):
    TEMPERATE_FOREST = "TEMPERATE_FOREST"
    ARID_DESERT = "ARID_DESERT"
    ARCTIC_TUNDRA = "ARCTIC_TUNDRA"
    TROPICAL_JUNGLE = "TROPICAL_JUNGLE"
    VOLCANIC_WASTELAND = "VOLCANIC_WASTELAND"
    URBAN_RUINS = "URBAN_RUINS"
    SCI_FI_INTERIOR = "SCI_FI_INTERIOR"
    INDUSTRIAL_SECTOR = "INDUSTRIAL_SECTOR"


@dataclass
class WorldBounds32:
    min_x: float = -5000.0
    max_x: float = 5000.0
    min_y: float = -5000.0
    max_y: float = 5000.0
    min_z: float = 0.0
    max_z: float = 2000.0

    @property
    def is_valid(self) -> bool:
        return (
            self.min_x < self.max_x and (self.max_x - self.min_x) >= 100.0 and
            self.min_y < self.max_y and (self.max_y - self.min_y) >= 100.0 and
            self.min_z < self.max_z and (self.max_z - self.min_z) >= 100.0
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
class BiomeDefinition32:
    biome_id: str
    biome_type: BiomeType32
    temperature: float = 0.5  # 0.0 to 1.0
    humidity: float = 0.5     # 0.0 to 1.0
    altitude_range: List[float] = field(default_factory=lambda: [0.0, 1000.0])

    @property
    def is_valid(self) -> bool:
        return (
            0.0 <= self.temperature <= 1.0 and
            0.0 <= self.humidity <= 1.0 and
            len(self.altitude_range) == 2 and
            self.altitude_range[0] <= self.altitude_range[1]
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "biome_id": self.biome_id,
            "biome_type": self.biome_type.value,
            "temperature": self.temperature,
            "humidity": self.humidity,
            "altitude_range": self.altitude_range,
        }


@dataclass
class BiomeWorldDefinition:
    world_id: str
    world_type: WorldType32
    bounds: WorldBounds32
    biomes: List[BiomeDefinition32] = field(default_factory=list)
    seed: int = 42

    @property
    def definition_hash(self) -> str:
        return CanonicalHasher.compute_hash(self.to_dict())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "world_id": self.world_id,
            "world_type": self.world_type.value,
            "bounds": self.bounds.to_dict(),
            "biomes": [b.to_dict() for b in self.biomes],
            "seed": self.seed,
        }
