"""
UAF-81.82: Spatial Navigation Tiles and UAF-81.81 Streaming Integration.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional, Set, Tuple

from ..models.definition import Vec3


@dataclass
class NavTile:
    """
    Spatial partition of a NavMesh corresponding directly to a world grid cell.
    Maintains revision tracking for path invalidation and residency status for streaming.
    """
    tile_x: int
    tile_y: int
    bounds: Tuple[Vec3, Vec3]  # (min_corner, max_corner)
    polygon_ids: Set[int] = field(default_factory=set)
    revision: int = 0
    is_resident: bool = True
    level: int = 0

    @property
    def tile_key(self) -> Tuple[int, int, int]:
        return (self.level, self.tile_x, self.tile_y)

    def add_polygon(self, polygon_id: int) -> None:
        self.polygon_ids.add(polygon_id)
        self.revision += 1

    def remove_polygon(self, polygon_id: int) -> None:
        if polygon_id in self.polygon_ids:
            self.polygon_ids.remove(polygon_id)
            self.revision += 1

    def set_resident(self, resident: bool) -> None:
        if self.is_resident != resident:
            self.is_resident = resident
            self.revision += 1

    def contains_point_2d(self, p: Vec3) -> bool:
        min_c, max_c = self.bounds
        return min_c[0] <= p[0] <= max_c[0] and min_c[2] <= p[2] <= max_c[2]
