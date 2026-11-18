"""
WorldType35, GridMode35, ModularKitComponent35, RoomType35, RoomDefinition35, BuildingAssemblySpecification models.
UAF-81.35 Sections 4, 5, 7, 8, 12, 13, 23, 29, 30.
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from ...core.hashing.canonical_hasher import CanonicalHasher


class WorldType35(str, Enum):
    INTERIOR = "INTERIOR"
    EXTERIOR = "EXTERIOR"
    URBAN = "URBAN"
    INDUSTRIAL = "INDUSTRIAL"
    MILITARY = "MILITARY"
    SCI_FI = "SCI_FI"
    FANTASY = "FANTASY"
    DUNGEON = "DUNGEON"
    FACILITY = "FACILITY"
    CITY = "CITY"
    OPEN_WORLD = "OPEN_WORLD"
    CUSTOM = "CUSTOM"


class GridMode35(str, Enum):
    RECTANGULAR = "RECTANGULAR"
    HEX = "HEX"
    RADIAL = "RADIAL"
    FREEFORM = "FREEFORM"
    CUSTOM = "CUSTOM"


class ModularKitComponent35(str, Enum):
    WALL = "WALL"
    WALL_CORNER = "WALL_CORNER"
    WALL_END = "WALL_END"
    FLOOR = "FLOOR"
    CEILING = "CEILING"
    DOOR = "DOOR"
    DOOR_FRAME = "DOOR_FRAME"
    WINDOW = "WINDOW"
    STAIR = "STAIR"
    COLUMN = "COLUMN"
    ROOF = "ROOF"
    TRIM = "TRIM"
    PILLAR = "PILLAR"
    ARCH = "ARCH"
    RAMP = "RAMP"
    PLATFORM = "PLATFORM"


class RoomType35(str, Enum):
    CORRIDOR = "CORRIDOR"
    HALL = "HALL"
    OFFICE = "OFFICE"
    BEDROOM = "BEDROOM"
    LAB = "LAB"
    STORAGE = "STORAGE"
    COMBAT_ARENA = "COMBAT_ARENA"
    COMMAND_CENTER = "COMMAND_CENTER"


@dataclass
class RoomDefinition35:
    room_id: str
    room_type: RoomType35
    dimensions_cm: List[float] = field(default_factory=lambda: [400.0, 400.0, 300.0])  # width, length, height
    origin: List[float] = field(default_factory=lambda: [0.0, 0.0, 0.0])
    connected_room_ids: List[str] = field(default_factory=list)

    @property
    def is_valid_scale(self) -> bool:
        return (
            len(self.dimensions_cm) == 3 and
            all(d > 0.0 for d in self.dimensions_cm) and
            self.dimensions_cm[2] >= 240.0  # Unreal minimum interior clearance height
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "room_id": self.room_id,
            "room_type": self.room_type.value,
            "dimensions_cm": self.dimensions_cm,
            "origin": self.origin,
            "connected_room_ids": self.connected_room_ids,
        }


@dataclass
class BuildingAssemblySpecification:
    world_id: str
    world_type: WorldType35
    grid_mode: GridMode35 = GridMode35.RECTANGULAR
    cell_size_cm: float = 100.0
    rooms: List[RoomDefinition35] = field(default_factory=list)
    spawn_points_count: int = 1
    has_objectives: bool = True
    seed: int = 42

    @property
    def is_valid_grid(self) -> bool:
        return self.cell_size_cm >= 50.0

    @property
    def definition_hash(self) -> str:
        return CanonicalHasher.compute_hash(self.to_dict())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "world_id": self.world_id,
            "world_type": self.world_type.value,
            "grid_mode": self.grid_mode.value,
            "cell_size_cm": self.cell_size_cm,
            "rooms": [r.to_dict() for r in self.rooms],
            "spawn_points_count": self.spawn_points_count,
            "has_objectives": self.has_objectives,
            "seed": self.seed,
        }
