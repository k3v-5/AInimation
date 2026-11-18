"""
UAF-81.82: Reciprocal Velocity Obstacles (RVO) Geometric Primitives.
"""

from __future__ import annotations

import math
from typing import Tuple

from ..models.definition import Vec3, vec3_distance, vec3_dot, vec3_length, vec3_scale, vec3_sub


class RVOPrimitive:
    """
    RVO cone evaluation in horizontal plane (X, Z).
    """

    @staticmethod
    def is_in_collision_cone(
        pos_a: Vec3,
        vel_a: Vec3,
        radius_a: float,
        pos_b: Vec3,
        vel_b: Vec3,
        radius_b: float,
        time_horizon: float = 2.0,
    ) -> bool:
        """
        Check if velocity vel_a leads to collision with agent b within time_horizon.
        """
        rel_pos = (pos_b[0] - pos_a[0], 0.0, pos_b[2] - pos_a[2])
        dist = math.sqrt(rel_pos[0] * rel_pos[0] + rel_pos[2] * rel_pos[2])
        combined_radius = radius_a + radius_b

        # Already overlapping
        if dist <= combined_radius:
            return True

        # RVO relative velocity: v_rel = 2 * v_a - (v_a + v_b) = v_a - v_b
        rel_vel = (vel_a[0] - vel_b[0], 0.0, vel_a[2] - vel_b[2])

        # Ray-sphere intersection along rel_vel over time [0, time_horizon]
        vel_speed_sq = rel_vel[0] * rel_vel[0] + rel_vel[2] * rel_vel[2]
        if vel_speed_sq < 1e-8:
            return False

        # Projection of rel_pos onto rel_vel
        dot_pv = rel_pos[0] * rel_vel[0] + rel_pos[2] * rel_vel[2]
        if dot_pv <= 0.0:
            return False  # Moving away

        t_closest = dot_pv / vel_speed_sq
        if t_closest > time_horizon:
            return False

        closest_dist_sq = (dist * dist) - (dot_pv * dot_pv / vel_speed_sq)
        return closest_dist_sq <= (combined_radius * combined_radius)
