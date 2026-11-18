"""
WorldGrid defines spatial quantization, snapping intervals, and orientation increments.
UAF-81.6 Sections 5, 6.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Tuple


@dataclass
class WorldGrid:
    grid_size_meters: float = 2.0
    snap_increment_meters: float = 0.5
    rotation_increment_degrees: float = 90.0
    height_increment_meters: float = 3.0  # standard floor height
    major_grid_meters: float = 10.0
    minor_grid_meters: float = 1.0

    def snap_position(self, position: List[float]) -> List[float]:
        inc = self.snap_increment_meters
        h_inc = self.height_increment_meters
        return [
            round(position[0] / inc) * inc,
            round(position[1] / inc) * inc,
            round(position[2] / h_inc) * h_inc,
        ]

    def snap_rotation(self, yaw_degrees: float) -> float:
        inc = self.rotation_increment_degrees
        return round(yaw_degrees / inc) * inc

    def to_dict(self) -> Dict[str, Any]:
        return {
            "grid_size_meters": self.grid_size_meters,
            "snap_increment_meters": self.snap_increment_meters,
            "rotation_increment_degrees": self.rotation_increment_degrees,
            "height_increment_meters": self.height_increment_meters,
            "major_grid_meters": self.major_grid_meters,
            "minor_grid_meters": self.minor_grid_meters,
        }
