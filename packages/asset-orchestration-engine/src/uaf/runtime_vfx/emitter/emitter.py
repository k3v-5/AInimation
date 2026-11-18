"""
UAF-81.84.1: Particle Emitter and Lifecycle Manager.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Tuple

from ..models.definition import (
    ColorRGBA,
    DEFAULT_PARTICLE_SCHEMA,
    DeterminismMode,
    OverflowPolicy,
    ParticleAttribute,
    ParticleId,
    ParticleLifecycleState,
    ParticleSchema,
    RendererType,
    SpawnMode,
    Vec3,
    ensure_finite_float,
    ensure_finite_vec3,
)
from .particle import Particle


@dataclass(frozen=True)
class SpawnConfig:
    mode: SpawnMode = SpawnMode.RATE
    rate: float = 20.0  # particles per second
    burst_count: int = 0
    burst_interval: float = 0.0


@dataclass(frozen=True)
class EmitterConfig:
    emitter_id: str
    min_capacity: int = 10
    target_capacity: int = 200
    max_capacity: int = 1000
    overflow_policy: OverflowPolicy = OverflowPolicy.DROP_NEW
    lifetime_min: float = 1.0
    lifetime_max: float = 2.0
    spawn_config: SpawnConfig = field(default_factory=SpawnConfig)
    initial_position: Vec3 = (0.0, 0.0, 0.0)
    initial_velocity: Vec3 = (0.0, 1.0, 0.0)
    velocity_spread: float = 0.5
    color: ColorRGBA = (1.0, 1.0, 1.0, 1.0)
    size: Vec3 = (1.0, 1.0, 1.0)
    renderer_type: RendererType = RendererType.SPRITE
    determinism: DeterminismMode = DeterminismMode.DETERMINISTIC
    seed: int = 42


class VFXEmitter:
    """Manages particle allocation, spawning, lifecycle advancement, and recycling."""

    def __init__(
        self,
        config: EmitterConfig,
        schema: ParticleSchema = DEFAULT_PARTICLE_SCHEMA,
    ):
        self.config = config
        self.schema = schema
        self.rng = random.Random(config.seed)

        self.active_particles: List[Particle] = []
        self.particle_pool: List[Particle] = []
        self.spawn_accumulator: float = 0.0
        self.time_since_last_burst: float = 0.0
        self.particle_counter: int = 0
        self.is_enabled: bool = True

        # Pre-allocate min capacity in pool
        for i in range(self.config.min_capacity):
            pid = ParticleId(emitter_id=config.emitter_id, index=i, generation=0)
            p = Particle(particle_id=pid, schema=schema)
            p.state = ParticleLifecycleState.RECYCLED
            self.particle_pool.append(p)

    def reset(self) -> None:
        """Reset emitter state cleanly without leaving ghost particles."""
        for p in self.active_particles:
            p.reset()
            p.state = ParticleLifecycleState.RECYCLED
            self.particle_pool.append(p)
        self.active_particles.clear()
        self.spawn_accumulator = 0.0
        self.time_since_last_burst = 0.0
        self.particle_counter = 0
        self.rng = random.Random(self.config.seed)

    def spawn(self, count: int) -> List[Particle]:
        """Spawn requested count of particles with overflow policy enforcement."""
        if not self.is_enabled or count <= 0:
            return []

        # Check capacity
        available = self.config.max_capacity - len(self.active_particles)
        if available <= 0:
            if self.config.overflow_policy == OverflowPolicy.DROP_NEW:
                return []
            elif self.config.overflow_policy == OverflowPolicy.KILL_OLDEST:
                # Evict oldest particles
                evict_count = min(count, len(self.active_particles))
                for _ in range(evict_count):
                    oldest = self.active_particles.pop(0)
                    oldest.reset()
                    oldest.state = ParticleLifecycleState.RECYCLED
                    self.particle_pool.append(oldest)
            elif self.config.overflow_policy == OverflowPolicy.CLAMP:
                count = min(count, max(0, available))

        spawn_count = min(count, self.config.max_capacity - len(self.active_particles))
        spawned: List[Particle] = []

        for _ in range(spawn_count):
            self.particle_counter += 1
            if self.particle_pool:
                p = self.particle_pool.pop()
                p.reset()
                # Update generation for identification stability
                p.particle_id = ParticleId(
                    emitter_id=self.config.emitter_id,
                    index=p.particle_id.index,
                    generation=p.particle_id.generation + 1,
                )
            else:
                pid = ParticleId(
                    emitter_id=self.config.emitter_id,
                    index=self.particle_counter,
                    generation=0,
                )
                p = Particle(particle_id=pid, schema=self.schema)

            # Initialize attributes
            lt = self.rng.uniform(self.config.lifetime_min, self.config.lifetime_max)
            p.lifetime = ensure_finite_float(lt, "spawn lifetime")
            p.age = 0.0
            p.position = self.config.initial_position

            # Spread velocity
            spread = self.config.velocity_spread
            vx = self.config.initial_velocity[0] + self.rng.uniform(-spread, spread)
            vy = self.config.initial_velocity[1] + self.rng.uniform(-spread, spread)
            vz = self.config.initial_velocity[2] + self.rng.uniform(-spread, spread)
            p.velocity = (vx, vy, vz)

            p.attributes["color"] = self.config.color
            p.attributes["size"] = self.config.size
            p.state = ParticleLifecycleState.ACTIVE

            self.active_particles.append(p)
            spawned.append(p)

        return spawned

    def tick(self, dt: float) -> None:
        """Advance emitter time, age existing particles, and spawn new particles based on mode."""
        if not self.is_enabled:
            return

        dt = ensure_finite_float(dt, "emitter dt")

        # 1. Age existing active particles and cull dead ones
        surviving: List[Particle] = []
        for p in self.active_particles:
            p.age += dt
            if p.age >= p.lifetime:
                p.state = ParticleLifecycleState.DEAD
                p.reset()
                p.state = ParticleLifecycleState.RECYCLED
                self.particle_pool.append(p)
            else:
                surviving.append(p)

        self.active_particles = surviving

        # 2. Spawn new particles for current tick
        cfg = self.config.spawn_config
        if cfg.mode == SpawnMode.RATE and cfg.rate > 0.0:
            self.spawn_accumulator += cfg.rate * dt
            num_to_spawn = int(self.spawn_accumulator)
            if num_to_spawn > 0:
                self.spawn_accumulator -= num_to_spawn
                self.spawn(num_to_spawn)

        elif cfg.mode == SpawnMode.BURST:
            self.time_since_last_burst += dt
            if cfg.burst_interval <= 0.0:
                if self.particle_counter == 0:  # Single burst at start
                    self.spawn(cfg.burst_count)
            elif self.time_since_last_burst >= cfg.burst_interval:
                self.time_since_last_burst = 0.0
                self.spawn(cfg.burst_count)
