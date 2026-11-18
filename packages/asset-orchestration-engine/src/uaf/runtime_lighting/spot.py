"""
Spot Light Implementation for UAF-81.85.
"""

from __future__ import annotations
import math
from dataclasses import dataclass
from typing import Any, Dict

from .core import LightType, ensure_finite_scalar
from .lights import Light


@dataclass
class SpotLight(Light):
    """
    Directional cone light source with inner and outer cone falloff.
    """
    inner_cone_angle: float = 20.0       # Degrees (0.0 to 89.0)
    outer_cone_angle: float = 45.0       # Degrees (inner to 89.9)
    source_radius: float = 0.0           # Soft specular radius
    soft_source_radius: float = 0.0

    def __post_init__(self) -> None:
        self.light_type = LightType.SPOT
        super().__post_init__()
        self.inner_cone_angle = max(0.0, min(89.0, ensure_finite_scalar(self.inner_cone_angle, "inner_cone_angle", 20.0)))
        self.outer_cone_angle = max(self.inner_cone_angle, min(89.9, ensure_finite_scalar(self.outer_cone_angle, "outer_cone_angle", 45.0)))
        self.source_radius = max(0.0, ensure_finite_scalar(self.source_radius, "source_radius", 0.0))
        self.soft_source_radius = max(0.0, ensure_finite_scalar(self.soft_source_radius, "soft_source_radius", 0.0))

    def evaluate_spot_factor(self, cos_angle: float) -> float:
        """
        Calculates smooth angular attenuation factor from cos(theta).
        Returns [0.0, 1.0].
        """
        cos_outer = math.cos(math.radians(self.outer_cone_angle))
        cos_inner = math.cos(math.radians(self.inner_cone_angle))
        if cos_angle <= cos_outer:
            return 0.0
        if cos_angle >= cos_inner:
            return 1.0
        t = (cos_angle - cos_outer) / max(1e-6, (cos_inner - cos_outer))
        # Smoothstep
        return t * t * (3.0 - 2.0 * t)

    def to_dict(self) -> Dict[str, Any]:
        d = super().to_dict()
        d.update({
            "inner_cone_angle": self.inner_cone_angle,
            "outer_cone_angle": self.outer_cone_angle,
            "source_radius": self.source_radius,
            "soft_source_radius": self.soft_source_radius,
        })
        return d
