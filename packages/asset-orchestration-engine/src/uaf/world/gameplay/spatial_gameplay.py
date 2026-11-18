"""
Spatial gameplay entities: Spawn points, Tactical Cover, and Mission Objectives.
UAF-81.6 Sections 57, 58, 59, 60, 61.
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional


class CoverType(str, Enum):
    FULL = "FULL"        # > 1.8m cover
    LOW = "LOW"          # ~ 1.0m crouch cover
    CROUCH = "CROUCH"
    CORNER = "CORNER"


@dataclass
class CoverDefinition:
    cover_id: str
    cover_type: CoverType
    position: List[float] = field(default_factory=lambda: [0.0, 0.0, 0.0])
    rotation: List[float] = field(default_factory=lambda: [0.0, 0.0, 0.0])
    height_meters: float = 1.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "cover_id": self.cover_id,
            "cover_type": self.cover_type.value,
            "position": self.position,
            "rotation": self.rotation,
            "height_meters": self.height_meters,
        }


@dataclass
class SpawnPoint:
    spawn_id: str
    team: str = "PLAYER"  # "PLAYER", "ENEMY", "NEUTRAL"
    position: List[float] = field(default_factory=lambda: [0.0, 0.0, 0.0])
    rotation: List[float] = field(default_factory=lambda: [0.0, 0.0, 0.0])
    is_safe: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "spawn_id": self.spawn_id,
            "team": self.team,
            "position": self.position,
            "rotation": self.rotation,
            "is_safe": self.is_safe,
        }


@dataclass
class ObjectiveDefinition:
    objective_id: str
    objective_type: str = "CAPTURE"  # "CAPTURE", "EXTRACT", "DESTROY", "SURVIVE"
    position: List[float] = field(default_factory=lambda: [0.0, 0.0, 0.0])
    radius_meters: float = 3.0
    priority: int = 1

    def to_dict(self) -> Dict[str, Any]:
        return {
            "objective_id": self.objective_id,
            "objective_type": self.objective_type,
            "position": self.position,
            "radius_meters": self.radius_meters,
            "priority": self.priority,
        }
