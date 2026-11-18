"""
UAF-81.84.3: Particle Physical Constraints.
"""

from __future__ import annotations

from typing import Tuple

from ..emitter.particle import Particle
from ..math.operators import (
    vec3_add,
    vec3_length,
    vec3_normalize,
    vec3_scale,
    vec3_sub,
)
from ..models.definition import ConstraintType, Vec3, ensure_finite_float, ensure_finite_vec3


class ParticleConstraint:
    """Base physical constraint."""

    def apply(self, particle: Particle, dt: float) -> None:
        raise NotImplementedError


class VelocityConstraint(ParticleConstraint):
    """Clamps maximum particle speed."""

    def __init__(self, max_speed: float = 50.0):
        self.max_speed = ensure_finite_float(max_speed, "VelocityConstraint.max_speed")

    def apply(self, particle: Particle, dt: float) -> None:
        speed = vec3_length(particle.velocity)
        if speed > self.max_speed and speed > 1e-6:
            scale = self.max_speed / speed
            particle.velocity = vec3_scale(particle.velocity, scale)


class DistanceConstraint(ParticleConstraint):
    """Constrains particle position to remain within max_distance of an anchor."""

    def __init__(self, anchor: Vec3 = (0.0, 0.0, 0.0), max_distance: float = 20.0):
        self.anchor = ensure_finite_vec3(anchor, "DistanceConstraint.anchor")
        self.max_distance = ensure_finite_float(max_distance, "DistanceConstraint.max_distance")

    def apply(self, particle: Particle, dt: float) -> None:
        delta = vec3_sub(particle.position, self.anchor)
        d = vec3_length(delta)
        if d > self.max_distance and d > 1e-6:
            dir_norm = vec3_scale(delta, 1.0 / d)
            particle.position = vec3_add(self.anchor, vec3_scale(dir_norm, self.max_distance))
