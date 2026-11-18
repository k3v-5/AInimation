"""
Cascaded Shadow Maps (CSM) Calculations & Texel Snapping for UAF-81.85.
"""

from __future__ import annotations
import math
from dataclasses import dataclass
from typing import List, Tuple


@dataclass
class CascadeSlice:
    """Represents a single cascade in CSM."""
    cascade_index: int
    near_distance: float
    far_distance: float
    split_distance: float
    bounding_radius: float
    texel_size: float
    center: Tuple[float, float, float]
    ortho_bounds: Tuple[float, float, float, float]  # min_x, max_x, min_y, max_y


class CSMCalculator:
    """
    Computes deterministic cascade splits and stabilized bounding boxes for directional lights.
    """

    @staticmethod
    def compute_splits(
        near_z: float,
        far_z: float,
        cascade_count: int,
        lambda_factor: float = 0.8
    ) -> List[float]:
        """
        Computes cascade split distances using the Practical Split Scheme (PSSM),
        blending logarithmic and uniform distributions.
        """
        near = max(0.1, float(near_z))
        far = max(near + 1.0, float(far_z))
        count = max(1, int(cascade_count))
        lam = max(0.0, min(1.0, float(lambda_factor)))

        splits: List[float] = [near]
        ratio = far / near

        for i in range(1, count):
            p = float(i) / float(count)
            log_split = near * (ratio ** p)
            uniform_split = near + (far - near) * p
            split = lam * log_split + (1.0 - lam) * uniform_split
            splits.append(round(split, 4))

        splits.append(far)
        return splits

    @staticmethod
    def calculate_slices(
        camera_fov_rad: float,
        aspect_ratio: float,
        camera_pos: Tuple[float, float, float],
        camera_forward: Tuple[float, float, float],
        splits: List[float],
        shadow_map_resolution: int = 1024
    ) -> List[CascadeSlice]:
        """
        Generates stabilized cascade slices with texel snapping.
        """
        slices: List[CascadeSlice] = []
        tan_half_fov = math.tan(camera_fov_rad * 0.5)

        for i in range(len(splits) - 1):
            near_d = splits[i]
            far_d = splits[i + 1]

            # Approximate bounding sphere of the frustum slice
            mid_d = (near_d + far_d) * 0.5
            half_depth = (far_d - near_d) * 0.5
            half_height = far_d * tan_half_fov
            half_width = half_height * aspect_ratio

            radius = math.sqrt(half_depth * half_depth + half_width * half_width + half_height * half_height)
            center = (
                camera_pos[0] + camera_forward[0] * mid_d,
                camera_pos[1] + camera_forward[1] * mid_d,
                camera_pos[2] + camera_forward[2] * mid_d,
            )

            # Texel size for stabilization
            world_size = radius * 2.0
            texel_size = world_size / float(shadow_map_resolution)

            # Snap center to world-space texel grid to avoid shimmering
            snapped_center = (
                math.floor(center[0] / texel_size + 0.5) * texel_size,
                math.floor(center[1] / texel_size + 0.5) * texel_size,
                math.floor(center[2] / texel_size + 0.5) * texel_size,
            )

            slice_obj = CascadeSlice(
                cascade_index=i,
                near_distance=near_d,
                far_distance=far_d,
                split_distance=far_d,
                bounding_radius=round(radius, 4),
                texel_size=round(texel_size, 6),
                center=snapped_center,
                ortho_bounds=(-radius, radius, -radius, radius),
            )
            slices.append(slice_obj)

        return slices
