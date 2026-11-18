"""
UAF-81.84.12: Universal Runtime VFX Fabricator and Central Orchestrator.
"""

from __future__ import annotations

import copy
import hashlib
import json
from typing import Any, Callable, Dict, List, Optional, Sequence, Tuple

from ..emitter.emitter import EmitterConfig, VFXEmitter
from ..emitter.particle import Particle
from ..forces.collision import ParticleCollider
from ..forces.constraints import ParticleConstraint
from ..forces.forces import ForceField
from ..graph.events import VFXEvent, VFXEventBus
from ..graph.graph import SubEmitterBinding, VFXGraph
from ..integration.gameplay import GameplayVFXBridge
from ..integration.world_integration import StreamingCellVFXTracker
from ..management.lod_culling import VFXLODManager
from ..management.pool_budget import VFXBudgetManager, VFXPool
from ..models.definition import (
    DeterminismMode,
    ParticleId,
    SimulationBackendType,
    Vec3,
    VFXBudget,
    VFXLOD,
    VFXMetrics,
    VFXPriority,
    VFXSnapshot,
)
from ..networking.networked_vfx import NetworkVFXManager
from ..niagara.golden_assets import GoldenVFXFactory
from ..profiling.profiler import VFXProfiler
from ..profiling.recovery import VFXRecoveryManager
from ..rendering.renderers import VFXRenderer
from ..simulation.backends import (
    CPUSimulationBackend,
    GPUSimulationBackend,
    ReferenceSimulationBackend,
    VFXSimulationBackend,
)


