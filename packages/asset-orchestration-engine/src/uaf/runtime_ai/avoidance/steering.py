"""
UAF-81.82: Kinematic Steering Behaviors (Seek, Arrive, Path Following).
"""

from __future__ import annotations

import math
from typing import Sequence, Tuple

from ..models.definition import (
    AgentKinematics,
    Vec3,
    ensure_finite_vec3,
    vec3_add,
    vec3_distance,
    vec3_length,
    vec3_normalize,
    vec3_scale,
    vec3_sub,
)


class SteeringController:
    """Calculates preferred velocities using kinematic steering behaviors."""

    @staticmethod
    def seek(position: Vec3, target: Vec3, max_speed: float) -> Vec3:
        """Direct seek towards target at max_speed."""
        diff = vec3_sub(target, position)
        # Keep horizontal steering primarily, maintaining height Y
        dir_norm = vec3_normalize(diff)
        res = vec3_scale(dir_norm, max_speed)
        return ensure_finite_vec3(res, "SteeringController.seek")

    @staticmethod
    def arrive(
        position: Vec3,
        target: Vec3,
        max_speed: float,
        slowing_radius: float = 2.0,
        stopping_distance: float = 0.1,
    ) -> Vec3:
        """Seek with smooth deceleration within slowing_radius."""
        diff = vec3_sub(target, position)
        dist = vec3_length(diff)
        if dist <= stopping_distance:
            return (0.0, 0.0, 0.0)

        dir_norm = vec3_normalize(diff)
        if dist < slowing_radius:
            target_speed = max_speed * (dist / max(1e-5, slowing_radius))
        else:
            target_speed = max_speed

        res = vec3_scale(dir_norm, target_speed)
        return ensure_finite_vec3(res, "SteeringController.arrive")

    @staticmethod
    def follow_path(
        position: Vec3,
        waypoints: Sequence[Vec3],
        current_index: int,
        max_speed: float,
        waypoint_radius: float = 0.5,
    ) -> Tuple[Vec3, int]:
        """
        Advance along waypoints. Returns (preferred_velocity, new_waypoint_index).
        """
        if not waypoints:
            return ((0.0, 0.0, 0.0), 0)

        idx = max(0, min(current_index, len(waypoints) - 1))

        # Check if reached current waypoint
        while idx < len(waypoints) - 1:
            dist = vec3_distance(position, waypoints[idx])
            if dist <= waypoint_radius:
                idx += 1
            else:
                break

        target = waypoints[idx]
        is_last = (idx == len(waypoints) - 1)

        if is_last:
            vel = SteeringController.arrive(position, target, max_speed, slowing_radius=1.5)
        else:
            vel = SteeringController.seek(position, target, max_speed)

        return (ensure_finite_vec3(vel, "SteeringController.follow_path"), idx)
