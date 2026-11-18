"""
ModuleType31, ArchitecturalKitType31, SocketType31, ArchitecturalModulePiece, and ModularArchitectureKitDefinition models.
UAF-81.31 Sections 4, 5, 6, 7, 13, 14, 15, 129, 144.
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from ...core.hashing.canonical_hasher import CanonicalHasher


class ModuleType31(str, Enum):
    WALL = "WALL"
    HALF_WALL = "HALF_WALL"
    CORNER = "CORNER"
    INNER_CORNER = "INNER_CORNER"
    OUTER_CORNER = "OUTER_CORNER"
    FLOOR = "FLOOR"
    CEILING = "CEILING"
    ROOF = "ROOF"
    DOOR = "DOOR"
    WINDOW = "WINDOW"
    STAIR = "STAIR"
    RAMP = "RAMP"
    COLUMN = "COLUMN"
    BEAM = "BEAM"
    PILLAR = "PILLAR"
    PANEL = "PANEL"
    PIPE = "PIPE"
    PLATFORM = "PLATFORM"
    RAILING = "RAILING"
    FENCE = "FENCE"
    DECORATION = "DECORATION"


class ArchitecturalKitType31(str, Enum):
    SCI_FI_CORRIDOR_KIT = "SCI_FI_CORRIDOR_KIT"
    INDUSTRIAL_ROOM_KIT = "INDUSTRIAL_ROOM_KIT"
    URBAN_BUILDING_KIT = "URBAN_BUILDING_KIT"
    BUNKER_KIT = "BUNKER_KIT"
    CUSTOM_KIT = "CUSTOM_KIT"


class SocketType31(str, Enum):
    WALL_START = "WALL_START"
    WALL_END = "WALL_END"
    FLOOR_TOP = "FLOOR_TOP"
    FLOOR_BOTTOM = "FLOOR_BOTTOM"
    CEILING = "CEILING"
    DOOR = "DOOR"
    WINDOW = "WINDOW"
    STAIR = "STAIR"
    PIPE = "PIPE"
    CORNER = "CORNER"
    ROOF = "ROOF"
    STRUCTURAL = "STRUCTURAL"
    DECORATIVE = "DECORATIVE"
    CUSTOM = "CUSTOM"


@dataclass
class ArchitecturalModulePiece:
    piece_id: str
    module_type: ModuleType31
    dimensions_cm: List[float] = field(default_factory=lambda: [400.0, 20.0, 300.0])
    sockets: List[SocketType31] = field(default_factory=list)

    @property
    def is_valid(self) -> bool:
        return len(self.dimensions_cm) == 3 and all(d > 0.0 for d in self.dimensions_cm)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "piece_id": self.piece_id,
            "module_type": self.module_type.value,
            "dimensions_cm": self.dimensions_cm,
            "sockets": [s.value for s in self.sockets],
        }


@dataclass
class ModularArchitectureKitDefinition:
    kit_id: str
    kit_type: ArchitecturalKitType31
    grid_unit_cm: float = 400.0
    pieces: List[ArchitecturalModulePiece] = field(default_factory=list)
    seed: int = 42

    @property
    def is_valid_grid(self) -> bool:
        return self.grid_unit_cm >= 100.0

    @property
    def definition_hash(self) -> str:
        return CanonicalHasher.compute_hash(self.to_dict())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "kit_id": self.kit_id,
            "kit_type": self.kit_type.value,
            "grid_unit_cm": self.grid_unit_cm,
            "pieces": [p.to_dict() for p in self.pieces],
            "seed": self.seed,
        }
