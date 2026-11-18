"""
UAF-81.83: Server-Side Lag Compensation and Historical Rewind Validation.
"""

from __future__ import annotations

import math
from typing import Any, Dict, Optional, Tuple

from ..models.definition import (
    NetworkEntityId,
    Vec3,
    ensure_finite_float,
    ensure_finite_vec3,
)
from .history_buffer import HistoryBuffer


class LagCompensator:
    """
    Validates client hit claims by rewinding authoritative entity positions
    to the exact server tick the client perceived at the time of firing.
    """

    def __init__(self, history_buffer: HistoryBuffer, max_rewind_ticks: int = 60):
        self.history = history_buffer
        self.max_rewind_ticks = max_rewind_ticks

    def is_rewind_tick_valid(self, current_tick: int, target_tick: int) -> bool:
        """Check if target tick is within permitted historical rewind window and not in the future."""
        if target_tick > current_tick:
            return False
        if current_tick - target_tick > self.max_rewind_ticks:
            return False
        return True

    def verify_proximity_hit(
        self,
        current_tick: int,
        target_tick: int,
        target_id: NetworkEntityId,
        impact_point: Vec3,
        tolerance_radius: float = 1.5,
    ) -> bool:
        """
        Verify if target entity was within tolerance_radius of impact_point at target_tick.
        """
        if not self.is_rewind_tick_valid(current_tick, target_tick):
            return False

        impact_point = ensure_finite_vec3(impact_point, "verify_proximity_hit")
        tolerance_radius = ensure_finite_float(tolerance_radius, "verify_proximity_hit")

        past_state = self.history.get_state_at_tick(target_tick)
        if not past_state or target_id not in past_state:
            return False

        target_props = past_state[target_id]
        pos = target_props.get("position")
        if not pos or not isinstance(pos, (list, tuple)) or len(pos) != 3:
            return False

        dx = pos[0] - impact_point[0]
        dy = pos[1] - impact_point[1]
        dz = pos[2] - impact_point[2]
        dist_sq = dx * dx + dy * dy + dz * dz

        return dist_sq <= (tolerance_radius * tolerance_radius)

    def verify_ray_hit(
        self,
        current_tick: int,
        target_tick: int,
        target_id: NetworkEntityId,
        ray_origin: Vec3,
        ray_direction: Vec3,
        max_range: float = 100.0,
        hitbox_radius: float = 1.0,
    ) -> bool:
        """
        Validate raycast hit against target bounding sphere in historical frame.
        """
        if not self.is_rewind_tick_valid(current_tick, target_tick):
            return False

        ray_origin = ensure_finite_vec3(ray_origin, "verify_ray_hit origin")
        ray_dir = ensure_finite_vec3(ray_direction, "verify_ray_hit dir")

        # Normalize direction
        mag = math.sqrt(ray_dir[0] ** 2 + ray_dir[1] ** 2 + ray_dir[2] ** 2)
        if mag <= 1e-6:
            return False
        d = (ray_dir[0] / mag, ray_dir[1] / mag, ray_dir[2] / mag)

        past_state = self.history.get_state_at_tick(target_tick)
        if not past_state or target_id not in past_state:
            return False

        target_pos = past_state[target_id].get("position")
        if not target_pos or len(target_pos) != 3:
            return False

        # Vector from ray origin to target center
        oc = (target_pos[0] - ray_origin[0], target_pos[1] - ray_origin[1], target_pos[2] - ray_origin[2])
        proj = oc[0] * d[0] + oc[1] * d[1] + oc[2] * d[2]

        if proj < 0.0 or proj > max_range:
            return False  # Target behind ray or beyond range

        # Distance from target center to closest point on ray
        closest = (
            ray_origin[0] + d[0] * proj,
            ray_origin[1] + d[1] * proj,
            ray_origin[2] + d[2] * proj,
        )
        dist_sq = (
            (target_pos[0] - closest[0]) ** 2
            + (target_pos[1] - closest[1]) ** 2
            + (target_pos[2] - closest[2]) ** 2
        )

        return dist_sq <= (hitbox_radius * hitbox_radius)
