"""
ModuleCategory47, SnapType47, EnvironmentStyle47, EnvironmentDimensions47, ModularEnvironmentSpecification models.
UAF-81.47 Sections 4, 5, 6, 8, 12, 131, 170.
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from ...core.hashing.canonical_hasher import CanonicalHasher


class ModuleCategory47(str, Enum):
    WALL = "WALL"
    FLOOR = "FLOOR"
    CEILING = "CEILING"
    DOOR = "DOOR"
    WINDOW = "WINDOW"
    STAIR = "STAIR"
    RAMP = "RAMP"
    COLUMN = "COLUMN"
    BEAM = "BEAM"
    ROOF = "ROOF"
    PILLAR = "PILLAR"
    PLATFORM = "PLATFORM"
    BRIDGE = "BRIDGE"
    CORRIDOR = "CORRIDOR"
    DECORATIVE = "DECORATIVE"
    UTILITY = "UTILITY"
    STRUCTURAL = "STRUCTURAL"


class SnapType47(str, Enum):
    EDGE = "EDGE"
    CORNER = "CORNER"
    CENTER = "CENTER"
    SOCKET = "SOCKET"
    GRID = "GRID"
    SURFACE = "SURFACE"
    CUSTOM = "CUSTOM"


class EnvironmentStyle47(str, Enum):
    SCI_FI = "SCI_FI"
    MILITARY = "MILITARY"
    INDUSTRIAL = "INDUSTRIAL"
    FANTASY = "FANTASY"
    MODERN = "MODERN"
    POST_APOCALYPTIC = "POST_APOCALYPTIC"
    HORROR = "HORROR"
    URBAN = "URBAN"
    CUSTOM = "CUSTOM"


@dataclass
class EnvironmentDimensions47:
    width_m: float = 30.0
    length_m: float = 30.0
    height_m: float = 4.5

    @property
    def is_valid(self) -> bool:
        return self.width_m > 0.0 and self.length_m > 0.0 and self.height_m >= 3.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "width_m": self.width_m,
            "length_m": self.length_m,
            "height_m": self.height_m,
        }


@dataclass
class ModularEnvironmentSpecification:
    environment_id: str
    style: EnvironmentStyle47
    category: ModuleCategory47 = ModuleCategory47.STRUCTURAL
    dimensions: EnvironmentDimensions47 = field(default_factory=EnvironmentDimensions47)
    grid_snap_cm: float = 100.0
    module_count: int = 16
    has_collision: bool = True
    has_navigation: bool = True
    has_gameplay_anchors: bool = True
    seed: int = 42

    @property
    def is_valid_environment(self) -> bool:
        return (
            self.dimensions.is_valid and
            self.grid_snap_cm >= 10.0 and
            self.module_count >= 1 and
            self.has_collision and
            self.has_navigation and
            self.has_gameplay_anchors
        )

    @property
    def definition_hash(self) -> str:
        return CanonicalHasher.compute_hash(self.to_dict())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "environment_id": self.environment_id,
            "style": self.style.value,
            "category": self.category.value,
            "dimensions": self.dimensions.to_dict(),
            "grid_snap_cm": self.grid_snap_cm,
            "module_count": self.module_count,
            "has_collision": self.has_collision,
            "has_navigation": self.has_navigation,
            "has_gameplay_anchors": self.has_gameplay_anchors,
            "seed": self.seed,
        }
