"""
Bloom & Anamorphic Glow Settings for UAF-81.85.
"""

from __future__ import annotations
import math
from dataclasses import dataclass
from typing import Tuple

from .core import ensure_finite_scalar, ensure_finite_vec3


@dataclass
class BloomSettings:
    """
    Bloom dual-filtering pyramid and anamorphic flare configuration.
    """
    enabled: bool = True
    threshold: float = 1.0           # Luminance threshold to trigger bloom
    knee: float = 0.5                # Soft knee transition [0.0, 1.0]
    intensity: float = 0.67          # Overall bloom intensity
    radius: float = 4.0              # Blur radius in screen percentage
    anamorphic_ratio: float = 1.0    # 1.0 = isotropic circular bloom, >1.0 = wide anamorphic streaks
    tint: Tuple[float, float, float] = (1.0, 1.0, 1.0)

    def __post_init__(self) -> None:
        self.threshold = max(0.0, ensure_finite_scalar(self.threshold, "threshold", 1.0))
        self.knee = max(0.0, min(1.0, ensure_finite_scalar(self.knee, "knee", 0.5)))
        self.intensity = max(0.0, ensure_finite_scalar(self.intensity, "intensity", 0.67))
        self.radius = max(0.1, min(10.0, ensure_finite_scalar(self.radius, "radius", 4.0)))
        self.anamorphic_ratio = max(0.1, min(10.0, ensure_finite_scalar(self.anamorphic_ratio, "anamorphic_ratio", 1.0)))
        self.tint = ensure_finite_vec3(self.tint, "tint", (1.0, 1.0, 1.0))

    def evaluate_prefilter(self, color_hdr: Tuple[float, float, float]) -> Tuple[float, float, float]:
        """
        Thresholds and soft-knees HDR color for bloom pyramid input.
        """
        if not self.enabled or self.intensity <= 0.0:
            return (0.0, 0.0, 0.0)

        r, g, b = color_hdr
        lum = 0.2126 * r + 0.7152 * g + 0.0722 * b

        # Soft knee calculation
        soft = lum - self.threshold + self.knee
        soft = max(0.0, min(2.0 * self.knee, soft))
        soft = (soft * soft) / max(1e-4, 4.0 * self.knee)

        weight = max(soft, lum - self.threshold) / max(1e-4, lum)
        weight = max(0.0, weight) * self.intensity

        return (
            round(r * weight * self.tint[0], 6),
            round(g * weight * self.tint[1], 6),
            round(b * weight * self.tint[2], 6),
        )
