"""
UAF-81.84.2: Curves and Interpolation Models.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import List, Sequence, Tuple

from ..models.definition import Vec3, ensure_finite_float, ensure_finite_vec3


@dataclass(frozen=True)
class Keyframe:
    time: float
    value: float
    in_tangent: float = 0.0
    out_tangent: float = 0.0
    interpolation: str = "linear"  # linear, constant, cubic, bezier

    def __post_init__(self):
        ensure_finite_float(self.time, "Keyframe.time")
        ensure_finite_float(self.value, "Keyframe.value")


class FloatCurve:
    """Evaluates a 1D scalar curve over time with multiple interpolation modes."""

    def __init__(self, keyframes: Sequence[Keyframe] | None = None):
        self.keyframes: List[Keyframe] = sorted(keyframes or [], key=lambda k: k.time)

    def add_keyframe(self, keyframe: Keyframe) -> None:
        self.keyframes.append(keyframe)
        self.keyframes.sort(key=lambda k: k.time)

    def evaluate(self, time: float) -> float:
        """Evaluate curve value at given time."""
        if not self.keyframes:
            return 0.0

        if time <= self.keyframes[0].time:
            return self.keyframes[0].value
        if time >= self.keyframes[-1].time:
            return self.keyframes[-1].value

        # Locate segment
        for i in range(len(self.keyframes) - 1):
            k0 = self.keyframes[i]
            k1 = self.keyframes[i + 1]
            if k0.time <= time <= k1.time:
                dt = k1.time - k0.time
                if dt <= 1e-7:
                    return k0.value

                t = (time - k0.time) / dt

                if k0.interpolation == "constant":
                    return k0.value

                if k0.interpolation == "cubic" or k0.interpolation == "bezier":
                    # Hermite cubic spline interpolation
                    t2 = t * t
                    t3 = t2 * t
                    h00 = 2 * t3 - 3 * t2 + 1
                    h10 = t3 - 2 * t2 + t
                    h01 = -2 * t3 + 3 * t2
                    h11 = t3 - t2
                    val = (
                        h00 * k0.value
                        + h10 * k0.out_tangent * dt
                        + h01 * k1.value
                        + h11 * k1.in_tangent * dt
                    )
                    return ensure_finite_float(val, "FloatCurve.evaluate(cubic)")

                # Default linear
                val = k0.value + t * (k1.value - k0.value)
                return ensure_finite_float(val, "FloatCurve.evaluate(linear)")

        return self.keyframes[-1].value


class VectorCurve:
    """Evaluates 3D vector curves using separate FloatCurves per axis."""

    def __init__(
        self,
        x_curve: FloatCurve | None = None,
        y_curve: FloatCurve | None = None,
        z_curve: FloatCurve | None = None,
    ):
        self.x = x_curve or FloatCurve()
        self.y = y_curve or FloatCurve()
        self.z = z_curve or FloatCurve()

    def evaluate(self, time: float) -> Vec3:
        return (
            self.x.evaluate(time),
            self.y.evaluate(time),
            self.z.evaluate(time),
        )
