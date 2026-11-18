"""
UAF-81.89.3: Persistent Surface Modification and Slope Flow Simulation.
Simulates persistent scorch marks, fluid puddles, liquid slope advection, and material weathering.
"""

from __future__ import annotations

import math
from typing import List, Tuple
from ..core.contracts import (
    SurfaceImpactEvent,
    DisplacementChannel,
    clamp_scalar,
    ensure_finite_vec3,
)


class PersistentSurfaceManager:
    """
    Manages persistent runtime surface alterations (burns, blood, acid, mud).
    Simulates thermal cooling, fluid diffusion, and tangential gravity slope runoff.
    """

    def __init__(
        self,
        world_bounds: Tuple[float, float, float, float] = (-50.0, -50.0, 50.0, 50.0), # min_x, min_z, max_x, max_z
        resolution: int = 128,
        burn_cool_rate: float = 0.05,
        liquid_evap_rate: float = 0.02,
    ) -> None:
        self.min_x, self.min_z, self.max_x, self.max_z = world_bounds
        self.res: int = resolution
        self.cell_w: float = (self.max_x - self.min_x) / float(self.res)
        self.cell_h: float = (self.max_z - self.min_z) / float(self.res)

        self.burn_cool_rate: float = burn_cool_rate
        self.liquid_evap_rate: float = liquid_evap_rate

        total_cells = self.res * self.res
        self.burn_map: List[float] = [0.0] * total_cells
        self.liquid_map: List[float] = [0.0] * total_cells

    def _world_to_grid(self, wx: float, wz: float) -> Tuple[int, int]:
        gx = int((wx - self.min_x) / self.cell_w)
        gz = int((wz - self.min_z) / self.cell_h)
        return max(0, min(self.res - 1, gx)), max(0, min(self.res - 1, gz))

    def _idx(self, gx: int, gz: int) -> int:
        return gz * self.res + gx

    def apply_impact(self, event: SurfaceImpactEvent) -> None:
        """Applies an impact to the persistent surface buffer (burns, splashes)."""
        wx, wy, wz = event.world_position
        radius = event.radius
        intensity = event.intensity

        # Bounding box in grid space
        min_gx, min_gz = self._world_to_grid(wx - radius, wz - radius)
        max_gx, max_gz = self._world_to_grid(wx + radius, wz + radius)

        for gz in range(min_gz, max_gz + 1):
            cell_z = self.min_z + (gz + 0.5) * self.cell_h
            for gx in range(min_gx, max_gx + 1):
                cell_x = self.min_x + (gx + 0.5) * self.cell_w
                dist_sq = (cell_x - wx) ** 2 + (cell_z - wz) ** 2
                if dist_sq <= radius * radius:
                    falloff = 1.0 - math.sqrt(dist_sq) / radius
                    idx = self._idx(gx, gz)
                    if event.channel == DisplacementChannel.BURN:
                        self.burn_map[idx] = clamp_scalar(self.burn_map[idx] + intensity * falloff, 0.0, 1.0)
                    elif event.channel == DisplacementChannel.LIQUID:
                        self.liquid_map[idx] = clamp_scalar(self.liquid_map[idx] + intensity * falloff, 0.0, 1.0)

    def calculate_slope_flow(
        self,
        normal: Tuple[float, float, float],
        gravity: Tuple[float, float, float] = (0.0, -9.81, 0.0),
    ) -> Tuple[float, float, float]:
        """
        Computes fluid runoff velocity tangent to the terrain slope.
        Formula: v_flow = g - (g . n) * n
        """
        nx, ny, nz = normal
        gx, gy, gz = gravity

        # Dot product g . n
        g_dot_n = gx * nx + gy * ny + gz * nz

        # Tangential projection
        tx = gx - g_dot_n * nx
        ty = gy - g_dot_n * ny
        tz = gz - g_dot_n * nz

        return ensure_finite_vec3((tx, ty, tz))

    def update(self, dt: float) -> None:
        """Simulates cooling of burns and evaporation of liquids over time."""
        for i in range(len(self.burn_map)):
            if self.burn_map[i] > 0.0:
                self.burn_map[i] = max(0.0, self.burn_map[i] - self.burn_cool_rate * dt)
            if self.liquid_map[i] > 0.0:
                self.liquid_map[i] = max(0.0, self.liquid_map[i] - self.liquid_evap_rate * dt)

    def get_burn_at(self, wx: float, wz: float) -> float:
        gx, gz = self._world_to_grid(wx, wz)
        return self.burn_map[self._idx(gx, gz)]

    def get_liquid_at(self, wx: float, wz: float) -> float:
        gx, gz = self._world_to_grid(wx, wz)
        return self.liquid_map[self._idx(gx, gz)]
