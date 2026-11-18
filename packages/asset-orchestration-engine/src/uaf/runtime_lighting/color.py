"""
Linear HDR Color Grading & White Balance for UAF-81.85.
"""

from __future__ import annotations
import math
from dataclasses import dataclass
from typing import Tuple

from .core import ensure_finite_scalar, ensure_finite_vec3


@dataclass
class ColorGradingSettings:
    """
    Linear color grading controls applied before tone mapping.
    """
    saturation: float = 1.0
    contrast: float = 1.0
    gamma: float = 1.0
    gain: Tuple[float, float, float] = (1.0, 1.0, 1.0)
    lift: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    temperature_offset: float = 0.0      # -1.0 to 1.0 (warm / cool shift)
    tint_offset: float = 0.0             # -1.0 to 1.0 (magenta / green shift)

    def __post_init__(self) -> None:
        self.saturation = max(0.0, ensure_finite_scalar(self.saturation, "saturation", 1.0))
        self.contrast = max(0.0, ensure_finite_scalar(self.contrast, "contrast", 1.0))
        self.gamma = max(0.01, ensure_finite_scalar(self.gamma, "gamma", 1.0))
        self.gain = ensure_finite_vec3(self.gain, "gain", (1.0, 1.0, 1.0))
        self.lift = ensure_finite_vec3(self.lift, "lift", (0.0, 0.0, 0.0))
        self.temperature_offset = max(-1.0, min(1.0, ensure_finite_scalar(self.temperature_offset, "temperature_offset", 0.0)))
        self.tint_offset = max(-1.0, min(1.0, ensure_finite_scalar(self.tint_offset, "tint_offset", 0.0)))

    def apply(self, rgb: Tuple[float, float, float]) -> Tuple[float, float, float]:
        """Applies linear grading pipeline to an RGB triplet."""
        r, g, b = rgb

        # 1. White balance tint/temp adjustment
        if self.temperature_offset != 0.0:
            r += self.temperature_offset * 0.1
            b -= self.temperature_offset * 0.1
        if self.tint_offset != 0.0:
            g += self.tint_offset * 0.1

        # 2. Lift / Gain: out = rgb * gain + lift * (1.0 - rgb)
        r = r * self.gain[0] + self.lift[0] * (1.0 - r)
        g = g * self.gain[1] + self.lift[1] * (1.0 - g)
        b = b * self.gain[2] + self.lift[2] * (1.0 - b)

        # 3. Saturation (Rec.709 luminance weights)
        lum = 0.2126 * r + 0.7152 * g + 0.0722 * b
        r = lum + self.saturation * (r - lum)
        g = lum + self.saturation * (g - lum)
        b = lum + self.saturation * (b - lum)

        # 4. Contrast
        if self.contrast != 1.0:
            r = (r - 0.5) * self.contrast + 0.5
            g = (g - 0.5) * self.contrast + 0.5
            b = (b - 0.5) * self.contrast + 0.5

        # 5. Gamma
        if self.gamma != 1.0:
            inv_gamma = 1.0 / self.gamma
            r = (max(0.0, r) ** inv_gamma) if r > 0.0 else 0.0
            g = (max(0.0, g) ** inv_gamma) if g > 0.0 else 0.0
            b = (max(0.0, b) ** inv_gamma) if b > 0.0 else 0.0

        return (max(0.0, round(r, 6)), max(0.0, round(g, 6)), max(0.0, round(b, 6)))
