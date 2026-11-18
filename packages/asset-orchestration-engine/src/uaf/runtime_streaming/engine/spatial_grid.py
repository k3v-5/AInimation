"""
Spatial Grid and Coordinate Partitioning Engine (UAF-81.81 Section 1).
Deterministic coordinate-to-cell mapping, multi-level hierarchy, neighbor queries,
bounding box spatial checks, and AABB intersection tests.
"""

from __future__ import annotations

import math
from typing import Dict, List, Optional, Set, Tuple

from ..models.definition import (
    CellBounds,
    CellKey,
)


class SpatialGrid:
    """
    Authoritative spatial partitioning grid.
    Translates continuous 3D world coordinates into discrete hierarchical CellKeys.
    """

    def __init__(
        self,
        base_cell_size: float = 64.0,
        scale_multiplier: float = 2.0,
        max_levels: int = 4,
    ):
        if base_cell_size <= 0.0:
            raise ValueError("base_cell_size must be strictly positive.")
        self.base_cell_size = float(base_cell_size)
        self.scale_multiplier = float(scale_multiplier)
        self.max_levels = int(max_levels)

    def get_cell_size_for_level(self, level: int) -> float:
        """Return the cubic dimension of a cell at the given hierarchy level."""
        return self.base_cell_size * (self.scale_multiplier ** max(0, level))

    def world_to_cell_key(self, position: Tuple[float, float, float], level: int = 0) -> CellKey:
        """Convert continuous 3D world coordinates into a discrete CellKey."""
        cell_size = self.get_cell_size_for_level(level)
        cx = math.floor(position[0] / cell_size)
        cy = math.floor(position[1] / cell_size)
        cz = math.floor(position[2] / cell_size)
        return CellKey(level=level, x=cx, y=cy, z=cz)

    def cell_key_to_bounds(self, key: CellKey) -> CellBounds:
        """Compute the continuous Axis-Aligned Bounding Box (AABB) for a CellKey."""
        cell_size = self.get_cell_size_for_level(key.level)
        min_x = key.x * cell_size
        min_y = key.y * cell_size
        min_z = key.z * cell_size
        max_x = min_x + cell_size
        max_y = min_y + cell_size
        max_z = min_z + cell_size
        return CellBounds(min_corner=(min_x, min_y, min_z), max_corner=(max_x, max_y, max_z))

    def get_neighbors(self, key: CellKey, radius: int = 1) -> List[CellKey]:
        """Return the Moore neighborhood (all surrounding cells within Chebyshev distance)."""
        if radius < 0:
            return []
        neighbors: List[CellKey] = []
        for dz in range(-radius, radius + 1):
            for dy in range(-radius, radius + 1):
                for dx in range(-radius, radius + 1):
                    if dx == 0 and dy == 0 and dz == 0:
                        continue
                    neighbors.append(CellKey(level=key.level, x=key.x + dx, y=key.y + dy, z=key.z + dz))
        return sorted(neighbors)

    def query_region(
        self,
        min_corner: Tuple[float, float, float],
        max_corner: Tuple[float, float, float],
        level: int = 0,
    ) -> List[CellKey]:
        """Return all CellKeys that overlap with the query AABB."""
        cell_size = self.get_cell_size_for_level(level)
        start_x = math.floor(min(min_corner[0], max_corner[0]) / cell_size)
        start_y = math.floor(min(min_corner[1], max_corner[1]) / cell_size)
        start_z = math.floor(min(min_corner[2], max_corner[2]) / cell_size)

        end_x = math.floor(max(min_corner[0], max_corner[0]) / cell_size)
        end_y = math.floor(max(min_corner[1], max_corner[1]) / cell_size)
        end_z = math.floor(max(min_corner[2], max_corner[2]) / cell_size)

        cells: List[CellKey] = []
        for z in range(start_z, end_z + 1):
            for y in range(start_y, end_y + 1):
                for x in range(start_x, end_x + 1):
                    cells.append(CellKey(level=level, x=x, y=y, z=z))
        return sorted(cells)

    def query_radius(
        self,
        center: Tuple[float, float, float],
        radius: float,
        level: int = 0,
    ) -> List[CellKey]:
        """Return all CellKeys whose bounds intersect a bounding sphere."""
        if radius <= 0.0:
            return [self.world_to_cell_key(center, level)]

        min_corner = (center[0] - radius, center[1] - radius, center[2] - radius)
        max_corner = (center[0] + radius, center[1] + radius, center[2] + radius)
        candidates = self.query_region(min_corner, max_corner, level)

        intersecting: List[CellKey] = []
        for key in candidates:
            bounds = self.cell_key_to_bounds(key)
            if bounds.closest_distance_to_point(center) <= radius:
                intersecting.append(key)
        return sorted(intersecting)

    def get_parent_key(self, key: CellKey) -> CellKey:
        """Return parent CellKey in the next hierarchical level (downsampled by multiplier)."""
        scale_int = int(self.scale_multiplier)
        px = key.x // scale_int
        py = key.y // scale_int
        pz = key.z // scale_int
        return CellKey(level=key.level + 1, x=px, y=py, z=pz)

    def get_child_keys(self, key: CellKey) -> List[CellKey]:
        """Return child CellKeys at the finer resolution level."""
        if key.level <= 0:
            return []
        scale_int = int(self.scale_multiplier)
        children: List[CellKey] = []
        start_x = key.x * scale_int
        start_y = key.y * scale_int
        start_z = key.z * scale_int
        for dz in range(scale_int):
            for dy in range(scale_int):
                for dx in range(scale_int):
                    children.append(CellKey(level=key.level - 1, x=start_x + dx, y=start_y + dy, z=start_z + dz))
        return sorted(children)
