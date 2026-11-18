"""
Point Light Implementation for UAF-81.85.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict

from .core import LightType, ensure_finite_scalar
from .lights import Light


@dataclass
class PointLight(Light):
    """
    Omnidirectional point light source emitting in all directions from a point or sphere.
    Intensity is measured in Candelas (or Lumens if lumens_mode is True).
    """
    source_radius: float = 0.0          # Soft specular radius (meters)
    soft_source_radius: float = 0.0     # Penumbra radius (meters)
    source_length: float = 0.0          # For capsule/tube lights

    def __post_init__(self) -> None:
        self.light_type = LightType.POINT
        super().__post_init__()
        self.source_radius = max(0.0, ensure_finite_scalar(self.source_radius, "source_radius", 0.0))
        self.soft_source_radius = max(0.0, ensure_finite_scalar(self.soft_source_radius, "soft_source_radius", 0.0))
        self.source_length = max(0.0, ensure_finite_scalar(self.source_length, "source_length", 0.0))

    def to_dict(self) -> Dict[str, Any]:
        d = super().to_dict()
        d.update({
            "source_radius": self.source_radius,
            "soft_source_radius": self.soft_source_radius,
            "source_length": self.source_length,
        })
        return d
