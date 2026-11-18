"""
UAF-81.84.4: VFX Event System and Dispatcher.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Tuple

from ..models.definition import Vec3, ensure_finite_vec3


@dataclass(frozen=True)
class VFXEvent:
    """Explicitly typed event triggered by particle or gameplay actions."""
    event_id: str
    tick: int
    event_type: str
    position: Vec3 = (0.0, 0.0, 0.0)
    normal: Vec3 = (0.0, 1.0, 0.0)
    payload: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        ensure_finite_vec3(self.position, f"VFXEvent({self.event_id}).position")
        ensure_finite_vec3(self.normal, f"VFXEvent({self.event_id}).normal")


class VFXEventBus:
    """Deterministic event queue and listener dispatcher for VFX systems."""

    def __init__(self):
        self._listeners: Dict[str, List[Callable[[VFXEvent], None]]] = {}
        self._event_queue: List[VFXEvent] = []
        self._processed_event_ids: set[str] = set()

    def subscribe(self, event_type: str, callback: Callable[[VFXEvent], None]) -> None:
        """Subscribe handler to an event type."""
        if event_type not in self._listeners:
            self._listeners[event_type] = []
        self._listeners[event_type].append(callback)

    def post_event(self, event: VFXEvent) -> None:
        """Enqueue event for deterministic dispatch."""
        self._event_queue.append(event)

    def dispatch_all(self) -> int:
        """Deliver all pending events to subscribers and clear queue."""
        dispatched_count = len(self._event_queue)
        events_to_process = list(self._event_queue)
        self._event_queue.clear()

        for ev in events_to_process:
            self._processed_event_ids.add(ev.event_id)
            callbacks = self._listeners.get(ev.event_type, [])
            for cb in callbacks:
                cb(ev)

        return dispatched_count

    def has_processed(self, event_id: str) -> bool:
        """Check if an event was already processed (deduplication check)."""
        return event_id in self._processed_event_ids

    def clear(self) -> None:
        self._event_queue.clear()
        self._processed_event_ids.clear()
