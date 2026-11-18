"""
Light Base Entity, Properties and Hierarchy for UAF-81.85.
"""

from __future__ import annotations
import math
import hashlib
import json
from dataclasses import dataclass, field
from typing import Any, Dict, Optional, Tuple

from .core import (
    LightId,
    LightType,
    LightMobility,
    LightPriority,
    ensure_finite_scalar,
    ensure_finite_vec3,
    normalize_vec3,
    kelvin_to_rgb,
)


@dataclass
class Light:
    """
    Universal Light representation adhering to UAF-81.85 contracts.
    """
    light_id: LightId
    light_type: LightType = LightType.POINT
    position: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    rotation: Tuple[float, float, float] = (0.0, 0.0, 0.0)  # Pitch, Yaw, Roll (radians)
    direction: Tuple[float, float, float] = (0.0, 0.0, -1.0)
    color: Tuple[float, float, float] = (1.0, 1.0, 1.0)     # Linear RGB
    intensity: float = 1000.0                               # Lux / Candela / Nits
    temperature: float = 6500.0                             # Kelvin
    use_temperature: bool = False
    range: float = 20.0                                     # Meters (attenuation radius)
    falloff_exponent: float = 2.0                           # 2.0 = Inverse Square
    cast_shadows: bool = True
    affect_translucency: bool = True
    affect_volumetrics: bool = True
    mobility: LightMobility = LightMobility.MOVABLE
    priority: LightPriority = LightPriority.GAMEPLAY
    visibility: bool = True

    # Shadow & Contact
    shadow_bias: float = 0.05
    shadow_slope_bias: float = 0.5
    shadow_normal_bias: float = 0.1
    contact_shadow_length: float = 0.02
    shadow_resolution_scale: float = 1.0

    # Indirect & Volumetrics
    indirect_lighting_scale: float = 1.0
    volumetric_scattering_intensity: float = 1.0

    # Attachment & Streaming
    attached_to: Optional[str] = None
    socket_name: Optional[str] = None
    cell_id: Optional[str] = None

    def __post_init__(self) -> None:
        self.sanitize()

    def sanitize(self) -> None:
        """Sanitizes all numeric values to prevent unphysical states or NaNs."""
        self.position = ensure_finite_vec3(self.position, "position")
        self.rotation = ensure_finite_vec3(self.rotation, "rotation")
        self.direction = normalize_vec3(ensure_finite_vec3(self.direction, "direction", (0.0, 0.0, -1.0)))
        self.color = ensure_finite_vec3(self.color, "color", (1.0, 1.0, 1.0))
        # Ensure positive color components
        self.color = (max(0.0, self.color[0]), max(0.0, self.color[1]), max(0.0, self.color[2]))

        self.intensity = max(0.0, ensure_finite_scalar(self.intensity, "intensity", 1000.0))
        self.temperature = max(1000.0, min(40000.0, ensure_finite_scalar(self.temperature, "temperature", 6500.0)))
        self.range = max(0.001, ensure_finite_scalar(self.range, "range", 20.0))
        self.falloff_exponent = max(0.0, ensure_finite_scalar(self.falloff_exponent, "falloff_exponent", 2.0))
        self.shadow_bias = max(0.0, ensure_finite_scalar(self.shadow_bias, "shadow_bias", 0.05))
        self.shadow_slope_bias = max(0.0, ensure_finite_scalar(self.shadow_slope_bias, "shadow_slope_bias", 0.5))
        self.shadow_normal_bias = max(0.0, ensure_finite_scalar(self.shadow_normal_bias, "shadow_normal_bias", 0.1))
        self.contact_shadow_length = max(0.0, ensure_finite_scalar(self.contact_shadow_length, "contact_shadow_length", 0.02))
        self.shadow_resolution_scale = max(0.1, min(4.0, ensure_finite_scalar(self.shadow_resolution_scale, "shadow_resolution_scale", 1.0)))
        self.indirect_lighting_scale = max(0.0, ensure_finite_scalar(self.indirect_lighting_scale, "indirect_lighting_scale", 1.0))
        self.volumetric_scattering_intensity = max(0.0, ensure_finite_scalar(self.volumetric_scattering_intensity, "volumetric_scattering_intensity", 1.0))

    def get_effective_color(self) -> Tuple[float, float, float]:
        """Returns the linear RGB color, multiplied by the blackbody Kelvin color if temperature is enabled."""
        if not self.use_temperature:
            return self.color
        k_rgb = kelvin_to_rgb(self.temperature)
        return (
            round(self.color[0] * k_rgb[0], 6),
            round(self.color[1] * k_rgb[1], 6),
            round(self.color[2] * k_rgb[2], 6),
        )

    def to_dict(self) -> Dict[str, Any]:
        """Serializes the light to a dictionary."""
        return {
            "light_id": self.light_id.value,
            "light_type": self.light_type.value,
            "position": list(self.position),
            "rotation": list(self.rotation),
            "direction": list(self.direction),
            "color": list(self.color),
            "intensity": self.intensity,
            "temperature": self.temperature,
            "use_temperature": self.use_temperature,
            "range": self.range,
            "falloff_exponent": self.falloff_exponent,
            "cast_shadows": self.cast_shadows,
            "affect_translucency": self.affect_translucency,
            "affect_volumetrics": self.affect_volumetrics,
            "mobility": self.mobility.value,
            "priority": self.priority.value,
            "visibility": self.visibility,
            "shadow_bias": self.shadow_bias,
            "shadow_slope_bias": self.shadow_slope_bias,
            "shadow_normal_bias": self.shadow_normal_bias,
            "contact_shadow_length": self.contact_shadow_length,
            "shadow_resolution_scale": self.shadow_resolution_scale,
            "indirect_lighting_scale": self.indirect_lighting_scale,
            "volumetric_scattering_intensity": self.volumetric_scattering_intensity,
            "attached_to": self.attached_to,
            "socket_name": self.socket_name,
            "cell_id": self.cell_id,
        }

    def compute_hash(self) -> str:
        """Computes a canonical SHA-256 hash of the light's state."""
        payload = json.dumps(self.to_dict(), sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()
