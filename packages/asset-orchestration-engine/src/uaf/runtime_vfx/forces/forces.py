"""
UAF-81.84.3: Physical Force Fields, Gravity, Drag, Wind, Vortices & Noise.
"""

from __future__ import annotations

import math
from typing import List, Tuple

from ..emitter.particle import Particle
from ..math.operators import (
    vec3_add,
    vec3_cross,
    vec3_dot,
    vec3_length,
    vec3_normalize,
    vec3_scale,
    vec3_sub,
)
from ..models.definition import Vec3, ensure_finite_float, ensure_finite_vec3


class ForceField:
    """Base interface for all forces acting on particles."""

    def apply(self, particle: Particle, dt: float) -> None:
        raise NotImplementedError


class GravityForce(ForceField):
    """Applies constant gravitational acceleration to particles."""

    def __init__(self, acceleration: Vec3 = (0.0, -9.81, 0.0)):
        self.acceleration = ensure_finite_vec3(acceleration, "GravityForce.acceleration")

    def apply(self, particle: Particle, dt: float) -> None:
        vx = particle.velocity[0] + self.acceleration[0] * dt
        vy = particle.velocity[1] + self.acceleration[1] * dt
        vz = particle.velocity[2] + self.acceleration[2] * dt
        particle.velocity = (vx, vy, vz)


class DragForce(ForceField):
    """Applies aerodynamic drag resistance opposing particle velocity."""

    def __init__(self, drag_coefficient: float = 0.1):
        self.drag = ensure_finite_float(drag_coefficient, "DragForce.drag")

    def apply(self, particle: Particle, dt: float) -> None:
        damping = max(0.0, 1.0 - self.drag * dt)
        vx = particle.velocity[0] * damping
        vy = particle.velocity[1] * damping
        vz = particle.velocity[2] * damping
        particle.velocity = (vx, vy, vz)


class WindForce(ForceField):
    """Applies directional wind acceleration."""

    def __init__(self, direction: Vec3 = (1.0, 0.0, 0.0), speed: float = 5.0):
        self.direction = vec3_normalize(direction)
        self.speed = ensure_finite_float(speed, "WindForce.speed")

    def apply(self, particle: Particle, dt: float) -> None:
        target_vel = vec3_scale(self.direction, self.speed)
        # Push particle towards wind velocity
        diff = vec3_sub(target_vel, particle.velocity)
        push = vec3_scale(diff, min(1.0, 2.0 * dt))
        particle.velocity = vec3_add(particle.velocity, push)


class PointForce(ForceField):
    """Attractor or repulsor pulling towards or pushing away from a center."""

    def __init__(self, center: Vec3, strength: float = 10.0, radius: float = 20.0):
        self.center = ensure_finite_vec3(center, "PointForce.center")
        self.strength = ensure_finite_float(strength, "PointForce.strength")
        self.radius = ensure_finite_float(radius, "PointForce.radius")

    def apply(self, particle: Particle, dt: float) -> None:
        delta = vec3_sub(self.center, particle.position)
        dist = vec3_length(delta)
        if 1e-4 < dist <= self.radius:
            dir_norm = vec3_scale(delta, 1.0 / dist)
            falloff = 1.0 - (dist / self.radius)
            accel = vec3_scale(dir_norm, self.strength * falloff)
            particle.velocity = vec3_add(particle.velocity, vec3_scale(accel, dt))


class VortexForce(ForceField):
    """Applies rotational acceleration around an axis."""

    def __init__(self, axis: Vec3 = (0.0, 1.0, 0.0), center: Vec3 = (0.0, 0.0, 0.0), speed: float = 5.0):
        self.axis = vec3_normalize(axis)
        self.center = ensure_finite_vec3(center, "VortexForce.center")
        self.speed = ensure_finite_float(speed, "VortexForce.speed")

    def apply(self, particle: Particle, dt: float) -> None:
        r = vec3_sub(particle.position, self.center)
        # Tangent vector = axis x r
        tangent = vec3_cross(self.axis, r)
        t_len = vec3_length(tangent)
        if t_len > 1e-4:
            t_norm = vec3_scale(tangent, 1.0 / t_len)
            particle.velocity = vec3_add(particle.velocity, vec3_scale(t_norm, self.speed * dt))


class CurlNoiseForce(ForceField):
    """Applies pseudo-turbulence curl noise acceleration."""

    def __init__(self, scale: float = 0.5, strength: float = 2.0):
        self.scale = scale
        self.strength = strength

    def apply(self, particle: Particle, dt: float) -> None:
        p = particle.position
        s = self.scale
        # Analytic pseudo-curl from sinusoidal fields
        nx = math.cos(p[1] * s) - math.sin(p[2] * s)
        ny = math.cos(p[2] * s) - math.sin(p[0] * s)
        nz = math.cos(p[0] * s) - math.sin(p[1] * s)
        turb = vec3_scale((nx, ny, nz), self.strength * dt)
        particle.velocity = vec3_add(particle.velocity, turb)
