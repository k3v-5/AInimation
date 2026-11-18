"""
UAF-81.84.1: Particle Representation, Lifecycle and Attributes.
"""

from __future__ import annotations

import copy
from dataclasses import dataclass, field
from typing import Any, Dict, Optional

from ..models.definition import (
    ColorRGBA,
    DEFAULT_PARTICLE_SCHEMA,
    ParticleId,
    ParticleLifecycleState,
    ParticleSchema,
    Vec3,
    ensure_finite_float,
    ensure_finite_vec3,
)


class Particle:
    """Represents an individual simulated particle with typed attribute storage."""

    def __init__(
        self,
        particle_id: ParticleId,
        schema: ParticleSchema = DEFAULT_PARTICLE_SCHEMA,
    ):
        self.particle_id = particle_id
        self.state: ParticleLifecycleState = ParticleLifecycleState.SPAWNED
        self.schema = schema
        self.attributes: Dict[str, Any] = {}
        self.reset()

    def reset(self) -> None:
        """Reset particle attributes to schema defaults without allocation."""
        self.state = ParticleLifecycleState.SPAWNED
        self.attributes.clear()
        for attr in self.schema.attributes:
            val = attr.default_value
            if isinstance(val, (list, tuple)):
                self.attributes[attr.name] = tuple(val)
            else:
                self.attributes[attr.name] = val

    @property
    def position(self) -> Vec3:
        return self.attributes.get("position", (0.0, 0.0, 0.0))

    @position.setter
    def position(self, val: Vec3) -> None:
        self.attributes["position"] = ensure_finite_vec3(val, f"Particle({self.particle_id}).position")

    @property
    def velocity(self) -> Vec3:
        return self.attributes.get("velocity", (0.0, 0.0, 0.0))

    @velocity.setter
    def velocity(self, val: Vec3) -> None:
        self.attributes["velocity"] = ensure_finite_vec3(val, f"Particle({self.particle_id}).velocity")

    @property
    def age(self) -> float:
        return float(self.attributes.get("age", 0.0))

    @age.setter
    def age(self, val: float) -> None:
        self.attributes["age"] = ensure_finite_float(val, f"Particle({self.particle_id}).age")

    @property
    def lifetime(self) -> float:
        return float(self.attributes.get("lifetime", 1.0))

    @lifetime.setter
    def lifetime(self, val: float) -> None:
        self.attributes["lifetime"] = ensure_finite_float(val, f"Particle({self.particle_id}).lifetime")

    @property
    def normalized_age(self) -> float:
        lt = self.lifetime
        if lt <= 1e-7:
            return 1.0
        return min(1.0, max(0.0, self.age / lt))

    @property
    def is_alive(self) -> bool:
        return self.state in (ParticleLifecycleState.SPAWNED, ParticleLifecycleState.ACTIVE, ParticleLifecycleState.DYING)
