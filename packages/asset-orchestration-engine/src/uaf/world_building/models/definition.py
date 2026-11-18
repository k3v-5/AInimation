"""
WorldType28, ModularCategory, SocketType28, ModularBlockDefinition, and PlayableWorldDefinition models.
UAF-81.28 Sections 3, 4, 5, 7, 8, 9, 10, 11.
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from ...core.hashing.canonical_hasher import CanonicalHasher


class WorldType28(str, Enum):
    INTERIOR = "INTERIOR"
    EXTERIOR = "EXTERIOR"
    URBAN = "URBAN"
    INDUSTRIAL = "INDUSTRIAL"
    MILITARY = "MILITARY"
    SCI_FI = "SCI_FI"
    FANTASY = "FANTASY"
    DUNGEON = "DUNGEON"
    FACILITY = "FACILITY"
    OPEN_WORLD = "OPEN_WORLD"
    LINEAR_LEVEL = "LINEAR_LEVEL"
    ARENA = "ARENA"
    HYBRID = "HYBRID"
    CUSTOM = "CUSTOM"


class ModularCategory(str, Enum):
    WALL = "WALL"
    FLOOR = "FLOOR"
    CEILING = "CEILING"
    DOOR = "DOOR"
    WINDOW = "WINDOW"
    STAIR = "STAIR"
    RAMP = "RAMP"
    COLUMN = "COLUMN"
    BEAM = "BEAM"
    PLATFORM = "PLATFORM"
    ROOF = "ROOF"


class SocketType28(str, Enum):
    WALL_CONNECTOR = "WALL_CONNECTOR"
    FLOOR_CONNECTOR = "FLOOR_CONNECTOR"
    CEILING_CONNECTOR = "CEILING_CONNECTOR"
    DOOR_CONNECTOR = "DOOR_CONNECTOR"
    STAIR_CONNECTOR = "STAIR_CONNECTOR"
    CUSTOM = "CUSTOM"


@dataclass
class ModularBlockDefinition:
    block_id: str
    category: ModularCategory
    dimensions_cm: List[float] = field(default_factory=lambda: [400.0, 400.0, 300.0])
    sockets: List[SocketType28] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "block_id": self.block_id,
            "category": self.category.value,
            "dimensions_cm": self.dimensions_cm,
            "sockets": [s.value for s in self.sockets],
        }


@dataclass
class PlayableWorldDefinition:
    world_id: str
    world_type: WorldType28
    grid_size_cm: float = 400.0
    module_blocks: List[ModularBlockDefinition] = field(default_factory=list)
    seed: int = 42

    @property
    def is_valid_grid(self) -> bool:
        return self.grid_size_cm >= 100.0

    @property
    def definition_hash(self) -> str:
        return CanonicalHasher.compute_hash(self.to_dict())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "world_id": self.world_id,
            "world_type": self.world_type.value,
            "grid_size_cm": self.grid_size_cm,
            "module_blocks": [b.to_dict() for b in self.module_blocks],
            "seed": self.seed,
        }
