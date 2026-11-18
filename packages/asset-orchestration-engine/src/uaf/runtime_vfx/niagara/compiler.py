"""
UAF-81.84.10: VFX Graph and Emitter to UAF VFX IR Compiler.
"""

from __future__ import annotations

from typing import List, Sequence

from ..emitter.emitter import VFXEmitter
from ..models.definition import SimulationBackendType
from .ir import VFXIREmitter, VFXIRModule, VFXIRRenderer, VFXIRSystem


class VFXIRCompiler:
    """Compiles runtime VFX emitters and graphs into decoupled Intermediate Representation."""

    @classmethod
    def compile_emitter(cls, emitter: VFXEmitter, sim_target: str = "CPU") -> VFXIREmitter:
        cfg = emitter.config
        modules: List[VFXIRModule] = []

        # 1. Spawn module
        modules.append(
            VFXIRModule(
                module_name="SpawnBurst_Instantaneous" if cfg.spawn_config.burst_count > 0 else "SpawnRate",
                stage="Spawn",
                parameters={
                    "SpawnRate": cfg.spawn_config.rate,
                    "BurstCount": cfg.spawn_config.burst_count,
                },
            )
        )

        # 2. Initialization module
        modules.append(
            VFXIRModule(
                module_name="InitializeParticle",
                stage="Initialize",
                parameters={
                    "LifetimeMin": cfg.lifetime_min,
                    "LifetimeMax": cfg.lifetime_max,
                    "Color": cfg.color,
                    "Size": cfg.size,
                    "Velocity": cfg.initial_velocity,
                },
            )
        )

        # 3. Renderer IR
        renderer_ir = VFXIRRenderer(
            renderer_type=cfg.renderer_type.value,
            settings={
                "RendererType": cfg.renderer_type.value,
            },
        )

        return VFXIREmitter(
            emitter_id=cfg.emitter_id,
            sim_target=sim_target,
            spawn_mode=cfg.spawn_config.mode.value,
            max_capacity=cfg.max_capacity,
            modules=tuple(modules),
            renderer=renderer_ir,
        )

    @classmethod
    def compile_system(cls, system_id: str, emitters: Sequence[VFXEmitter], revision: int = 1) -> VFXIRSystem:
        ir_emitters = tuple(cls.compile_emitter(em) for em in emitters)
        return VFXIRSystem(
            system_id=system_id,
            revision=revision,
            emitters=ir_emitters,
        )
