"""
Moon Celestial Body Implementation for UAF-81.85.
"""

from __future__ import annotations
import math
from dataclasses import dataclass
from typing import Tuple

from .core import ensure_finite_scalar, ensure_finite_vec3, normalize_vec3


@dataclass
class Moon:
    """
    Moon celestial body providing secondary nighttime directional illumination.
    """
    direction: Tuple[float, float, float] = (0.0, 0.7071, 0.7071)
    phase: float = 0.5                                              # 0.0 = New Moon, 0.5 = Full Moon, 1.0 = New
    intensity: float = 0.25                                         # Peak full moon lux (~0.25 lux)
    color: Tuple[float, float, float] = (0.75, 0.85, 1.0)           # Cool silver-blue
    angular_diameter: float = 0.518                                 # Degrees

    def __post_init__(self) -> None:
        self.direction = normalize_vec3(ensure_finite_vec3(self.direction, "direction", (0.0, 0.7071, 0.7071)))
        self.phase = max(0.0, min(1.0, ensure_finite_scalar(self.phase, "phase", 0.5)))
        self.intensity = max(0.0, ensure_finite_scalar(self.intensity, "intensity", 0.25))
        self.color = ensure_finite_vec3(self.color, "color", (0.75, 0.85, 1.0))
        self.angular_diameter = max(0.01, min(10.0, ensure_finite_scalar(self.angular_diameter, "angular_diameter", 0.518)))

    @property
    def phase_illumination_fraction(self) -> float:
        """Returns lunar illumination fraction based on phase (0.0 for new moon, 1.0 for full moon)."""
        # Phase 0.5 is full moon
        dist = abs(self.phase - 0.5) * 2.0  # 0 at full moon, 1 at new moon
        return max(0.0, 1.0 - dist)

    def get_lunar_irradiance(self, elevation_deg: float) -> float:
        """Calculates moonlight reaching the surface."""
        if elevation_deg <= 0.0:
            return 0.0
        sin_elev = math.sin(math.radians(elevation_deg))
        return self.intensity * self.phase_illumination_fraction * max(0.0, sin_elev)
