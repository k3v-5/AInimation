"""
PivotDefinition, PivotType, and OriginPolicy models.
UAF-81.8 Sections 10, 11, 12, 13.
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional


class PivotType(str, Enum):
    CENTER = "CENTER"
    BOTTOM = "BOTTOM"
    ORIGIN = "ORIGIN"
    ROOT = "ROOT"
    CUSTOM = "CUSTOM"
    SOCKET = "SOCKET"


class OriginPolicy(str, Enum):
    FEET_ROOT = "FEET_ROOT"      # Characters / Creatures
    GRIP = "GRIP"                # Weapons / Tools
    BASE = "BASE"                # Props / Furniture
    FOUNDATION = "FOUNDATION"    # Buildings / Structures
    CHASSIS_ROOT = "CHASSIS_ROOT"# Vehicles
    CENTER_MASS = "CENTER_MASS"  # Projectiles / Debris


@dataclass
class PivotDefinition:
    pivot_type: PivotType = PivotType.BOTTOM
    position: List[float] = field(default_factory=lambda: [0.0, 0.0, 0.0])
    orientation: List[float] = field(default_factory=lambda: [0.0, 0.0, 0.0])  # Euler degrees
    origin_policy: OriginPolicy = OriginPolicy.BASE

    def to_dict(self) -> Dict[str, Any]:
        return {
            "pivot_type": self.pivot_type.value,
            "position": self.position,
            "orientation": self.orientation,
            "origin_policy": self.origin_policy.value,
        }
