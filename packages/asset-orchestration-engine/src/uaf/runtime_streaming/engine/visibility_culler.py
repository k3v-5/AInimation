"""
Visibility and Frustum Culling Engine (UAF-81.81 Section 8).
Decoupled geometric cone and frustum tests with deterministic visibility caching.
"""

from __future__ import annotations

import math
from typing import Dict, Tuple

from ..models.definition import (
    CellBounds,
    CellKey,
    ObserverState,
)


class VisibilityCuller:
    """
    Pure geometric visibility culler.
    Evaluates view-cone, distance attenuation, and directional alignment without GPU context.
    """

    def __init__(self):
        self._cache: Dict[Tuple[CellKey, int], bool] = {}  # (CellKey, observer_hash) -> visible

    def is_bounds_visible(self, bounds: CellBounds, observer: ObserverState) -> bool:
        """Check if an AABB intersects the observer's viewing cone / frustum."""
        center = bounds.center()
        extents = bounds.extents()
        radius = math.sqrt(extents[0] ** 2 + extents[1] ** 2 + extents[2] ** 2)

        # Vector from observer to center
        to_center = (
            center[0] - observer.position[0],
            center[1] - observer.position[1],
            center[2] - observer.position[2],
        )
        dist = math.sqrt(to_center[0] ** 2 + to_center[1] ** 2 + to_center[2] ** 2)

        # Distance culling
        if dist - radius > observer.view_distance:
            return False

        # If observer is inside or very close to bounds
        if dist <= radius:
            return True

        # Directional test
        norm_dir = (to_center[0] / dist, to_center[1] / dist, to_center[2] / dist)
        dot = (
            observer.forward[0] * norm_dir[0]
            + observer.forward[1] * norm_dir[1]
            + observer.forward[2] * norm_dir[2]
        )

        half_fov_rad = math.radians(observer.fov_degrees * 0.5)
        # Angular expansion for bounding sphere
        angular_radius = math.asin(min(1.0, radius / dist))
        effective_min_dot = math.cos(min(math.pi, half_fov_rad + angular_radius))

        return dot >= effective_min_dot
