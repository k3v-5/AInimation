"""
GridMode44, ModularCategory44, ConnectorType44, WorldTheme44, MapDimensions44, MapAuthoringSpecification models.
UAF-81.44 Sections 4, 9, 10, 13, 15, 134, 135.
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from ...core.hashing.canonical_hasher import CanonicalHasher


class GridMode44(str, Enum):
    SQUARE = "SQUARE"
    RECTANGULAR = "RECTANGULAR"
    HEXAGONAL = "HEXAGONAL"
    FREEFORM = "FREEFORM"
    MODULAR = "MODULAR"


class ModularCategory44(str, Enum):
    FLOOR = "FLOOR"
    WALL = "WALL"
    CORNER = "CORNER"
    T_JUNCTION = "T_JUNCTION"
    CROSS_JUNCTION = "CROSS_JUNCTION"
    CEILING = "CEILING"
    ROOF = "ROOF"
    DOOR = "DOOR"
    WINDOW = "WINDOW"
    STAIR = "STAIR"
    RAMP = "RAMP"
    COLUMN = "COLUMN"
    PILLAR = "PILLAR"
    ARCH = "ARCH"
    PIPE = "PIPE"
    RAILING = "RAILING"
    PLATFORM = "PLATFORM"
    COVER = "COVER"
    DECORATION = "DECORATION"


class ConnectorType44(str, Enum):
    WALL = "WALL"
    FLOOR = "FLOOR"
    CEILING = "CEILING"
    DOOR = "DOOR"
    WINDOW = "WINDOW"
    PIPE = "PIPE"
    STAIR = "STAIR"
    ROOF = "ROOF"
    POWER = "POWER"
    VENTILATION = "VENTILATION"
    GAMEPLAY = "GAMEPLAY"


class WorldTheme44(str, Enum):
    INDUSTRIAL = "INDUSTRIAL"
    SCI_FI = "SCI_FI"
    BUNKER = "BUNKER"
    OUTDOOR = "OUTDOOR"
    FOREST = "FOREST"
    COMBAT = "COMBAT"


@dataclass
class MapDimensions44:
    width_m: float = 2000.0
    length_m: float = 2000.0
    height_m: float = 200.0

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
class MapAuthoringSpecification:
    map_id: str
    theme: WorldTheme44
    grid_mode: GridMode44 = GridMode44.MODULAR
    dimensions: MapDimensions44 = field(default_factory=MapDimensions44)
    cell_size_cm: float = 100.0
    modular_piece_count: int = 24
    has_collision: bool = True
    has_navigation: bool = True
    has_lighting: bool = True
    has_streaming_partition: bool = True
    seed: int = 42

    @property
    def is_valid_map(self) -> bool:
        return (
            self.dimensions.is_valid and
            self.cell_size_cm >= 10.0 and
            self.modular_piece_count >= 1 and
            self.has_collision and
            self.has_navigation and
            self.has_lighting and
            self.has_streaming_partition
        )

    @property
    def definition_hash(self) -> str:
        return CanonicalHasher.compute_hash(self.to_dict())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "map_id": self.map_id,
            "theme": self.theme.value,
            "grid_mode": self.grid_mode.value,
            "dimensions": self.dimensions.to_dict(),
            "cell_size_cm": self.cell_size_cm,
            "modular_piece_count": self.modular_piece_count,
            "has_collision": self.has_collision,
            "has_navigation": self.has_navigation,
            "has_lighting": self.has_lighting,
            "has_streaming_partition": self.has_streaming_partition,
            "seed": self.seed,
        }
