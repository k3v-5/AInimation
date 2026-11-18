"""
EnvironmentType50, ModularPieceType50, AssemblyDimensions50, ModularAssemblySpecification models.
UAF-81.50 Sections 4, 5, 8, 12, 149, 151.
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from ...core.hashing.canonical_hasher import CanonicalHasher


class EnvironmentType50(str, Enum):
    INTERIOR = "INTERIOR"
    EXTERIOR = "EXTERIOR"
    URBAN = "URBAN"
    INDUSTRIAL = "INDUSTRIAL"
    SCI_FI = "SCI_FI"
    MILITARY = "MILITARY"
    DUNGEON = "DUNGEON"
    FACILITY = "FACILITY"
    CITY_BLOCK = "CITY_BLOCK"
    BASE = "BASE"
    COMPOUND = "COMPOUND"
    NATURAL = "NATURAL"
    HYBRID = "HYBRID"
    CUSTOM = "CUSTOM"


class ModularPieceType50(str, Enum):
    WALL = "WALL"
    FLOOR = "FLOOR"
    CEILING = "CEILING"
    ROOF = "ROOF"
    CORNER = "CORNER"
    COLUMN = "COLUMN"
    BEAM = "BEAM"
    PILLAR = "PILLAR"
    DOOR_FRAME = "DOOR_FRAME"
    WINDOW_FRAME = "WINDOW_FRAME"
    STAIR = "STAIR"
    RAMP = "RAMP"
    PLATFORM = "PLATFORM"
    BRIDGE = "BRIDGE"
    PIPE = "PIPE"
    RAILING = "RAILING"
    FENCE = "FENCE"


@dataclass
class AssemblyDimensions50:
    width_m: float = 30.0
    length_m: float = 30.0
    height_m: float = 6.0

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
class ModularAssemblySpecification:
    environment_id: str
    environment_type: EnvironmentType50
    dimensions: AssemblyDimensions50 = field(default_factory=AssemblyDimensions50)
    grid_snap_cm: float = 50.0
    module_count: int = 32
    has_collision: bool = True
    has_navigation: bool = True
    has_lighting: bool = True
    has_world_partition: bool = True
    seed: int = 42

    @property
    def is_valid_assembly(self) -> bool:
        return (
            self.dimensions.is_valid and
            self.grid_snap_cm >= 10.0 and
            self.module_count >= 1 and
            self.has_collision and
            self.has_navigation and
            self.has_lighting and
            self.has_world_partition
        )

    @property
    def definition_hash(self) -> str:
        return CanonicalHasher.compute_hash(self.to_dict())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "environment_id": self.environment_id,
            "environment_type": self.environment_type.value,
            "dimensions": self.dimensions.to_dict(),
            "grid_snap_cm": self.grid_snap_cm,
            "module_count": self.module_count,
            "has_collision": self.has_collision,
            "has_navigation": self.has_navigation,
            "has_lighting": self.has_lighting,
            "has_world_partition": self.has_world_partition,
            "seed": self.seed,
        }
