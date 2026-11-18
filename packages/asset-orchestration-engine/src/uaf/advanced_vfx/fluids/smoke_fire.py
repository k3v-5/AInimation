"""
UAF-81.89.1: Coupled Smoke and Fire Combustion Solver.
Models chemical fuel consumption, heat generation, soot/smoke release, and dynamic fire luminosity.
"""

from __future__ import annotations

from typing import List, Tuple
from .grid3d import EulerianFluidGrid3D
from ..core.contracts import GridDimensions3D, FluidProperties, clamp_scalar


class SmokeFireSolver:
    """
    Coupled fire and smoke combustion model integrated atop Eulerian 3D fluid dynamics.
    Fuel + Heat -> Consumed Fuel + Flame Light + Smoke Soot + Thermal Expansion.
    """

    def __init__(
        self,
        grid_dims: GridDimensions3D,
        burn_rate: float = 0.65,
        ignition_temp: float = 60.0,
        smoke_yield: float = 0.8,
        heat_yield: float = 120.0,
    ) -> None:
        self.grid: EulerianFluidGrid3D = EulerianFluidGrid3D(grid_dims, FluidProperties())
        self.burn_rate: float = burn_rate
        self.ignition_temp: float = ignition_temp
        self.smoke_yield: float = smoke_yield
        self.heat_yield: float = heat_yield

        num_cells = self.grid.w * self.grid.h * self.grid.d
        self.fuel: List[float] = [0.0] * num_cells
        self.flame: List[float] = [0.0] * num_cells

    def inject_fuel(self, x: int, y: int, z: int, amount: float) -> None:
        """Adds combustible fuel to a specific grid cell."""
        if 0 <= x < self.grid.w and 0 <= y < self.grid.h and 0 <= z < self.grid.d:
            idx = self.grid._c_idx(x, y, z)
            self.fuel[idx] = max(0.0, self.fuel[idx] + amount)

    def ignite(self, x: int, y: int, z: int, temp_boost: float = 150.0) -> None:
        """Injects thermal energy to trigger combustion."""
        self.grid.add_temperature(x, y, z, temp_boost)

    def update_combustion(self, dt: float) -> None:
        """
        Calculates fuel combustion reaction for all cells where temperature exceeds ignition threshold.
        """
        for z in range(self.grid.d):
            for y in range(self.grid.h):
                for x in range(self.grid.w):
                    idx = self.grid._c_idx(x, y, z)
                    fuel_amt = self.fuel[idx]
                    temp = self.grid.temperature[idx]

                    if fuel_amt > 0.001 and temp >= self.ignition_temp:
                        # Reaction rate proportional to temperature excess
                        rate = min(fuel_amt, self.burn_rate * dt * (temp / self.ignition_temp))
                        self.fuel[idx] -= rate

                        # Byproducts: Smoke soot + Heat release + Visual Flame
                        self.grid.density[idx] += rate * self.smoke_yield
                        self.grid.temperature[idx] += rate * self.heat_yield
                        self.flame[idx] = rate * 10.0
                    else:
                        # Flame decay when not burning
                        self.flame[idx] = max(0.0, self.flame[idx] - 5.0 * dt)

                    # Gradual thermal dissipation to ambient
                    ambient = self.grid.props.ambient_temp
                    self.grid.temperature[idx] += (ambient - self.grid.temperature[idx]) * 0.05 * dt

    def step(self, dt: float) -> float:
        """Simulates one step of fire combustion coupled with 3D fluid motion."""
        self.update_combustion(dt)
        max_div = self.grid.step(dt)
        return max_div

    def get_flame_intensity(self, x: int, y: int, z: int) -> float:
        """Returns visual flame brightness in range [0, +inf)."""
        if 0 <= x < self.grid.w and 0 <= y < self.grid.h and 0 <= z < self.grid.d:
            return self.flame[self.grid._c_idx(x, y, z)]
        return 0.0

    def get_total_fuel(self) -> float:
        return sum(self.fuel)

    def get_total_smoke(self) -> float:
        return sum(self.grid.density)
