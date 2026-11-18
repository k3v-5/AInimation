"""
Directional Light Implementation for UAF-81.85.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict

from .core import LightType, ensure_finite_scalar
from .lights import Light


@dataclass
class DirectionalLight(Light):
    """
    Directional light source providing parallel illumination across the world (Sun / Moon).
    Intensity is measured in Lux (lm/m^2).
    """
    sun_angular_diameter: float = 0.5357             # Sun disk angular size in degrees (approx 32 arcminutes)
    cascade_count: int = 4                           # Number of CSM cascades (1 to 8)
    cascade_distribution_exponent: float = 0.8       # Split lambda: 0.0=uniform, 1.0=logarithmic
    cascade_max_distance: float = 200.0              # Max shadow distance in meters
    cascade_transition_fraction: float = 0.1         # Fade zone fraction between cascades
    atmosphere_sun_light_index: int = 0              # 0 for primary Sun, 1 for secondary Moon

    def __post_init__(self) -> None:
        self.light_type = LightType.DIRECTIONAL
        super().__post_init__()
        self.sun_angular_diameter = max(0.01, min(10.0, ensure_finite_scalar(self.sun_angular_diameter, "sun_angular_diameter", 0.5357)))
        self.cascade_count = max(1, min(8, int(ensure_finite_scalar(self.cascade_count, "cascade_count", 4))))
        self.cascade_distribution_exponent = max(0.0, min(1.0, ensure_finite_scalar(self.cascade_distribution_exponent, "cascade_distribution_exponent", 0.8)))
        self.cascade_max_distance = max(1.0, ensure_finite_scalar(self.cascade_max_distance, "cascade_max_distance", 200.0))
        self.cascade_transition_fraction = max(0.0, min(0.5, ensure_finite_scalar(self.cascade_transition_fraction, "cascade_transition_fraction", 0.1)))
        self.atmosphere_sun_light_index = max(0, min(1, int(self.atmosphere_sun_light_index)))

    def to_dict(self) -> Dict[str, Any]:
        d = super().to_dict()
        d.update({
            "sun_angular_diameter": self.sun_angular_diameter,
            "cascade_count": self.cascade_count,
            "cascade_distribution_exponent": self.cascade_distribution_exponent,
            "cascade_max_distance": self.cascade_max_distance,
            "cascade_transition_fraction": self.cascade_transition_fraction,
            "atmosphere_sun_light_index": self.atmosphere_sun_light_index,
        })
        return d
