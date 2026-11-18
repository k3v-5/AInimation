"""
UAF-81.84: Math, Curves and Gradients exports.
"""

from .curves import FloatCurve, Keyframe, VectorCurve
from .gradients import ColorGradient, ColorStop
from .operators import (
    clamp,
    lerp,
    remap,
    saturate,
    smoothstep,
    vec3_add,
    vec3_cross,
    vec3_dot,
    vec3_length,
    vec3_length_sq,
    vec3_lerp,
    vec3_normalize,
    vec3_scale,
    vec3_sub,
)

__all__ = [
    "ColorGradient",
    "ColorStop",
    "FloatCurve",
    "Keyframe",
    "VectorCurve",
    "clamp",
    "lerp",
    "remap",
    "saturate",
    "smoothstep",
    "vec3_add",
    "vec3_cross",
    "vec3_dot",
    "vec3_length",
    "vec3_length_sq",
    "vec3_lerp",
    "vec3_normalize",
    "vec3_scale",
    "vec3_sub",
]
