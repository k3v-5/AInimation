from typing import Optional, Any
from ..core.presentation_types import LightType
from ..core.presentation_schema import LightingConfiguration, LightSourceSpec

class LightingRigBuilder:
    @classmethod
    def build_lighting_rig(
        cls,
        distance: float = 3.0,
        reference_analysis: Optional[Any] = None
    ) -> LightingConfiguration:
        scale = max(1.0, distance / 3.0)

        key = LightSourceSpec(
            light_id="LIGHT_KEY",
            light_type=LightType.AREA,
            position=(2.5 * scale, -2.5 * scale, 3.5 * scale),
            rotation=(45.0, 0.0, -45.0),
            intensity=650.0 * (scale**1.5),
            color=(1.0, 0.98, 0.95),
            size=1.2 * scale,
            temperature=5600.0,
            cast_shadow=True,
            softness=0.4
        )

        fill = LightSourceSpec(
            light_id="LIGHT_FILL",
            light_type=LightType.AREA,
            position=(-3.0 * scale, -2.0 * scale, 2.0 * scale),
            rotation=(30.0, 0.0, 45.0),
            intensity=250.0 * (scale**1.5),
            color=(0.92, 0.95, 1.0),
            size=2.0 * scale,
            temperature=6500.0,
            cast_shadow=False,
            softness=0.8
        )

        rim = LightSourceSpec(
            light_id="LIGHT_RIM",
            light_type=LightType.SPOT,
            position=(0.0, 3.0 * scale, 3.0 * scale),
            rotation=(-45.0, 0.0, 180.0),
            intensity=400.0 * (scale**1.5),
            color=(1.0, 1.0, 1.0),
            size=0.5 * scale,
            temperature=6000.0,
            cast_shadow=True,
            softness=0.2
        )

        return LightingConfiguration(
            key_light=key,
            fill_light=fill,
            rim_light=rim,
            environment_intensity=0.25,
            ground_plane_enabled=True,
            ground_color=(0.15, 0.15, 0.16),
            ground_roughness=0.85
        )
