"""
UAF-81.84.2: Color Gradients and Color Interpolation.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Sequence, Tuple

from ..models.definition import ColorRGBA, ensure_finite_float


@dataclass(frozen=True)
class ColorStop:
    time: float  # Normalized 0.0 to 1.0
    color: ColorRGBA  # (r, g, b, a)

    def __post_init__(self):
        ensure_finite_float(self.time, "ColorStop.time")
        for c in self.color:
            ensure_finite_float(c, "ColorStop.color")


class ColorGradient:
    """Evaluates RGBA color interpolation across normalized keys."""

    def __init__(self, stops: Sequence[ColorStop] | None = None):
        self.stops: List[ColorStop] = sorted(stops or [], key=lambda s: s.time)

    def add_stop(self, stop: ColorStop) -> None:
        self.stops.append(stop)
        self.stops.sort(key=lambda s: s.time)

    def evaluate(self, time: float) -> ColorRGBA:
        """Evaluate color at normalized time (clamped to [0.0, 1.0])."""
        if not self.stops:
            return (1.0, 1.0, 1.0, 1.0)

        t = max(0.0, min(1.0, time))

        if t <= self.stops[0].time:
            return self.stops[0].color
        if t >= self.stops[-1].time:
            return self.stops[-1].color

        for i in range(len(self.stops) - 1):
            s0 = self.stops[i]
            s1 = self.stops[i + 1]
            if s0.time <= t <= s1.time:
                dt = s1.time - s0.time
                if dt <= 1e-7:
                    return s0.color
                factor = (t - s0.time) / dt
                c0 = s0.color
                c1 = s1.color
                return (
                    c0[0] + factor * (c1[0] - c0[0]),
                    c0[1] + factor * (c1[1] - c0[1]),
                    c0[2] + factor * (c1[2] - c0[2]),
                    c0[3] + factor * (c1[3] - c0[3]),
                )

        return self.stops[-1].color
