"""
Sun Celestial Body Implementation for UAF-81.85.
"""

from __future__ import annotations
import math
from dataclasses import dataclass
from typing import Tuple

from .core import ensure_finite_scalar, ensure_finite_vec3, normalize_vec3, kelvin_to_rgb


@dataclass
class Sun:
    """
    Sun celestial body providing primary directional illumination and atmospheric scattering.
    """
    direction: Tuple[float, float, float] = (0.0, -0.7071, -0.7071)  # Points in direction light travels
    intensity: float = 120000.0                                     # Direct sunlight lux at zenith
    temperature: float = 5800.0                                     # Kelvin (5800K for direct sunlight)
    angular_diameter: float = 0.5357                                # Degrees
    disk_color: Tuple[float, float, float] = (1.0, 0.98, 0.95)
    atmospheric_contribution: float = 1.0

    def __post_init__(self) -> None:
        self.direction = normalize_vec3(ensure_finite_vec3(self.direction, "direction", (0.0, -0.7071, -0.7071)))
        self.intensity = max(0.0, ensure_finite_scalar(self.intensity, "intensity", 120000.0))
        self.temperature = max(1000.0, min(40000.0, ensure_finite_scalar(self.temperature, "temperature", 5800.0)))
        self.angular_diameter = max(0.01, min(10.0, ensure_finite_scalar(self.angular_diameter, "angular_diameter", 0.5357)))
        self.disk_color = ensure_finite_vec3(self.disk_color, "disk_color", (1.0, 0.98, 0.95))
        self.atmospheric_contribution = max(0.0, ensure_finite_scalar(self.atmospheric_contribution, "atmospheric_contribution", 1.0))

    def get_solar_irradiance(self, elevation_deg: float) -> float:
        """Computes sunlight attenuation through atmospheric air mass."""
        if elevation_deg <= 0.0:
            return 0.0
        sin_elev = math.sin(math.radians(elevation_deg))
        # Kasten-Young air mass approximation
        air_mass = 1.0 / max(0.01, sin_elev + 0.50572 * ((elevation_deg + 6.07995) ** -1.6364))
        # Atmospheric transmission factor approx 0.7 ^ air_mass
        transmission = 0.75 ** air_mass
        return self.intensity * transmission
