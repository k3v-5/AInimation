"""
Bounding volumes (AABB, OBB, BoundingSphere) for collision, culling, and validation.
UAF-81.3 Section 67.
"""

import math
from dataclasses import dataclass, field
from typing import List, Dict, Any


@dataclass
class AABB:
    """Axis-Aligned Bounding Box."""
    min_point: List[float] = field(default_factory=lambda: [0.0, 0.0, 0.0])
    max_point: List[float] = field(default_factory=lambda: [0.0, 0.0, 0.0])

    @property
    def dimensions(self) -> List[float]:
        return [
            self.max_point[0] - self.min_point[0],
            self.max_point[1] - self.min_point[1],
            self.max_point[2] - self.min_point[2],
        ]

    @property
    def center(self) -> List[float]:
        return [
            (self.min_point[0] + self.max_point[0]) / 2.0,
            (self.min_point[1] + self.max_point[1]) / 2.0,
            (self.min_point[2] + self.max_point[2]) / 2.0,
        ]

    def intersects(self, other: "AABB") -> bool:
        return (
            self.min_point[0] <= other.max_point[0] and self.max_point[0] >= other.min_point[0] and
            self.min_point[1] <= other.max_point[1] and self.max_point[1] >= other.min_point[1] and
            self.min_point[2] <= other.max_point[2] and self.max_point[2] >= other.min_point[2]
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "min_point": self.min_point,
            "max_point": self.max_point,
            "dimensions": self.dimensions,
            "center": self.center,
        }

    @classmethod
    def from_points(cls, points: List[List[float]]) -> "AABB":
        if not points:
            return cls([0.0, 0.0, 0.0], [0.0, 0.0, 0.0])
        min_p = [min(p[0] for p in points), min(p[1] for p in points), min(p[2] for p in points)]
        max_p = [max(p[0] for p in points), max(p[1] for p in points), max(p[2] for p in points)]
        return cls(min_p, max_p)


@dataclass
class BoundingSphere:
    center: List[float] = field(default_factory=lambda: [0.0, 0.0, 0.0])
    radius: float = 1.0

    def to_dict(self) -> Dict[str, Any]:
        return {"center": self.center, "radius": self.radius}
