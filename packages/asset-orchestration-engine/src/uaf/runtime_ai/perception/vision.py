"""
UAF-81.82: Vision Sensor (Range, FOV Cone, and Line-Of-Sight Raycasting).
"""

from __future__ import annotations

import math
from typing import Callable, Optional

from ..models.definition import (
    Vec3,
    vec3_distance,
    vec3_dot,
    vec3_normalize,
    vec3_sub,
)


class VisionSensor:
    """
    Simulates optical perception via range checks, angular field-of-view tests,
    and optional physical line-of-sight raycasting.
    """

    def __init__(
        self,
        vision_range: float = 30.0,
        vision_angle_degrees: float = 120.0,
        line_of_sight_required: bool = True,
    ):
        self.vision_range = vision_range
        self.vision_angle_degrees = vision_angle_degrees
        self.line_of_sight_required = line_of_sight_required
        # Precompute cosine of half angle
        half_rad = math.radians(vision_angle_degrees * 0.5)
        self._min_cos = math.cos(half_rad)

    def can_see(
        self,
        observer_position: Vec3,
        observer_forward: Vec3,
        target_position: Vec3,
        raycast_fn: Optional[Callable[[Vec3, Vec3, float], bool]] = None,
    ) -> bool:
        """
        Evaluate visibility of target from observer.
        raycast_fn(origin, direction, max_dist) -> returns True if path is blocked by geometry.
        """
        dist = vec3_distance(observer_position, target_position)
        if dist > self.vision_range:
            return False

        # Target at observer origin is visible
        if dist < 1e-4:
            return True

        # Field-of-view angle test in horizontal plane XZ
        to_target = vec3_sub(target_position, observer_position)
        to_target_dir = vec3_normalize((to_target[0], 0.0, to_target[2]))
        forward_dir = vec3_normalize((observer_forward[0], 0.0, observer_forward[2]))

        cos_angle = vec3_dot(forward_dir, to_target_dir)
        if cos_angle < self._min_cos:
            return False

        # Line of Sight check
        if self.line_of_sight_required and raycast_fn is not None:
            dir_3d = vec3_normalize(to_target)
            is_blocked = raycast_fn(observer_position, dir_3d, dist)
            if is_blocked:
                return False

        return True
