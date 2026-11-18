"""
UE5 ExponentialHeightFog Serializer for UAF-81.85.
"""

from __future__ import annotations
from typing import Any, Dict

from uaf.runtime_lighting.fog import FogSystem


class UE5FogExporter:
    """
    Translates UAF Fog System to Unreal Engine 5 ExponentialHeightFog component descriptor.
    """

    @staticmethod
    def export_fog(fog: FogSystem) -> Dict[str, Any]:
        return {
            "component_class": "UExponentialHeightFogComponent",
            "fog_density": fog.density,
            "fog_height_falloff": fog.height_falloff * 0.01,
            "fog_inscattering_color": {
                "r": fog.albedo[0],
                "g": fog.albedo[1],
                "b": fog.albedo[2],
                "a": 1.0,
            },
            "start_distance": fog.start_distance * 100.0,
            "fog_cutoff_distance": fog.cutoff_distance * 100.0,
            "volumetric_fog": True,
            "volumetric_fog_distance": fog.cutoff_distance * 100.0,
        }
