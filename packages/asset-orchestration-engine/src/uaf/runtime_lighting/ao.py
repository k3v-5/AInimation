"""
Ambient Occlusion (SSAO, GTAO, HBAO) for UAF-81.85.
"""

from __future__ import annotations
import math
from dataclasses import dataclass
from typing import Tuple

from .core import AOBackend, ensure_finite_scalar


@dataclass
class AOSettings:
    """
    Screen-space and raytraced ambient occlusion configuration.
    """
    enabled: bool = True
    backend: AOBackend = AOBackend.GTAO
    radius: float = 0.5                  # World-space sample radius in meters
    intensity: float = 0.5               # Occlusion strength
    power: float = 1.0                   # Exponent / contrast curve
    bias: float = 0.05                   # Horizon angle or depth bias
    temporal_accumulation: bool = True

    def __post_init__(self) -> None:
        self.radius = max(0.01, ensure_finite_scalar(self.radius, "radius", 0.5))
        self.intensity = max(0.0, min(2.0, ensure_finite_scalar(self.intensity, "intensity", 0.5)))
        self.power = max(0.1, min(5.0, ensure_finite_scalar(self.power, "power", 1.0)))
        self.bias = max(0.0, min(1.0, ensure_finite_scalar(self.bias, "bias", 0.05)))

    def evaluate_occlusion(self, geometric_curvature: float = 0.0) -> float:
        """
        Computes ambient occlusion visibility factor in [0.0, 1.0].
        1.0 = unoccluded, 0.0 = fully occluded in corners/crevices.
        """
        if not self.enabled or self.intensity <= 0.0:
            return 1.0

        # Curvature > 0 indicates concavity/crevice
        concavity = max(0.0, min(1.0, geometric_curvature))
        occlusion = (concavity ** self.power) * self.intensity
        visibility = max(0.0, min(1.0, 1.0 - occlusion))
        return round(visibility, 6)
