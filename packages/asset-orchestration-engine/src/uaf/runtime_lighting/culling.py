"""
Light Culling (Frustum, Distance, Screen Influence) for UAF-81.85.
"""

from __future__ import annotations
import math
from dataclasses import dataclass
from typing import List, Tuple

from .lights import Light
from .directional import DirectionalLight
from .core import LightPriority


@dataclass
class SimpleFrustum:
    """Camera view frustum defined by position, forward, FOV, and aspect ratio."""
    position: Tuple[float, float, float]
    forward: Tuple[float, float, float]
    fov_rad: float
    aspect_ratio: float
    near_z: float = 0.1
    far_z: float = 500.0


class LightCuller:
    """
    Performs multi-stage culling for dynamic lights.
    """

    @staticmethod
    def cull_lights(
        lights: List[Light],
        frustum: SimpleFrustum,
        min_screen_size_px: float = 2.0,
        screen_height_px: int = 1080
    ) -> List[Light]:
        """
        Filters visible lights via distance, frustum containment, and screen size influence.
        Directional lights are never frustum-culled.
        """
        visible: List[Light] = []
        cam_pos = frustum.position
        cam_fwd = frustum.forward
        half_fov = frustum.fov_rad * 0.5
        cos_half_fov = math.cos(half_fov)

        for light in lights:
            if not light.visibility:
                continue

            # Directional lights illuminate the entire scene
            if isinstance(light, DirectionalLight):
                visible.append(light)
                continue

            # Distance culling
            dx = light.position[0] - cam_pos[0]
            dy = light.position[1] - cam_pos[1]
            dz = light.position[2] - cam_pos[2]
            dist_sq = dx * dx + dy * dy + dz * dz
            dist = math.sqrt(dist_sq)

            # Check if light influence sphere reaches camera or extends past far plane
            if dist > (frustum.far_z + light.range):
                continue

            # Frustum angle culling
            if dist > light.range:
                inv_dist = 1.0 / max(1e-4, dist)
                dir_to_light = (dx * inv_dist, dy * inv_dist, dz * inv_dist)
                cos_angle = dir_to_light[0] * cam_fwd[0] + dir_to_light[1] * cam_fwd[1] + dir_to_light[2] * cam_fwd[2]

                # Angular radius of the light sphere
                sin_light_cone = min(1.0, light.range * inv_dist)
                angular_radius = math.asin(sin_light_cone)

                # If completely behind frustum cone
                angle_to_light = math.acos(max(-1.0, min(1.0, cos_angle)))
                if (angle_to_light - angular_radius) > (half_fov * 1.5):  # generous aspect margin
                    continue

            # Screen size influence culling
            if dist > 0.0:
                projected_radius_px = (light.range / dist) * (screen_height_px / (2.0 * math.tan(half_fov)))
                if projected_radius_px < min_screen_size_px and light.priority == LightPriority.COSMETIC:
                    continue

            visible.append(light)

        return visible
