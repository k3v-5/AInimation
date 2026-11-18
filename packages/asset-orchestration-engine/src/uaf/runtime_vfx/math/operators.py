"""
UAF-81.84.2: Modular Attribute and Mathematical Operators.
"""

from __future__ import annotations

import math
from typing import Tuple

from ..models.definition import Vec3, ensure_finite_float, ensure_finite_vec3


def clamp(val: float, min_val: float, max_val: float) -> float:
    return max(min_val, min(max_val, val))


def lerp(a: float, b: float, t: float) -> float:
    return a + t * (b - a)


def smoothstep(edge0: float, edge1: float, x: float) -> float:
    t = clamp((x - edge0) / (edge1 - edge0), 0.0, 1.0)
    return t * t * (3.0 - 2.0 * t)


def remap(val: float, in_min: float, in_max: float, out_min: float, out_max: float) -> float:
    if abs(in_max - in_min) <= 1e-7:
        return out_min
    t = (val - in_min) / (in_max - in_min)
    return out_min + t * (out_max - out_min)


def saturate(val: float) -> float:
    return clamp(val, 0.0, 1.0)


# Vector math helpers
def vec3_add(a: Vec3, b: Vec3) -> Vec3:
    return (a[0] + b[0], a[1] + b[1], a[2] + b[2])


def vec3_sub(a: Vec3, b: Vec3) -> Vec3:
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])


def vec3_scale(v: Vec3, s: float) -> Vec3:
    return (v[0] * s, v[1] * s, v[2] * s)


def vec3_dot(a: Vec3, b: Vec3) -> float:
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def vec3_cross(a: Vec3, b: Vec3) -> Vec3:
    return (
        a[1] * b[2] - a[2] * b[1],
        a[2] * b[0] - a[0] * b[2],
        a[0] * b[1] - a[1] * b[0],
    )


def vec3_length_sq(v: Vec3) -> float:
    return v[0] * v[0] + v[1] * v[1] + v[2] * v[2]


def vec3_length(v: Vec3) -> float:
    return math.sqrt(vec3_length_sq(v))


def vec3_normalize(v: Vec3) -> Vec3:
    l = vec3_length(v)
    if l <= 1e-7:
        return (0.0, 0.0, 0.0)
    return (v[0] / l, v[1] / l, v[2] / l)


def vec3_lerp(a: Vec3, b: Vec3, t: float) -> Vec3:
    return (
        lerp(a[0], b[0], t),
        lerp(a[1], b[1], t),
        lerp(a[2], b[2], t),
    )
