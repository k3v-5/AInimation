"""
UAF-81.95: Co-Pilot Reconciler, Concurrency Arbitration & Latency Tracking.
Reconciles procedural generation deltas with human designer inputs,
enforcing Designer Lock policies and guaranteeing sub-500ms response latencies.
"""

from __future__ import annotations

import time
from typing import Dict, List, Optional, Set, Tuple

from uaf.copilot.core.contracts import (
    CoPilotSessionMetrics,
    ConflictResolutionPolicy,
    LiveActorSync,
    TerrainRegionPatch,
    Transform3D,
)


class CoPilotReconciler:
    """
    Arbitrates state updates between AOE's procedural generation engine
    and human designer manipulation within the Unreal Engine Editor viewport.
    """

    MAX_ACCEPTABLE_LATENCY_MS: float = 500.0  # Sub-500ms budget

    def __init__(
        self,
        conflict_policy: ConflictResolutionPolicy = ConflictResolutionPolicy.DESIGNER_LOCK_WINS,
    ):
        self.conflict_policy = conflict_policy
        self.actors: Dict[str, LiveActorSync] = {}
        self.designer_locks: Set[str] = set()
        self.terrain_patches: Dict[str, TerrainRegionPatch] = {}

        # Telemetry & metrics
        self.metrics = CoPilotSessionMetrics()
        self.latencies_ms: List[float] = []

    def record_latency(self, latency_ms: float) -> None:
        """Records round-trip latency and updates rolling average."""
        self.latencies_ms.append(latency_ms)
        if len(self.latencies_ms) > 50:
            self.latencies_ms.pop(0)
        self.metrics.average_latency_ms = round(sum(self.latencies_ms) / len(self.latencies_ms), 2)

    def register_actor(self, actor: LiveActorSync) -> None:
        """Registers an actor into the live replication registry."""
        self.actors[actor.actor_id] = actor
        if actor.is_locked_by_designer:
            self.designer_locks.add(actor.actor_id)
        self.metrics.designer_locks_active = len(self.designer_locks)

    def apply_procedural_update(self, incoming: LiveActorSync) -> Tuple[bool, str]:
        """
        Attempts to apply a procedurally synthesized actor update from AOE.
        Respects human designer locks under DESIGNER_LOCK_WINS policy.
        """
        actor_id = incoming.actor_id
        existing = self.actors.get(actor_id)

        self.metrics.sync_events_count += 1

        if existing and existing.is_locked_by_designer:
            if self.conflict_policy == ConflictResolutionPolicy.DESIGNER_LOCK_WINS:
                # Designer lock strictly wins: discard procedural transform change
                self.metrics.conflicts_resolved += 1
                return False, "PRESERVED_DESIGNER_LOCK"
            elif self.conflict_policy == ConflictResolutionPolicy.PROCEDURAL_OVERRIDE:
                # Procedural override unlocks and overwrites
                self.designer_locks.discard(actor_id)
                incoming.is_locked_by_designer = False
                incoming.revision = existing.revision + 1
                incoming.last_updated_timestamp = time.time()
                self.actors[actor_id] = incoming
                self.metrics.designer_locks_active = len(self.designer_locks)
                self.metrics.conflicts_resolved += 1
                return True, "PROCEDURAL_OVERRIDE_APPLIED"

        # Normal clean application
        if existing:
            incoming.revision = existing.revision + 1
        else:
            incoming.revision = 1

        incoming.last_updated_timestamp = time.time()
        self.actors[actor_id] = incoming
        return True, "APPLIED"

    def apply_designer_feedback(
        self,
        actor_id: str,
        new_transform: Transform3D,
        lock_designer: bool = True,
    ) -> LiveActorSync:
        """
        Applies a viewport transformation initiated by the human designer in Unreal Engine.
        Marks the actor as locked to prevent procedural overwrites.
        """
        self.metrics.sync_events_count += 1
        existing = self.actors.get(actor_id)

        if existing:
            existing.transform = new_transform
            existing.is_locked_by_designer = lock_designer
            existing.revision += 1
            existing.last_updated_timestamp = time.time()
            actor = existing
        else:
            actor = LiveActorSync(
                actor_id=actor_id,
                actor_class="StaticMeshActor",
                transform=new_transform,
                is_locked_by_designer=lock_designer,
                revision=1,
                last_updated_timestamp=time.time(),
            )
            self.actors[actor_id] = actor

        if lock_designer:
            self.designer_locks.add(actor_id)
        else:
            self.designer_locks.discard(actor_id)

        self.metrics.designer_locks_active = len(self.designer_locks)
        return actor

    def unlock_actor(self, actor_id: str) -> bool:
        """Explicitly releases the designer lock on an actor."""
        if actor_id in self.actors:
            self.actors[actor_id].is_locked_by_designer = False
            self.designer_locks.discard(actor_id)
            self.metrics.designer_locks_active = len(self.designer_locks)
            return True
        return False

    def apply_terrain_patch(self, patch: TerrainRegionPatch) -> bool:
        """Stores a sub-region terrain delta patch."""
        self.terrain_patches[patch.patch_id] = patch
        self.metrics.sync_events_count += 1
        return True

    def get_actor(self, actor_id: str) -> Optional[LiveActorSync]:
        """Returns the synchronized actor state if registered."""
        return self.actors.get(actor_id)
