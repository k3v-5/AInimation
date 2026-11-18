"""
NaturalLandmark and LandmarkType models.
UAF-81.13 Sections 32, 33, 34.
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import List, Dict, Any


class LandmarkType(str, Enum):
    MOUNTAIN = "MOUNTAIN"
    CLIFF = "CLIFF"
    MONOLITH = "MONOLITH"
    RUIN = "RUIN"
    CRATER = "CRATER"
    LAKE = "LAKE"
    NATURAL_FORMATION = "NATURAL_FORMATION"


@dataclass
class NaturalLandmark:
    landmark_id: str
    landmark_type: LandmarkType
    position: List[float] = field(default_factory=lambda: [0.0, 0.0, 0.0])
    scale: List[float] = field(default_factory=lambda: [1.0, 1.0, 1.0])
    prominence: float = 1.0  # Visual significance 0.0 to 1.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "landmark_id": self.landmark_id,
            "landmark_type": self.landmark_type.value,
            "position": self.position,
            "scale": self.scale,
            "prominence": self.prominence,
        }
