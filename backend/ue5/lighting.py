"""
Lumen Lighting Rig Configuration for Unreal Engine 5.

Configures dynamic real-time global illumination presets adhering to Lumen standards.
Supports 5 lighting rig presets:
- studio_3point: Balanced 3-point key/fill/rim with ambient skylight.
- cyberpunk_neon: High-energy stylized neon palette (cyan, magenta, amber).
- dramatic: Chiaroscuro high-contrast lighting with strong rim separation.
- outdoor_sunlight: High-lux directional sun (75,000 lux) and atmospheric sky.
- night_moonlight: Cool moonlight (1,500 lux, 8500K) and subtle nocturnal fill.

100% Zero-Any compliant with Pydantic v2 strict models.
"""

from __future__ import annotations

import logging
from typing import Dict, List, Optional
from backend.core.models import ColorRGB, Rotator3D, StrictBaseModel, Vector3D
from pydantic import Field

logger = logging.getLogger("ianimation.ue5.lighting")


class LightActorConfig(StrictBaseModel):
    """Configuration for an individual light actor in the UE5 scene."""
    name: str = Field(..., description="Unique actor name of the light")
    light_type: str = Field(..., description="Directional, Point, Spot, or Sky")
    intensity: float = Field(default=5000.0, ge=0.0, description="Luminous flux in Lumens or illuminance in Lux")
    color: ColorRGB = Field(default_factory=lambda: ColorRGB(r=1.0, g=1.0, b=1.0))
    position: Vector3D = Field(default_factory=Vector3D)
    rotation: Rotator3D = Field(default_factory=Rotator3D)
    cast_shadows: bool = Field(default=True)
    temperature_kelvin: Optional[float] = Field(default=None)


class LumenLightingSetup(StrictBaseModel):
    """Collection of light actors and global Lumen post-process volume parameters."""
    preset_name: str
    lights: List[LightActorConfig]
    indirect_lighting_intensity: float = Field(default=1.2)
    lumen_global_illumination: bool = Field(default=True)
    lumen_reflections: bool = Field(default=True)


