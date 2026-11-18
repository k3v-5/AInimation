"""
UE5 Light Component Manifest Serializers for UAF-81.85.
"""

from __future__ import annotations
import math
from typing import Any, Dict

from uaf.runtime_lighting.core import LightType, LightMobility
from uaf.runtime_lighting.lights import Light
from uaf.runtime_lighting.point import PointLight
from uaf.runtime_lighting.spot import SpotLight
from uaf.runtime_lighting.directional import DirectionalLight
from uaf.runtime_lighting.area import RectAreaLight


class UE5LightExporter:
    """
    Translates UAF Light representations into Unreal Engine 5 Component descriptors.
    """

    @staticmethod
    def _ue5_mobility(mobility: LightMobility) -> str:
        if mobility == LightMobility.STATIC:
            return "EComponentMobility::Static"
        elif mobility == LightMobility.STATIONARY:
            return "EComponentMobility::Stationary"
        else:
            return "EComponentMobility::Movable"

    @staticmethod
    def export_light(light: Light) -> Dict[str, Any]:
        """Translates a UAF light into a UE5 component manifest dictionary."""
        eff_color = light.get_effective_color()

        base_manifest: Dict[str, Any] = {
            "component_class": "ULightComponent",
            "actor_name": f"LightActor_{light.light_id.value}",
            "relative_location": {
                "x": round(light.position[0] * 100.0, 2),  # UE5 cm
                "y": round(light.position[2] * 100.0, 2),  # Coordinate swap Z/Y
                "z": round(light.position[1] * 100.0, 2),
            },
            "mobility": UE5LightExporter._ue5_mobility(light.mobility),
            "light_color": {
                "r": round(eff_color[0], 4),
                "g": round(eff_color[1], 4),
                "b": round(eff_color[2], 4),
                "a": 1.0,
            },
            "intensity": light.intensity,
            "cast_shadows": light.cast_shadows,
            "shadow_bias": light.shadow_bias,
            "shadow_slope_bias": light.shadow_slope_bias,
            "shadow_normal_bias": light.shadow_normal_bias,
            "contact_shadow_length": light.contact_shadow_length,
            "indirect_lighting_intensity": light.indirect_lighting_scale,
            "volumetric_scattering_intensity": light.volumetric_scattering_intensity,
        }

        if isinstance(light, DirectionalLight):
            base_manifest["component_class"] = "UDirectionalLightComponent"
            base_manifest["light_source_angle"] = light.sun_angular_diameter
            base_manifest["dynamic_shadow_distance_movable_light"] = light.cascade_max_distance * 100.0
            base_manifest["num_dynamic_shadow_cascades"] = light.cascade_count
            base_manifest["cascade_distribution_exponent"] = light.cascade_distribution_exponent
            base_manifest["cascade_transition_fraction"] = light.cascade_transition_fraction
            base_manifest["atmosphere_sun_light_index"] = light.atmosphere_sun_light_index

        elif isinstance(light, SpotLight):
            base_manifest["component_class"] = "USpotLightComponent"
            base_manifest["attenuation_radius"] = light.range * 100.0
            base_manifest["inner_cone_angle"] = light.inner_cone_angle
            base_manifest["outer_cone_angle"] = light.outer_cone_angle
            base_manifest["source_radius"] = light.source_radius * 100.0
            base_manifest["soft_source_radius"] = light.soft_source_radius * 100.0

        elif isinstance(light, PointLight):
            base_manifest["component_class"] = "UPointLightComponent"
            base_manifest["attenuation_radius"] = light.range * 100.0
            base_manifest["source_radius"] = light.source_radius * 100.0
            base_manifest["soft_source_radius"] = light.soft_source_radius * 100.0
            base_manifest["source_length"] = light.source_length * 100.0

        elif isinstance(light, RectAreaLight):
            base_manifest["component_class"] = "URectLightComponent"
            base_manifest["attenuation_radius"] = light.range * 100.0
            base_manifest["source_width"] = light.source_width * 100.0
            base_manifest["source_height"] = light.source_height * 100.0
            base_manifest["barn_door_angle"] = light.barn_door_angle
            base_manifest["barn_door_length"] = light.barn_door_length * 100.0

        return base_manifest
