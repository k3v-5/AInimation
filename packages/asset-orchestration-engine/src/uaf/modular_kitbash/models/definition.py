"""
ModuleType39, PivotType39, SnapMode39, KitStyle39, ModuleDimensions39, ModularKitbashSpecification models.
UAF-81.39 Sections 5, 6, 7, 8, 10, 13, 16, 17, 136, 144.
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from ...core.hashing.canonical_hasher import CanonicalHasher


class ModuleType39(str, Enum):
    WALL = "WALL"
    FLOOR = "FLOOR"
    CEILING = "CEILING"
    ROOF = "ROOF"
    DOOR = "DOOR"
    WINDOW = "WINDOW"
    STAIR = "STAIR"
    RAMP = "RAMP"
    COLUMN = "COLUMN"
    PILLAR = "PILLAR"
    BEAM = "BEAM"
    FRAME = "FRAME"
    PANEL = "PANEL"
    CORRIDOR = "CORRIDOR"
    ROOM = "ROOM"
    PLATFORM = "PLATFORM"
    BRIDGE = "BRIDGE"
    PIPE = "PIPE"
    VENT = "VENT"
    COVER = "COVER"
    BARRIER = "BARRIER"
    FENCE = "FENCE"
    PROP_ANCHOR = "PROP_ANCHOR"
    DECORATION = "DECORATION"


class PivotType39(str, Enum):
    CENTER = "CENTER"
    BASE_CENTER = "BASE_CENTER"
    BASE_LEFT = "BASE_LEFT"
    BASE_RIGHT = "BASE_RIGHT"
    CUSTOM = "CUSTOM"


class SnapMode39(str, Enum):
    GRID = "GRID"
    SOCKET = "SOCKET"
    EDGE = "EDGE"
    FACE = "FACE"
    CENTER = "CENTER"
    CUSTOM = "CUSTOM"


class KitStyle39(str, Enum):
    SCI_FI_KIT = "SCI_FI_KIT"
    INDUSTRIAL_KIT = "INDUSTRIAL_KIT"
    MILITARY_KIT = "MILITARY_KIT"
    LAB_KIT = "LAB_KIT"
    URBAN_KIT = "URBAN_KIT"
    UNDERGROUND_KIT = "UNDERGROUND_KIT"


@dataclass
class ModuleDimensions39:
    width_cm: float = 200.0
    depth_cm: float = 20.0
    height_cm: float = 300.0

    @property
    def is_valid(self) -> bool:
        return self.width_cm > 0.0 and self.depth_cm > 0.0 and self.height_cm > 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "width_cm": self.width_cm,
            "depth_cm": self.depth_cm,
            "height_cm": self.height_cm,
        }


@dataclass
class ModularKitbashSpecification:
    kitbash_id: str
    kit_style: KitStyle39
    root_type: ModuleType39
    dimensions: ModuleDimensions39 = field(default_factory=ModuleDimensions39)
    pivot: PivotType39 = PivotType39.BASE_CENTER
    snap_mode: SnapMode39 = SnapMode39.GRID
    grid_snap_size_cm: float = 100.0
    socket_count: int = 4
    module_count: int = 1
    seed: int = 42

    @property
    def is_valid_structure(self) -> bool:
        return (
            self.dimensions.is_valid and
            self.grid_snap_size_cm >= 10.0 and
            self.socket_count >= 1 and
            self.module_count >= 1
        )

    @property
    def definition_hash(self) -> str:
        return CanonicalHasher.compute_hash(self.to_dict())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "kitbash_id": self.kitbash_id,
            "kit_style": self.kit_style.value,
            "root_type": self.root_type.value,
            "dimensions": self.dimensions.to_dict(),
            "pivot": self.pivot.value,
            "snap_mode": self.snap_mode.value,
            "grid_snap_size_cm": self.grid_snap_size_cm,
            "socket_count": self.socket_count,
            "module_count": self.module_count,
            "seed": self.seed,
        }