class LightingRig:
    """
    Manages and synthesizes Lumen-enabled architectural and cinematographic lighting rigs.
    """

    @classmethod
    def get_preset(cls, preset_name: Optional[str] = "studio_3point") -> LumenLightingSetup:
        """
        Build a Lumen-enabled lighting setup based on a preset name.
        Falls back safely to 'studio_3point' if the preset is unknown.
        """
        name = (preset_name or "studio_3point").lower().strip()

        if "cyberpunk" in name or "neon" in name:
            lights = [
                LightActorConfig(
                    name="Key_NeonCyan",
                    light_type="Spot",
                    intensity=8000.0,
                    color=ColorRGB(r=0.0, g=0.9, b=1.0),
                    position=Vector3D(x=-200.0, y=-250.0, z=220.0),
                    rotation=Rotator3D(pitch=-25.0, yaw=45.0, roll=0.0),
                    temperature_kelvin=9000.0,
                ),
                LightActorConfig(
                    name="Fill_NeonMagenta",
                    light_type="Spot",
                    intensity=6000.0,
                    color=ColorRGB(r=1.0, g=0.0, b=0.8),
                    position=Vector3D(x=200.0, y=-250.0, z=180.0),
                    rotation=Rotator3D(pitch=-20.0, yaw=-45.0, roll=0.0),
                ),
                LightActorConfig(
                    name="Rim_NeonAmber",
                    light_type="Point",
                    intensity=12000.0,
                    color=ColorRGB(r=1.0, g=0.6, b=0.0),
                    position=Vector3D(x=0.0, y=250.0, z=260.0),
                ),
            ]
            actual_name = "cyberpunk_neon"

        elif "dramatic" in name or "chiaroscuro" in name:
            lights = [
                LightActorConfig(
                    name="Key_Chiaroscuro",
                    light_type="Spot",
                    intensity=15000.0,
                    color=ColorRGB(r=1.0, g=0.95, b=0.85),
                    position=Vector3D(x=-300.0, y=-200.0, z=300.0),
                    rotation=Rotator3D(pitch=-40.0, yaw=35.0, roll=0.0),
                    temperature_kelvin=4800.0,
                ),
                LightActorConfig(
                    name="Rim_HairLight",
                    light_type="Spot",
                    intensity=10000.0,
                    color=ColorRGB(r=0.7, g=0.8, b=1.0),
                    position=Vector3D(x=150.0, y=250.0, z=280.0),
                    rotation=Rotator3D(pitch=-30.0, yaw=-140.0, roll=0.0),
                    temperature_kelvin=7500.0,
                ),
            ]
            actual_name = "dramatic"

        elif "sunlight" in name or "outdoor" in name:
            lights = [
                LightActorConfig(
                    name="Directional_Sun",
                    light_type="Directional",
                    intensity=75000.0,
                    color=ColorRGB(r=1.0, g=0.96, b=0.9),
                    position=Vector3D(x=0.0, y=0.0, z=1000.0),
                    rotation=Rotator3D(pitch=-45.0, yaw=30.0, roll=0.0),
                    temperature_kelvin=5500.0,
                ),
                LightActorConfig(
                    name="Sky_AmbientDay",
                    light_type="Sky",
                    intensity=2500.0,
                    color=ColorRGB(r=0.75, g=0.85, b=1.0),
                    position=Vector3D(x=0.0, y=0.0, z=1000.0),
                ),
                LightActorConfig(
                    name="Fill_GroundBounce",
                    light_type="Spot",
                    intensity=3000.0,
                    color=ColorRGB(r=0.9, g=0.85, b=0.75),
                    position=Vector3D(x=0.0, y=-200.0, z=50.0),
                    rotation=Rotator3D(pitch=30.0, yaw=0.0, roll=0.0),
                ),
            ]
            actual_name = "outdoor_sunlight"

        elif "moon" in name or "night" in name or "nocturnal" in name:
            lights = [
                LightActorConfig(
                    name="Directional_Moon",
                    light_type="Directional",
                    intensity=1500.0,
                    color=ColorRGB(r=0.65, g=0.75, b=1.0),
                    position=Vector3D(x=0.0, y=0.0, z=1000.0),
                    rotation=Rotator3D(pitch=-60.0, yaw=120.0, roll=0.0),
                    temperature_kelvin=8500.0,
                ),
                LightActorConfig(
                    name="Sky_AmbientNight",
                    light_type="Sky",
                    intensity=500.0,
                    color=ColorRGB(r=0.2, g=0.3, b=0.6),
                    position=Vector3D(x=0.0, y=0.0, z=1000.0),
                ),
                LightActorConfig(
                    name="Rim_CoolBlue",
                    light_type="Point",
                    intensity=4000.0,
                    color=ColorRGB(r=0.4, g=0.7, b=1.0),
                    position=Vector3D(x=0.0, y=250.0, z=220.0),
                ),
            ]
            actual_name = "night_moonlight"

        else:
            # Default fallback: studio_3point
            if name != "studio_3point":
                logger.info("Unknown lighting preset '%s'; falling back to 'studio_3point'.", preset_name)
            lights = [
                LightActorConfig(
                    name="Key_Light",
                    light_type="Spot",
                    intensity=8000.0,
                    color=ColorRGB(r=1.0, g=0.98, b=0.95),
                    position=Vector3D(x=-250.0, y=-300.0, z=250.0),
                    rotation=Rotator3D(pitch=-30.0, yaw=40.0, roll=0.0),
                    temperature_kelvin=5200.0,
                ),
                LightActorConfig(
                    name="Fill_Light",
                    light_type="Spot",
                    intensity=3500.0,
                    color=ColorRGB(r=0.85, g=0.9, b=1.0),
                    position=Vector3D(x=250.0, y=-250.0, z=180.0),
                    rotation=Rotator3D(pitch=-20.0, yaw=-35.0, roll=0.0),
                    temperature_kelvin=6500.0,
                ),
                LightActorConfig(
                    name="Rim_Backlight",
                    light_type="Point",
                    intensity=5000.0,
                    color=ColorRGB(r=1.0, g=1.0, b=1.0),
                    position=Vector3D(x=0.0, y=300.0, z=280.0),
                ),
                LightActorConfig(
                    name="Sky_Ambient",
                    light_type="Sky",
                    intensity=1000.0,
                    color=ColorRGB(r=0.9, g=0.95, b=1.0),
                    position=Vector3D(x=0.0, y=0.0, z=500.0),
                ),
            ]
            actual_name = "studio_3point"

        return LumenLightingSetup(
            preset_name=actual_name,
            lights=lights,
            indirect_lighting_intensity=1.2,
            lumen_global_illumination=True,
            lumen_reflections=True,
        )


def setup_lumen_lighting(preset: Optional[str] = "studio_3point") -> LumenLightingSetup:
    """
    Functional helper to configure a Lumen lighting rig.
    Safely defaults to 'studio_3point' if preset is None.
    """
    return LightingRig.get_preset(preset or "studio_3point")
