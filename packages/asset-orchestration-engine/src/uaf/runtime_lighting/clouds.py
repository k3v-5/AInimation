"""
Volumetric Cloud Model & Wind Advection for UAF-81.85.
"""

from __future__ import annotations
import math
from dataclasses import dataclass, field
from typing import Tuple

from .core import ensure_finite_scalar, ensure_finite_vec3


@dataclass
class CloudSystem:
    """
    Volumetric Cloud Layer with wind advection and directional sun occlusion.
    """
    coverage: float = 0.5                          # [0.0 = clear, 1.0 = fully overcast]
    density: float = 0.8                           # Cloud mass density
    altitude_base: float = 2000.0                  # Meters
    thickness: float = 1500.0                      # Meters
    wind_velocity: Tuple[float, float, float] = (5.0, 0.0, 2.0)  # m/s
    multi_scattering_factor: float = 0.5
    wind_offset: Tuple[float, float, float] = (0.0, 0.0, 0.0)

    def __post_init__(self) -> None:
        self.coverage = max(0.0, min(1.0, ensure_finite_scalar(self.coverage, "coverage", 0.5)))
        self.density = max(0.0, min(2.0, ensure_finite_scalar(self.density, "density", 0.8)))
        self.altitude_base = max(100.0, ensure_finite_scalar(self.altitude_base, "altitude_base", 2000.0))
        self.thickness = max(100.0, ensure_finite_scalar(self.thickness, "thickness", 1500.0))
        self.wind_velocity = ensure_finite_vec3(self.wind_velocity, "wind_velocity", (5.0, 0.0, 2.0))

    def update(self, dt: float) -> None:
        """Advances wind advection displacement deterministically."""
        ox = self.wind_offset[0] + self.wind_velocity[0] * dt
        oy = self.wind_offset[1] + self.wind_velocity[1] * dt
        oz = self.wind_offset[2] + self.wind_velocity[2] * dt
        self.wind_offset = (ox, oy, oz)

    def evaluate_sun_occlusion(self, sun_dir: Tuple[float, float, float]) -> float:
        """
        Computes cloud shadow / sun attenuation factor in [0.0, 1.0].
        1.0 = direct sunlight reaches surface, 0.0 = fully blocked by clouds.
        """
        if self.coverage <= 0.01:
            return 1.0
        # More cloud coverage and higher density reduces sunlight transmission
        optical_thickness = self.coverage * self.density * 3.0
        # Slanted sun rays travel through more cloud mass
        sun_elev_sin = max(0.1, abs(sun_dir[1]))
        effective_depth = optical_thickness / sun_elev_sin
        transmission = math.exp(-effective_depth)
        return round(max(0.0, min(1.0, transmission)), 6)
