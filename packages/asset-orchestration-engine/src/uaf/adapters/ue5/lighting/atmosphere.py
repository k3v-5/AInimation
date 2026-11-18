"""
UE5 SkyAtmosphere & VolumetricCloud Serializers for UAF-81.85.
"""

from __future__ import annotations
from typing import Any, Dict

from uaf.runtime_lighting.atmosphere import AtmosphereScattering
from uaf.runtime_lighting.clouds import CloudSystem


class UE5AtmosphereExporter:
    """
    Translates UAF Atmosphere and Clouds into Unreal Engine 5 Component descriptors.
    """

    @staticmethod
    def export_atmosphere(atmosphere: AtmosphereScattering) -> Dict[str, Any]:
        return {
            "component_class": "USkyAtmosphereComponent",
            "rayleigh_scattering": {
                "r": atmosphere.rayleigh_scattering[0] * 1000.0,
                "g": atmosphere.rayleigh_scattering[1] * 1000.0,
                "b": atmosphere.rayleigh_scattering[2] * 1000.0,
            },
            "rayleigh_exponential_distribution": atmosphere.rayleigh_scale_height * 0.001,  # km
            "mie_scattering": atmosphere.mie_scattering * 1000.0,
            "mie_absorption": atmosphere.mie_absorption * 1000.0,
            "mie_anisotropy": atmosphere.mie_anisotropy_g,
            "mie_exponential_distribution": atmosphere.mie_scale_height * 0.001,  # km
            "other_absorption": {
                "r": atmosphere.ozone_absorption[0] * 1000.0,
                "g": atmosphere.ozone_absorption[1] * 1000.0,
                "b": atmosphere.ozone_absorption[2] * 1000.0,
            },
            "other_tent_distribution": {
                "tip_altitude": atmosphere.ozone_tent_center_altitude * 0.001,
                "tip_value": 1.0,
                "width": atmosphere.ozone_tent_width * 0.001,
            },
        }

    @staticmethod
    def export_clouds(clouds: CloudSystem) -> Dict[str, Any]:
        return {
            "component_class": "UVolumetricCloudComponent",
            "layer_bottom_altitude": clouds.altitude_base * 0.001,  # km
            "layer_height": clouds.thickness * 0.001,              # km
            "coverage": clouds.coverage,
            "density": clouds.density,
            "multi_scattering_factor": clouds.multi_scattering_factor,
        }
