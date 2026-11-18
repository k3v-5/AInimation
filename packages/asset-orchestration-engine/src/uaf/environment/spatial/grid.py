"""
GridProfile, SnapCategory, and SnapPoint models.
UAF-81.12 Sections 8, 9, 11, 12, 13, 14, 15.
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional


class SnapCategory(str, Enum):
    WALL = "WALL"
    FLOOR = "FLOOR"
    CEILING = "CEILING"
    DOOR = "DOOR"
    WINDOW = "WINDOW"
    CORNER = "CORNER"
    STAIR = "STAIR"
    PIPE = "PIPE"
    ELECTRICAL = "ELECTRICAL"
    STRUCTURAL = "STRUCTURAL"
    GAMEPLAY = "GAMEPLAY"


@dataclass
class SnapPoint:
    snap_id: str
    position: List[float] = field(default_factory=lambda: [0.0, 0.0, 0.0])
    rotation: List[float] = field(default_factory=lambda: [0.0, 0.0, 0.0])
    direction: List[float] = field(default_factory=lambda: [0.0, 1.0, 0.0])
    category: SnapCategory = SnapCategory.WALL
    compatibility_tags: List[str] = field(default_factory=list)

    def is_compatible_with(self, other: "SnapPoint") -> bool:
        if self.category != other.category:
            return False
        if not self.compatibility_tags or not other.compatibility_tags:
            return True
        return bool(set(self.compatibility_tags) & set(other.compatibility_tags))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "snap_id": self.snap_id,
            "position": self.position,
            "rotation": self.rotation,
            "direction": self.direction,
            "category": self.category.value,
            "compatibility_tags": self.compatibility_tags,
        }


@dataclass
class GridProfile:
    unit_size_cm: float = 100.0
    subdivision: int = 4
    rotation_increment_deg: float = 90.0
    height_increment_cm: float = 300.0

    def snap_coordinate(self, value: float) -> float:
        step = self.unit_size_cm / 100.0  # meters
        return round(value / step) * step

    def to_dict(self) -> Dict[str, Any]:
        return {
            "unit_size_cm": self.unit_size_cm,
            "subdivision": self.subdivision,
            "rotation_increment_deg": self.rotation_increment_deg,
            "height_increment_cm": self.height_increment_cm,
        }
