"""
Lighting LOD & Update Frequency for UAF-81.85.
"""

from __future__ import annotations
import math
from typing import Tuple

from .core import UpdateFrequency, LightPriority
from .lights import Light


class LightingLODManager:
    """
    Evaluates LOD and update frequency policies for dynamic lights based on camera distance and priority.
    """

    @staticmethod
    def evaluate_update_frequency(
        light: Light,
        camera_pos: Tuple[float, float, float]
    ) -> UpdateFrequency:
        """Determines how frequently the light and its shadows should be refreshed."""
        if light.priority == LightPriority.CRITICAL:
            return UpdateFrequency.EVERY_FRAME

        dx = light.position[0] - camera_pos[0]
        dy = light.position[1] - camera_pos[1]
        dz = light.position[2] - camera_pos[2]
        dist = math.sqrt(dx * dx + dy * dy + dz * dz)

        if dist < 20.0:
            return UpdateFrequency.EVERY_FRAME
        elif dist < 50.0:
            return UpdateFrequency.EVERY_2_FRAMES
        elif dist < 100.0:
            return UpdateFrequency.EVERY_4_FRAMES
        else:
            return UpdateFrequency.EVENT_DRIVEN

    @staticmethod
    def evaluate_shadow_resolution_scale(
        light: Light,
        camera_pos: Tuple[float, float, float]
    ) -> float:
        """Computes distance-based shadow resolution multiplier."""
        if light.priority == LightPriority.CRITICAL:
            return 1.0

        dx = light.position[0] - camera_pos[0]
        dy = light.position[1] - camera_pos[1]
        dz = light.position[2] - camera_pos[2]
        dist = math.sqrt(dx * dx + dy * dy + dz * dz)

        if dist < 25.0:
            return 1.0
        elif dist < 60.0:
            return 0.5
        else:
            return 0.25
