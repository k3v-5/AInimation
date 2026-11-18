"""Dynamic lighting and atmosphere bridge for Unreal Engine 5."""

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class UE5LightType(str, Enum):
    DIRECTIONAL = "DIRECTIONAL"
    POINT = "POINT"
    SPOT = "SPOT"
    RECT = "RECT"
    SKY_LIGHT = "SKY_LIGHT"

    # Aliases
    Directional = "DIRECTIONAL"
    Point = "POINT"
    Spot = "SPOT"
    Rect = "RECT"
    SkyLight = "SKY_LIGHT"


@dataclass
class LightingBridgePayload:
    light_id: str
    light_type: UE5LightType
    location: List[float] = field(default_factory=lambda: [0.0, 0.0, 300.0])
    rotation: List[float] = field(default_factory=lambda: [0.0, -45.0, 0.0])
    color_rgb: List[float] = field(default_factory=lambda: [1.0, 1.0, 1.0])
    intensity: float = 1000.0
    use_temperature: bool = False
    temperature_k: float = 6500.0
    attenuation_radius: float = 1000.0
    inner_cone_angle: float = 0.0
    outer_cone_angle: float = 44.0
    cast_shadows: bool = True
    lumen_indirect_mult: float = 1.0
    volumetric_scattering_intensity: float = 1.0
    extra_properties: Dict[str, Any] = field(default_factory=dict)
    intensity_lux: Optional[float] = None
    color_temperature_k: Optional[float] = None

    def __post_init__(self) -> None:
        if self.intensity_lux is not None:
            self.intensity = self.intensity_lux
        else:
            self.intensity_lux = self.intensity

        if self.color_temperature_k is not None:
            self.temperature_k = self.color_temperature_k
            self.use_temperature = True
        else:
            self.color_temperature_k = self.temperature_k

    def to_dict(self) -> Dict[str, Any]:
        return {
            "light_id": self.light_id,
            "light_type": self.light_type.value,
            "location": self.location,
            "rotation": self.rotation,
            "color_rgb": self.color_rgb,
            "intensity": self.intensity,
            "intensity_lux": self.intensity,
            "use_temperature": self.use_temperature,
            "temperature_k": self.temperature_k,
            "color_temperature_k": self.temperature_k,
            "attenuation_radius": self.attenuation_radius,
            "inner_cone_angle": self.inner_cone_angle,
            "outer_cone_angle": self.outer_cone_angle,
            "cast_shadows": self.cast_shadows,
            "lumen_indirect_mult": self.lumen_indirect_mult,
            "volumetric_scattering_intensity": self.volumetric_scattering_intensity,
            "extra_properties": self.extra_properties,
        }
