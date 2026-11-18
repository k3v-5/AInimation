"""
UAF-81.94: 3D Spatial Audio Attenuation & Strict Rule 10 Enforcement.
Calculates distance attenuation, air absorption high-frequency filtering,
and enforces closed spatial falloff limits (<= 20m) for looping enemy sounds.
"""

from __future__ import annotations

import math
from typing import Dict, Optional, Tuple

from uaf.interactive_audio.core.contracts import (
    AttenuationCurveType,
    SpatialAttenuationProfile,
)


class SpatialAttenuationCalculator:
    """
    Evaluates 3D positional sound propagation, distance falloff,
    air absorption, and stereo binaural panning.
    """

    MAX_PERMISSIBLE_LOOPING_FALLOFF_M: float = 20.0  # Strict upper bound from Rule 10

    @classmethod
    def validate_profile_compliance(cls, profile: SpatialAttenuationProfile) -> bool:
        """
        Enforces Rule 10: Any continuous loop or enemy state SFX must
        have a closed falloff distance <= 20.0 meters.
        """
        if profile.is_looping_spatial:
            return profile.falloff_distance_m <= cls.MAX_PERMISSIBLE_LOOPING_FALLOFF_M
        return True

    @classmethod
    def calculate_distance_gain(
        cls,
        distance_m: float,
        profile: SpatialAttenuationProfile,
    ) -> float:
        """
        Computes linear gain factor [0.0, 1.0] as a function of Euclidean distance.
        Guarantees exact 0.0 (inaudible) beyond falloff distance.
        """
        d = max(0.0, float(distance_m))
        r_inner = profile.inner_radius_m
        r_falloff = profile.falloff_distance_m

        if d <= r_inner:
            return 1.0
        if d >= r_falloff:
            return 0.0

        # Normalized distance between inner radius and falloff
        t = (d - r_inner) / max(0.001, (r_falloff - r_inner))

        curve = profile.curve_type
        if curve == AttenuationCurveType.LINEAR:
            return max(0.0, min(1.0, 1.0 - t))
        elif curve == AttenuationCurveType.NATURAL_SOUND_EXPONENTIAL:
            return max(0.0, min(1.0, (1.0 - t) ** 2.0))
        elif curve == AttenuationCurveType.LOGARITHMIC:
            # Falloff scaled by 1 / (1 + 9t)
            return max(0.0, min(1.0, (1.0 - t) / (1.0 + 4.0 * t)))
        elif curve == AttenuationCurveType.SPHERICAL_INVERSE:
            return max(0.0, min(1.0, r_inner / d * (1.0 - t)))

        return max(0.0, min(1.0, 1.0 - t))

    @classmethod
    def calculate_air_absorption_cutoff(
        cls,
        distance_m: float,
        profile: SpatialAttenuationProfile,
    ) -> float:
        """
        Calculates the low-pass filter cutoff frequency in Hz resulting
        from atmospheric moisture and thermal air absorption over distance.
        """
        d = max(0.0, float(distance_m))
        # Base cutoff is 20 kHz; drops toward ~2 kHz at max range
        loss_db = d * profile.air_absorption_hf_loss_db_per_m
        # Filter cutoff formula: 20000 * 10^(-loss_db / 20)
        cutoff = 20000.0 * (10.0 ** (-loss_db / 20.0))
        return max(1500.0, min(20000.0, round(cutoff, 1)))

    @classmethod
    def calculate_stereo_panning(
        cls,
        source_pos: Tuple[float, float, float],
        listener_pos: Tuple[float, float, float],
        listener_forward: Tuple[float, float, float] = (0.0, 1.0, 0.0),
    ) -> Tuple[float, float]:
        """
        Computes Left and Right channel gains (equal-power) based on the azimuth angle.
        """
        dx = source_pos[0] - listener_pos[0]
        dy = source_pos[1] - listener_pos[1]
        dist_2d = math.hypot(dx, dy)

        if dist_2d < 0.001:
            return 0.7071, 0.7071  # Center

        # Normalize relative vector
        ux = dx / dist_2d
        uy = dy / dist_2d

        # Right vector perpendicular to forward (Z up, right = forward x up)
        fx, fy = listener_forward[0], listener_forward[1]
        f_norm = math.hypot(fx, fy)
        if f_norm > 0.001:
            fx /= f_norm
            fy /= f_norm
        else:
            fx, fy = 0.0, 1.0

        rx = fy
        ry = -fx

        # Pan value in [-1.0, 1.0] (dot product with right vector)
        pan = max(-1.0, min(1.0, ux * rx + uy * ry))

        # Equal-power panning law
        angle = (math.pi / 4.0) * (pan + 1.0)
        left_gain = math.cos(angle)
        right_gain = math.sin(angle)

        return round(left_gain, 4), round(right_gain, 4)
