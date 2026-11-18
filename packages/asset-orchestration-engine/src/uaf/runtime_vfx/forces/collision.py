"""
UAF-81.84.3: Particle Collision Detection and Physics Response.
"""

from __future__ import annotations

import math
from typing import List, Optional, Tuple

from ..emitter.particle import Particle
from ..math.operators import (
    vec3_add,
    vec3_dot,
    vec3_length,
    vec3_normalize,
    vec3_scale,
    vec3_sub,
)
from ..models.definition import (
    CollisionMode,
    CollisionResponse,
    ParticleLifecycleState,
    Vec3,
    ensure_finite_float,
    ensure_finite_vec3,
)


class ParticleCollider:
    """Evaluates particle collisions against analytical geometric primitives."""

    def __init__(
        self,
        mode: CollisionMode = CollisionMode.PLANE,
        response: CollisionResponse = CollisionResponse.BOUNCE,
        restitution: float = 0.6,
        friction: float = 0.2,
    ):
        self.mode = mode
        self.response = response
        self.restitution = ensure_finite_float(restitution, "Collider.restitution")
        self.friction = ensure_finite_float(friction, "Collider.friction")

        # Primitive geometry parameters
        self.plane_normal: Vec3 = (0.0, 1.0, 0.0)
        self.plane_distance: float = 0.0
        self.sphere_center: Vec3 = (0.0, 0.0, 0.0)
        self.sphere_radius: float = 5.0
        self.box_min: Vec3 = (-5.0, 0.0, -5.0)
        self.box_max: Vec3 = (5.0, 10.0, 5.0)

    def set_plane(self, normal: Vec3, distance: float = 0.0) -> None:
        self.plane_normal = vec3_normalize(normal)
        self.plane_distance = distance

    def set_sphere(self, center: Vec3, radius: float) -> None:
        self.sphere_center = ensure_finite_vec3(center, "set_sphere.center")
        self.sphere_radius = ensure_finite_float(radius, "set_sphere.radius")

    def set_box(self, box_min: Vec3, box_max: Vec3) -> None:
        self.box_min = ensure_finite_vec3(box_min, "set_box.box_min")
        self.box_max = ensure_finite_vec3(box_max, "set_box.box_max")

    def collide(self, particle: Particle) -> bool:
        """Check and resolve collision for a particle. Returns True if collision occurred."""
        if self.mode == CollisionMode.NONE:
            return False

        has_hit = False
        hit_normal: Vec3 = (0.0, 1.0, 0.0)
        penetration = 0.0

        if self.mode == CollisionMode.PLANE:
            # Signed distance: dot(pos, n) - d
            dist = vec3_dot(particle.position, self.plane_normal) - self.plane_distance
            if dist <= 0.0:
                has_hit = True
                hit_normal = self.plane_normal
                penetration = -dist

        elif self.mode == CollisionMode.SPHERE:
            delta = vec3_sub(particle.position, self.sphere_center)
            d = vec3_length(delta)
            if d <= self.sphere_radius:
                has_hit = True
                hit_normal = vec3_normalize(delta) if d > 1e-6 else (0.0, 1.0, 0.0)
                penetration = self.sphere_radius - d

        elif self.mode == CollisionMode.BOX:
            p = particle.position
            if (
                self.box_min[0] <= p[0] <= self.box_max[0]
                and self.box_min[1] <= p[1] <= self.box_max[1]
                and self.box_min[2] <= p[2] <= self.box_max[2]
            ):
                has_hit = True
                hit_normal = (0.0, 1.0, 0.0)  # Default upwards
                penetration = 0.1

        if not has_hit:
            return False

        # Apply Response
        if self.response == CollisionResponse.KILL:
            particle.state = ParticleLifecycleState.DEAD
            return True

        # Correct penetration
        particle.position = vec3_add(particle.position, vec3_scale(hit_normal, penetration))

        if self.response == CollisionResponse.STICK:
            particle.velocity = (0.0, 0.0, 0.0)
            return True

        v_dot_n = vec3_dot(particle.velocity, hit_normal)
        if v_dot_n < 0.0:
            v_normal = vec3_scale(hit_normal, v_dot_n)
            v_tangent = vec3_sub(particle.velocity, v_normal)

            if self.response in (CollisionResponse.BOUNCE, CollisionResponse.REFLECT):
                # Invert normal velocity with restitution
                v_normal_resp = vec3_scale(v_normal, -self.restitution)
                # Friction dampens tangent velocity
                v_tangent_resp = vec3_scale(v_tangent, max(0.0, 1.0 - self.friction))
                particle.velocity = vec3_add(v_normal_resp, v_tangent_resp)

            elif self.response == CollisionResponse.SLIDE:
                # Remove normal velocity, apply friction
                particle.velocity = vec3_scale(v_tangent, max(0.0, 1.0 - self.friction))

        return True
