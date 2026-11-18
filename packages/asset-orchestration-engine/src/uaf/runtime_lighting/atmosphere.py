"""
Atmospheric Scattering Physics (Rayleigh, Mie, Ozone) for UAF-81.85.
"""

from __future__ import annotations
import math
from dataclasses import dataclass, field
from typing import Tuple

from .core import ensure_finite_scalar, ensure_finite_vec3


@dataclass
class AtmosphereScattering:
    """
    Physical parameters for planetary atmospheric scattering.
    Values represent standard Earth sea-level conditions.
    """
    # Rayleigh scattering coefficients (R, G, B) in m^-1 (wavelengths: 680nm, 550nm, 440nm)
    rayleigh_scattering: Tuple[float, float, float] = (5.802e-6, 13.558e-6, 33.100e-6)
    rayleigh_scale_height: float = 8000.0           # Meters (8 km)

    # Mie scattering coefficient in m^-1
    mie_scattering: float = 3.996e-6
    mie_absorption: float = 4.40e-6
    mie_scale_height: float = 1200.0                # Meters (1.2 km)
    mie_anisotropy_g: float = 0.8                   # Henyey-Greenstein asymmetry factor

    # Ozone absorption coefficients (R, G, B) in m^-1 (Chappuis band)
    ozone_absorption: Tuple[float, float, float] = (0.650e-6, 1.881e-6, 0.085e-6)
    ozone_tent_center_altitude: float = 25000.0     # 25 km altitude
    ozone_tent_width: float = 15000.0               # 15 km thickness

    # Aerial perspective
    aerial_perspective_distance_scale: float = 1.0

    def __post_init__(self) -> None:
        self.rayleigh_scattering = ensure_finite_vec3(self.rayleigh_scattering, "rayleigh_scattering", (5.802e-6, 13.558e-6, 33.100e-6))
        self.rayleigh_scale_height = max(100.0, ensure_finite_scalar(self.rayleigh_scale_height, "rayleigh_scale_height", 8000.0))
        self.mie_scattering = max(0.0, ensure_finite_scalar(self.mie_scattering, "mie_scattering", 3.996e-6))
        self.mie_absorption = max(0.0, ensure_finite_scalar(self.mie_absorption, "mie_absorption", 4.40e-6))
        self.mie_scale_height = max(100.0, ensure_finite_scalar(self.mie_scale_height, "mie_scale_height", 1200.0))
        self.mie_anisotropy_g = max(-0.99, min(0.99, ensure_finite_scalar(self.mie_anisotropy_g, "mie_anisotropy_g", 0.8)))
        self.ozone_absorption = ensure_finite_vec3(self.ozone_absorption, "ozone_absorption", (0.650e-6, 1.881e-6, 0.085e-6))

    def evaluate_rayleigh_phase(self, cos_theta: float) -> float:
        """Rayleigh phase function: 3 / (16 * pi) * (1 + cos^2(theta))."""
        return (3.0 / (16.0 * math.pi)) * (1.0 + cos_theta * cos_theta)

    def evaluate_mie_phase(self, cos_theta: float) -> float:
        """Henyey-Greenstein phase function for Mie forward scattering."""
        g = self.mie_anisotropy_g
        denom = 1.0 + g * g - 2.0 * g * cos_theta
        if denom <= 0.0:
            return 1.0 / (4.0 * math.pi)
        return (1.0 - g * g) / (4.0 * math.pi * (denom ** 1.5))

    def evaluate_transmittance(self, distance_m: float, altitude_m: float = 0.0) -> Tuple[float, float, float]:
        """Calculates atmospheric optical transmittance over a given distance."""
        dist = max(0.0, distance_m)
        r_density = math.exp(-max(0.0, altitude_m) / self.rayleigh_scale_height)
        m_density = math.exp(-max(0.0, altitude_m) / self.mie_scale_height)

        # Extinction = Scattering + Absorption
        tr_r = math.exp(-(self.rayleigh_scattering[0] * r_density + (self.mie_scattering + self.mie_absorption) * m_density + self.ozone_absorption[0]) * dist)
        tr_g = math.exp(-(self.rayleigh_scattering[1] * r_density + (self.mie_scattering + self.mie_absorption) * m_density + self.ozone_absorption[1]) * dist)
        tr_b = math.exp(-(self.rayleigh_scattering[2] * r_density + (self.mie_scattering + self.mie_absorption) * m_density + self.ozone_absorption[2]) * dist)
        return (round(tr_r, 6), round(tr_g, 6), round(tr_b, 6))
