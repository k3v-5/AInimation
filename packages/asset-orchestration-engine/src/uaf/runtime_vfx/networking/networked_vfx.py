"""
UAF-81.84.9: Networked VFX, Causal Event Replication, and Prediction Reconciliation.
"""

from __future__ import annotations

import collections
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Sequence, Set, Tuple

from ..models.definition import Vec3, ensure_finite_vec3


@dataclass(frozen=True)
class NetworkVFXEvent:
    """Network-replicated causal VFX event."""
    event_id: str
    server_tick: int
    effect_id: str
    position: Vec3
    normal: Vec3 = (0.0, 1.0, 0.0)
    source_entity: Optional[str] = None
    effect_revision: int = 1
    seed: int = 1337
    payload: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        ensure_finite_vec3(self.position, f"NetworkVFXEvent({self.event_id}).position")
        ensure_finite_vec3(self.normal, f"NetworkVFXEvent({self.event_id}).normal")


class NetworkVFXManager:
    """
    Handles causal event replication between server and clients,
    client-side prediction, and duplicate suppression.
    """

    def __init__(self, history_window: int = 256):
        self.history_window = history_window
        self._processed_events: collections.deque = collections.deque(maxlen=history_window)
        self._processed_set: Set[str] = set()

        # Locally predicted effects awaiting server confirmation
        self._predicted_events: Dict[str, NetworkVFXEvent] = {}

    def is_duplicate(self, event_id: str) -> bool:
        """Check if an incoming network VFX event was already played."""
        return event_id in self._processed_set

    def register_predicted_event(self, event: NetworkVFXEvent) -> None:
        """Register local client predicted VFX before authoritative server packet arrives."""
        self._predicted_events[event.event_id] = event
        self._mark_processed(event.event_id)

    def process_server_event(self, event: NetworkVFXEvent, spawn_callback: Callable[[NetworkVFXEvent], None]) -> bool:
        """
        Process authoritative server event.
        If already predicted, reconciles smoothly without duplicate spawn.
        If new, spawns the effect using the authoritative seed.
        """
        if event.event_id in self._predicted_events:
            # Confirmed by server - clean up predicted entry
            del self._predicted_events[event.event_id]
            return False  # Already playing locally via prediction

        if self.is_duplicate(event.event_id):
            return False  # Dropped duplicate

        self._mark_processed(event.event_id)
        spawn_callback(event)
        return True

    def _mark_processed(self, event_id: str) -> None:
        if len(self._processed_events) >= self.history_window:
            oldest = self._processed_events.popleft()
            self._processed_set.discard(oldest)

        self._processed_events.append(event_id)
        self._processed_set.add(event_id)

    def clear(self) -> None:
        self._processed_events.clear()
        self._processed_set.clear()
        self._predicted_events.clear()
