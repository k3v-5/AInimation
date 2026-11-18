"""
SkyAtmosphereProfile model.
UAF-81.25 Sections 27, 28, 29, 30, 31, 33, 34.
"""

from dataclasses import dataclass
from typing import Dict, Any


@dataclass
class SkyAtmosphereProfile:
    sky_type: str = "CLEAR"  # CLEAR, OVERCAST, STORM, NIGHT, SUNSET, SUNRISE, ALIEN, SCI_FI
    sun_intensity_lux: float = 100000.0
    fog_density: float = 0.02
    volumetric_fog_enabled: bool = True
    cloud_coverage: float = 0.3

    def to_dict(self) -> Dict[str, Any]:
        return {
            "sky_type": self.sky_type,
            "sun_intensity_lux": self.sun_intensity_lux,
            "fog_density": self.fog_density,
            "volumetric_fog_enabled": self.volumetric_fog_enabled,
            "cloud_coverage": self.cloud_coverage,
        }
