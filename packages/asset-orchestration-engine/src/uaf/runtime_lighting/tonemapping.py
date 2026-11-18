"""
Tone Mapping Operators (ACES, Filmic, AgX, Neutral) for UAF-81.85.
"""

from __future__ import annotations
import math
from typing import Tuple

from .core import ToneMapperType


class ToneMapper:
    """
    Evaluates HDR to LDR display transforms using industry-standard operators.
    """

    @staticmethod
    def map_color(
        color_hdr: Tuple[float, float, float],
        mapper_type: ToneMapperType = ToneMapperType.ACES
    ) -> Tuple[float, float, float]:
        """Maps an HDR linear RGB color to [0.0, 1.0] display range."""
        r = max(0.0, float(color_hdr[0]))
        g = max(0.0, float(color_hdr[1]))
        b = max(0.0, float(color_hdr[2]))

        if mapper_type == ToneMapperType.ACES:
            return (
                ToneMapper._aces_fitted(r),
                ToneMapper._aces_fitted(g),
                ToneMapper._aces_fitted(b),
            )
        elif mapper_type == ToneMapperType.FILMIC:
            return (
                ToneMapper._uncharted2_filmic(r),
                ToneMapper._uncharted2_filmic(g),
                ToneMapper._uncharted2_filmic(b),
            )
        elif mapper_type == ToneMapperType.AGX:
            return (
                ToneMapper._agx_approx(r),
                ToneMapper._agx_approx(g),
                ToneMapper._agx_approx(b),
            )
        else:  # NEUTRAL / Reinhard
            return (
                ToneMapper._reinhard(r),
                ToneMapper._reinhard(g),
                ToneMapper._reinhard(b),
            )

    @staticmethod
    def _aces_fitted(x: float) -> float:
        """Krzysztof Narkowicz ACES filmic fitted approximation."""
        a = 2.51
        b = 0.03
        c = 2.43
        d = 0.59
        e = 0.14
        mapped = (x * (a * x + b)) / (x * (c * x + d) + e)
        return max(0.0, min(1.0, round(mapped, 6)))

    @staticmethod
    def _uncharted2_filmic(x: float) -> float:
        """John Hable's Uncharted 2 filmic curve."""
        a = 0.15
        b = 0.50
        c = 0.10
        d = 0.20
        e = 0.02
        f = 0.30
        w = 11.2

        def curve(val: float) -> float:
            return ((val * (a * val + c * b) + d * e) / (val * (a * val + b) + d * f)) - e / f

        curr = curve(x * 2.0)
        white_scale = 1.0 / curve(w)
        mapped = curr * white_scale
        return max(0.0, min(1.0, round(mapped, 6)))

    @staticmethod
    def _agx_approx(x: float) -> float:
        """AgX sigmoid tone response curve approximation."""
        # Simple high-contrast logarithmic curve with soft shoulder
        mapped = x / (1.0 + x * 0.8)
        return max(0.0, min(1.0, round(mapped, 6)))

    @staticmethod
    def _reinhard(x: float) -> float:
        """Classic Reinhard operator: x / (1 + x)."""
        mapped = x / (1.0 + x)
        return max(0.0, min(1.0, round(mapped, 6)))
