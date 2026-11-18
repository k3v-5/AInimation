"""
UAF-81.89.3: Dynamic Foliage and Vegetation Interaction Buffer.
Simulates spring-damper vegetation deflection from explosive shockwaves and character movement.
"""

from __future__ import annotations

import math
from typing import List, Tuple
from ..core.contracts import clamp_scalar


class FoliageInteractionBuffer:
    """
    World-space 2D interactive buffer for procedural grass and foliage bending.
    Models damped harmonic oscillators per cell to create springy, responsive vegetation.
    """

    def __init__(
        self,
        world_bounds: Tuple[float, float, float, float] = (-50.0, -50.0, 50.0, 50.0),
        resolution: int = 64,
        spring_frequency: float = 12.0,
        damping_ratio: float = 0.6,
    ) -> None:
        self.min_x, self.min_z, self.max_x, self.max_z = world_bounds
        self.res: int = resolution
        self.cell_w: float = (self.max_x - self.min_x) / float(self.res)
        self.cell_h: float = (self.max_z - self.min_z) / float(self.res)

        self.omega_sq: float = spring_frequency * spring_frequency
        self.two_zeta_omega: float = 2.0 * damping_ratio * spring_frequency

        num_cells = self.res * self.res
        self.disp_x: List[float] = [0.0] * num_cells
        self.disp_z: List[float] = [0.0] * num_cells
        self.vel_x: List[float] = [0.0] * num_cells
        self.vel_z: List[float] = [0.0] * num_cells

    def _world_to_grid(self, wx: float, wz: float) -> Tuple[int, int]:
        gx = int((wx - self.min_x) / self.cell_w)
        gz = int((wz - self.min_z) / self.cell_h)
        return max(0, min(self.res - 1, gx)), max(0, min(self.res - 1, gz))

    def _idx(self, gx: int, gz: int) -> int:
        return gz * self.res + gx

    def apply_shockwave(self, center_x: float, center_z: float, radius: float, force: float = 5.0) -> None:
        """Injects an outward radial blast force bending all surrounding vegetation."""
        min_gx, min_gz = self._world_to_grid(center_x - radius, center_z - radius)
        max_gx, max_gz = self._world_to_grid(center_x + radius, center_z + radius)

        for gz in range(min_gz, max_gz + 1):
            wz = self.min_z + (gz + 0.5) * self.cell_h
            for gx in range(min_gx, max_gx + 1):
                wx = self.min_x + (gx + 0.5) * self.cell_w
                dx = wx - center_x
                dz = wz - center_z
                dist = math.sqrt(dx * dx + dz * dz)
                if 0.001 < dist <= radius:
                    falloff = (1.0 - dist / radius) * force
                    dir_x = dx / dist
                    dir_z = dz / dist
                    idx = self._idx(gx, gz)
                    # Add outward velocity impulse
                    self.vel_x[idx] += dir_x * falloff
                    self.vel_z[idx] += dir_z * falloff

    def update(self, dt: float) -> None:
        """
        Integrates damped spring equation: a = -omega^2 * x - 2*zeta*omega * v.
        """
        safe_dt = min(0.05, max(0.0001, dt))
        for i in range(len(self.disp_x)):
            # X component
            ax = -self.omega_sq * self.disp_x[i] - self.two_zeta_omega * self.vel_x[i]
            self.vel_x[i] += ax * safe_dt
            self.disp_x[i] += self.vel_x[i] * safe_dt

            # Z component
            az = -self.omega_sq * self.disp_z[i] - self.two_zeta_omega * self.vel_z[i]
            self.vel_z[i] += az * safe_dt
            self.disp_z[i] += self.vel_z[i] * safe_dt

    def sample_deflection(self, wx: float, wz: float) -> Tuple[float, float]:
        """Returns horizontal foliage bending vector (dx, dz) for rendering."""
        gx, gz = self._world_to_grid(wx, wz)
        idx = self._idx(gx, gz)
        return self.disp_x[idx], self.disp_z[idx]