class UniversalRuntimeVFXFabricator:
    """
    Central orchestrator for headless VFX simulation, event processing,
    multi-backend execution, budgeting, network replication, and state hashing.
    """

    def __init__(
        self,
        session_id: str = "vfx_session_01",
        backend_type: SimulationBackendType = SimulationBackendType.REFERENCE,
        budget: Optional[VFXBudget] = None,
        camera_position: Vec3 = (0.0, 0.0, 0.0),
    ):
        self.session_id = session_id
        self.current_tick: int = 0
        self.world_revision: int = 1
        self.camera_position: Vec3 = camera_position

        # Simulation Backend
        self.backend_type = backend_type
        if backend_type == SimulationBackendType.CPU:
            self.backend: VFXSimulationBackend = CPUSimulationBackend()
        elif backend_type == SimulationBackendType.GPU:
            self.backend = GPUSimulationBackend()
        else:
            self.backend = ReferenceSimulationBackend()

        # Emitters: emitter_id -> VFXEmitter
        self.emitters: Dict[str, VFXEmitter] = {}
        self.emitter_priorities: Dict[str, VFXPriority] = {}
        self.forces: List[ForceField] = []
        self.colliders: List[ParticleCollider] = []
        self.constraints: List[ParticleConstraint] = []

        # Subsystems
        self.event_bus = VFXEventBus()
        self.graph = VFXGraph()
        self.lod_manager = VFXLODManager()
        self.budget_manager = VFXBudgetManager(budget or VFXBudget())
        self.gameplay_bridge = GameplayVFXBridge(self.event_bus)
        self.streaming_tracker = StreamingCellVFXTracker()
        self.network_manager = NetworkVFXManager()
        self.profiler = VFXProfiler()
        self.recovery = VFXRecoveryManager()

    def register_emitter(
        self,
        emitter: VFXEmitter,
        priority: VFXPriority = VFXPriority.NORMAL,
    ) -> None:
        """Register an active emitter in the fabricator."""
        self.emitters[emitter.config.emitter_id] = emitter
        self.emitter_priorities[emitter.config.emitter_id] = priority
        self.world_revision += 1

    def unregister_emitter(self, emitter_id: str) -> None:
        """Unregister and clean up emitter."""
        em = self.emitters.pop(emitter_id, None)
        self.emitter_priorities.pop(emitter_id, None)
        if em:
            em.reset()
        self.world_revision += 1

    def add_force(self, force: ForceField) -> None:
        self.forces.append(force)

    def add_collider(self, collider: ParticleCollider) -> None:
        self.colliders.append(collider)

    def add_constraint(self, constraint: ParticleConstraint) -> None:
        self.constraints.append(constraint)

    def step(self, dt: float = 1.0 / 60.0) -> None:
        """
        Advance one simulation tick:
        1. Evaluate budget and degradation.
        2. Evaluate LOD and culling for each emitter.
        3. Simulate particles through active backend with fail-safe isolation.
        4. Dispatch graph events and sub-emitters.
        5. Record performance profiling.
        """
        self.current_tick += 1

        total_active_particles = sum(len(e.active_particles) for e in self.emitters.values())
        self.budget_manager.check_and_degrade(total_active_particles, len(self.emitters))

        collider = self.colliders[0] if self.colliders else None

        for em_id, emitter in list(self.emitters.items()):
            priority = self.emitter_priorities.get(em_id, VFXPriority.NORMAL)

            # Budget culling check
            if self.budget_manager.should_cull_priority(priority):
                continue

            # LOD evaluation
            pos = emitter.config.initial_position
            lod = self.lod_manager.evaluate_lod(pos, self.camera_position, priority)
            if lod == VFXLOD.CULLED:
                continue

            # Execute simulation with fail-safe recovery boundary
            def update_action():
                self.backend.update(
                    emitter=emitter,
                    dt=dt,
                    forces=self.forces,
                    collider=collider,
                    constraints=self.constraints,
                )

            self.recovery.execute_safe(emitter, update_action, action_name="update")

            # Profiling
            self.profiler.record_emitter_frame(
                emitter_id=em_id,
                active_count=len(emitter.active_particles),
                spawned_count=0,
                cpu_time_ms=0.01,
            )

        # Dispatch queued events
        self.event_bus.dispatch_all()

    def get_state_hash(self) -> str:
        """Return canonical deterministic SHA-256 state hash of all deterministic emitters."""
        systems_data = []
        for em_id in sorted(self.emitters.keys()):
            emitter = self.emitters[em_id]
            if emitter.config.determinism != DeterminismMode.DETERMINISTIC:
                continue  # Non-deterministic visual particles do not affect canonical hash

            particles_data = []
            for p in sorted(emitter.active_particles, key=lambda part: (part.particle_id.index, part.particle_id.generation)):
                if not p.is_alive:
                    continue
                pos = p.position
                vel = p.velocity
                particles_data.append({
                    "idx": p.particle_id.index,
                    "gen": p.particle_id.generation,
                    "pos": (round(pos[0], 3), round(pos[1], 3), round(pos[2], 3)),
                    "vel": (round(vel[0], 3), round(vel[1], 3), round(vel[2], 3)),
                    "age": round(p.age, 3),
                })

            systems_data.append({
                "id": em_id,
                "particle_count": len(particles_data),
                "particles": particles_data,
            })

        payload = {
            "tick": self.current_tick,
            "rev": self.world_revision,
            "systems": systems_data,
        }
        raw = json.dumps(payload, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    def create_checkpoint(self) -> Dict[str, Any]:
        """Generate serializable snapshot checkpoint."""
        emitters_data = []
        for em_id in sorted(self.emitters.keys()):
            emitter = self.emitters[em_id]
            particles_data = []
            for p in emitter.active_particles:
                particles_data.append({
                    "idx": p.particle_id.index,
                    "gen": p.particle_id.generation,
                    "pos": p.position,
                    "vel": p.velocity,
                    "age": p.age,
                    "lt": p.lifetime,
                })
            emitters_data.append({
                "id": em_id,
                "particle_counter": emitter.particle_counter,
                "spawn_accumulator": emitter.spawn_accumulator,
                "particles": particles_data,
            })

        return {
            "session_id": self.session_id,
            "tick": self.current_tick,
            "world_revision": self.world_revision,
            "state_hash": self.get_state_hash(),
            "emitters": copy.deepcopy(emitters_data),
        }

    def restore_checkpoint(self, checkpoint: Dict[str, Any]) -> None:
        """Restore emitter states from checkpoint."""
        self.current_tick = checkpoint["tick"]
        self.world_revision = checkpoint["world_revision"]

        saved_emitters = {e["id"]: e for e in checkpoint.get("emitters", [])}

        for em_id, emitter in self.emitters.items():
            emitter.reset()
            if em_id in saved_emitters:
                e_data = saved_emitters[em_id]
                emitter.particle_counter = e_data.get("particle_counter", 0)
                emitter.spawn_accumulator = e_data.get("spawn_accumulator", 0.0)
                for p_dict in e_data.get("particles", []):
                    spawned = emitter.spawn(1)
                    if spawned:
                        p = spawned[0]
                        p.particle_id = ParticleId(
                            emitter_id=em_id,
                            index=p_dict["idx"],
                            generation=p_dict.get("gen", 0),
                        )
                        p.position = tuple(p_dict["pos"])
                        p.velocity = tuple(p_dict["vel"])
                        p.age = p_dict["age"]
                        p.lifetime = p_dict["lt"]
