"""
UAF-81.84.10: Predefined Golden VFX Reference Assets.
"""

from __future__ import annotations

from typing import Dict

from ..emitter.emitter import EmitterConfig, SpawnConfig, VFXEmitter
from ..models.definition import RendererType, SpawnMode


class GoldenVFXFactory:
    """Factory producing the 10 normative Golden VFX reference assets."""

    @staticmethod
    def create_basic_fire() -> VFXEmitter:
        cfg = EmitterConfig(
            emitter_id="Golden_BasicFire",
            target_capacity=300,
            max_capacity=500,
            lifetime_min=0.8,
            lifetime_max=1.5,
            spawn_config=SpawnConfig(mode=SpawnMode.RATE, rate=80.0),
            initial_velocity=(0.0, 3.0, 0.0),
            color=(1.0, 0.4, 0.1, 1.0),
            renderer_type=RendererType.SPRITE,
        )
        return VFXEmitter(cfg)

    @staticmethod
    def create_smoke() -> VFXEmitter:
        cfg = EmitterConfig(
            emitter_id="Golden_Smoke",
            target_capacity=200,
            max_capacity=400,
            lifetime_min=2.0,
            lifetime_max=3.5,
            spawn_config=SpawnConfig(mode=SpawnMode.RATE, rate=30.0),
            initial_velocity=(0.0, 1.5, 0.0),
            color=(0.3, 0.3, 0.3, 0.6),
            renderer_type=RendererType.SPRITE,
        )
        return VFXEmitter(cfg)

    @staticmethod
    def create_sparks() -> VFXEmitter:
        cfg = EmitterConfig(
            emitter_id="Golden_Sparks",
            target_capacity=100,
            max_capacity=250,
            lifetime_min=0.3,
            lifetime_max=0.8,
            spawn_config=SpawnConfig(mode=SpawnMode.BURST, burst_count=50, burst_interval=1.0),
            initial_velocity=(0.0, 5.0, 0.0),
            velocity_spread=3.0,
            color=(1.0, 0.9, 0.4, 1.0),
            renderer_type=RendererType.SPRITE,
        )
        return VFXEmitter(cfg)

    @staticmethod
    def create_explosion() -> VFXEmitter:
        cfg = EmitterConfig(
            emitter_id="Golden_Explosion",
            target_capacity=150,
            max_capacity=300,
            lifetime_min=0.5,
            lifetime_max=1.2,
            spawn_config=SpawnConfig(mode=SpawnMode.BURST, burst_count=100),
            initial_velocity=(0.0, 2.0, 0.0),
            velocity_spread=5.0,
            color=(1.0, 0.2, 0.05, 1.0),
            renderer_type=RendererType.SPRITE,
        )
        return VFXEmitter(cfg)

    @staticmethod
    def create_beam() -> VFXEmitter:
        cfg = EmitterConfig(
            emitter_id="Golden_Beam",
            target_capacity=10,
            max_capacity=50,
            lifetime_min=1.0,
            lifetime_max=1.0,
            spawn_config=SpawnConfig(mode=SpawnMode.RATE, rate=5.0),
            color=(0.2, 0.6, 1.0, 1.0),
            renderer_type=RendererType.BEAM,
        )
        return VFXEmitter(cfg)

    @staticmethod
    def create_ribbon() -> VFXEmitter:
        cfg = EmitterConfig(
            emitter_id="Golden_Ribbon",
            target_capacity=60,
            max_capacity=120,
            lifetime_min=1.0,
            lifetime_max=1.5,
            spawn_config=SpawnConfig(mode=SpawnMode.RATE, rate=40.0),
            initial_velocity=(1.0, 0.0, 0.0),
            color=(0.8, 0.1, 0.9, 1.0),
            renderer_type=RendererType.RIBBON,
        )
        return VFXEmitter(cfg)

    @staticmethod
    def create_gpu_fountain() -> VFXEmitter:
        cfg = EmitterConfig(
            emitter_id="Golden_GPUFountain",
            target_capacity=2000,
            max_capacity=5000,
            lifetime_min=2.0,
            lifetime_max=4.0,
            spawn_config=SpawnConfig(mode=SpawnMode.RATE, rate=500.0),
            initial_velocity=(0.0, 8.0, 0.0),
            velocity_spread=2.0,
            color=(0.1, 0.5, 1.0, 0.8),
            renderer_type=RendererType.SPRITE,
        )
        return VFXEmitter(cfg)

    @staticmethod
    def create_mesh_particles() -> VFXEmitter:
        cfg = EmitterConfig(
            emitter_id="Golden_MeshParticles",
            target_capacity=50,
            max_capacity=100,
            lifetime_min=1.5,
            lifetime_max=2.5,
            spawn_config=SpawnConfig(mode=SpawnMode.RATE, rate=15.0),
            initial_velocity=(0.0, 3.0, 0.0),
            renderer_type=RendererType.MESH,
        )
        return VFXEmitter(cfg)

    @staticmethod
    def create_collision_particles() -> VFXEmitter:
        cfg = EmitterConfig(
            emitter_id="Golden_CollisionParticles",
            target_capacity=100,
            max_capacity=200,
            lifetime_min=1.0,
            lifetime_max=2.0,
            spawn_config=SpawnConfig(mode=SpawnMode.RATE, rate=30.0),
            initial_velocity=(2.0, 3.0, 0.0),
            renderer_type=RendererType.SPRITE,
        )
        return VFXEmitter(cfg)

    @staticmethod
    def create_sub_emitter_child() -> VFXEmitter:
        cfg = EmitterConfig(
            emitter_id="Golden_SubEmitterChild",
            target_capacity=50,
            max_capacity=100,
            lifetime_min=0.4,
            lifetime_max=0.8,
            spawn_config=SpawnConfig(mode=SpawnMode.BURST, burst_count=20),
            velocity_spread=4.0,
            color=(1.0, 0.8, 0.2, 1.0),
            renderer_type=RendererType.SPRITE,
        )
        return VFXEmitter(cfg)
