"""
Lens Effects (Vignette, Chromatic Aberration, Grain) for UAF-81.85.
"""

from __future__ import annotations
import math
from dataclasses import dataclass

from .core import ensure_finite_scalar


@dataclass
class LensSettings:
    """
    Optical lens imperfections and artifacts.
    """
    chromatic_aberration: float = 0.0     # Color fringing intensity (0.0 to 5.0)
    vignette_intensity: float = 0.4       # Corner darkening intensity (0.0 to 1.0)
    vignette_smoothness: float = 0.5      # Falloff curvature
    vignette_roundness: float = 1.0       # 1.0 = circular, 0.0 = rectangular
    film_grain_intensity: float = 0.0     # High-frequency film grain noise
    lens_flare_intensity: float = 0.0

    def __post_init__(self) -> None:
        self.chromatic_aberration = max(0.0, min(5.0, ensure_finite_scalar(self.chromatic_aberration, "chromatic_aberration", 0.0)))
        self.vignette_intensity = max(0.0, min(1.0, ensure_finite_scalar(self.vignette_intensity, "vignette_intensity", 0.4)))
        self.vignette_smoothness = max(0.01, min(2.0, ensure_finite_scalar(self.vignette_smoothness, "vignette_smoothness", 0.5)))
        self.film_grain_intensity = max(0.0, min(1.0, ensure_finite_scalar(self.film_grain_intensity, "film_grain_intensity", 0.0)))
        self.lens_flare_intensity = max(0.0, min(5.0, ensure_finite_scalar(self.lens_flare_intensity, "lens_flare_intensity", 0.0)))

    def evaluate_vignette(self, u: float, v: float) -> float:
        """
        Computes vignette transmission factor at normalized screen coordinate (u, v) in [0.0, 1.0].
        Returns 1.0 at center, < 1.0 towards edges.
        """
        if self.vignette_intensity <= 0.0:
            return 1.0

        # Center at (0.0, 0.0), range [-1.0, 1.0]
        cu = (u - 0.5) * 2.0
        cv = (v - 0.5) * 2.0
        dist_sq = cu * cu + cv * cv
        dist = math.sqrt(dist_sq)

        # Smooth falloff
        vig = 1.0 - (dist ** (1.0 / max(0.01, self.vignette_smoothness))) * self.vignette_intensity
        return max(0.0, min(1.0, round(vig, 6)))
