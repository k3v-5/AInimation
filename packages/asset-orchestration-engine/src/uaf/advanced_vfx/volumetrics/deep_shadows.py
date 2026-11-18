"""
UAF-81.89.4: Volumetric Deep Shadow Maps and Beer-Lambert Transmittance.
Computes self-shadowing inside dense smoke clouds and explosion plumes.
"""

from __future__ import annotations

import math
from typing import List, Tuple
from ..fluids.grid3d import EulerianFluidGrid3D
from ..core.contracts import VolumetricShadowSettings, clamp_scalar


class DeepShadowMapper:
    """
    Computes volumetric self-shadowing through participating media using discretized Beer-Lambert extinction.
    """

    def __init__(self, settings: VolumetricShadowSettings = VolumetricShadowSettings()) -> None:
        self.settings: VolumetricShadowSettings = settings
        self.transmittance_grid: List[float] = []
        self.dims: Tuple[int, int, int] = (0, 0, 0)

    def bake_deep_shadow_grid(
        self,
        fluid_grid: EulerianFluidGrid3D,
        light_direction: Tuple[float, float, float] = (0.0, -1.0, 0.0), # Light pointing downwards
    ) -> List[float]:
        """
        Marches through the fluid density field opposite to light direction,
        accumulating optical depth and computing transmittance per cell.
        """
        w, h, d = fluid_grid.w, fluid_grid.h, fluid_grid.d
        self.dims = (w, h, d)
        sigma_t = self.settings.absorption_coefficient + self.settings.scattering_coefficient
        ds = fluid_grid.dx

        lx, ly, lz = light_direction
        mag = math.sqrt(lx * lx + ly * ly + lz * lz) + 1e-6
        # March towards the light (opposite of light direction)
        ray_x, ray_y, ray_z = -lx / mag, -ly / mag, -lz / mag

        self.transmittance_grid = [1.0] * (w * h * d)

        # For vertical sunlight (standard case), iterate from top to bottom
        if abs(ray_y) >= max(abs(ray_x), abs(ray_z)):
            y_range = range(h - 1, -1, -1) if ray_y > 0 else range(h)
            for z in range(d):
                for x in range(w):
                    optical_depth = 0.0
                    for y in y_range:
                        idx = fluid_grid._c_idx(x, y, z)
                        density = fluid_grid.density[idx]
                        if density > 0.001:
                            optical_depth += sigma_t * density * ds
                        # Beer-Lambert: T = exp(-optical_depth)
                        self.transmittance_grid[idx] = math.exp(-optical_depth)
        else:
            # Generalized raymarching along light vector for non-vertical lights
            for z in range(d):
                for y in range(h):
                    for x in range(w):
                        idx = fluid_grid._c_idx(x, y, z)
                        # March backwards toward the light source
                        curr_x, curr_y, curr_z = float(x), float(y), float(z)
                        optical_depth = 0.0
                        for _ in range(self.settings.num_slices):
                            curr_x += ray_x * self.settings.step_size
                            curr_y += ray_y * self.settings.step_size
                            curr_z += ray_z * self.settings.step_size

                            if not (0 <= curr_x < w and 0 <= curr_y < h and 0 <= curr_z < d):
                                break
                            sample_d = fluid_grid.sample_density_trilinear(curr_x, curr_y, curr_z)
                            optical_depth += sigma_t * sample_d * self.settings.step_size

                        self.transmittance_grid[idx] = math.exp(-optical_depth)

        return self.transmittance_grid

    def get_shadow_factor(self, x: int, y: int, z: int) -> float:
        """Returns light transmission factor [0.0 = total shadow, 1.0 = fully lit]."""
        w, h, d = self.dims
        if 0 <= x < w and 0 <= y < h and 0 <= z < d:
            idx = (z * h + y) * w + x
            return self.transmittance_grid[idx] if idx < len(self.transmittance_grid) else 1.0
        return 1.0
