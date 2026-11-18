"""
UAF-81.83: Client Baseline State Tracking and Acknowledgment Confirmation.
"""

from __future__ import annotations

import copy
from typing import Any, Dict, Optional, Set

from ..models.definition import (
    BaselineInvalidatedError,
    EntitySnapshot,
    NetworkEntityId,
)


class ClientBaselineTracker:
    """
    Tracks the acknowledged baseline state for a specific connected client.
    Enables accurate delta compression by knowing exactly what state the client has confirmed.
    """

    def __init__(self, connection_id: str, max_history_ticks: int = 120):
        self.connection_id = connection_id
        self.max_history_ticks = max_history_ticks

        # Last server tick confirmed by the client (0 indicates uninitialized full baseline)
        self.confirmed_tick: int = 0

        # Snapshot history: tick -> Dict[NetworkEntityId, Dict[str, Any]]
        self._history: Dict[int, Dict[NetworkEntityId, Dict[str, Any]]] = {}

        # The authoritative state the client currently has confirmed
        self._confirmed_state: Dict[NetworkEntityId, Dict[str, Any]] = {}

    def record_snapshot(
        self,
        server_tick: int,
        entities: Dict[NetworkEntityId, Dict[str, Any]],
    ) -> None:
        """Store a copy of the outgoing state for this tick to allow future baseline delta diffing."""
        self._history[server_tick] = copy.deepcopy(entities)

        # Evict old history beyond retention window
        cutoff = server_tick - self.max_history_ticks
        evict_ticks = [t for t in self._history if t < cutoff]
        for t in evict_ticks:
            del self._history[t]

    def acknowledge_tick(self, acked_server_tick: int) -> None:
        """
        Mark a server tick as acknowledged by the client.
        Updates the confirmed baseline state.
        """
        if acked_server_tick <= self.confirmed_tick:
            return  # Outdated or duplicate ACK

        if acked_server_tick in self._history:
            self.confirmed_tick = acked_server_tick
            self._confirmed_state = copy.deepcopy(self._history[acked_server_tick])
            # Evict history up to this tick
            evict_ticks = [t for t in self._history if t < acked_server_tick]
            for t in evict_ticks:
                del self._history[t]
        elif acked_server_tick > 0:
            # Client ACKed a tick not in history window
            raise BaselineInvalidatedError(
                f"Client {self.connection_id} ACKed tick {acked_server_tick} not found in history window."
            )

    def get_confirmed_entity_state(self, net_id: NetworkEntityId) -> Optional[Dict[str, Any]]:
        """Return confirmed properties for an entity, or None if client doesn't have it."""
        return self._confirmed_state.get(net_id)

    def get_confirmed_state(self) -> Dict[NetworkEntityId, Dict[str, Any]]:
        """Return a copy of the entire confirmed baseline state."""
        return copy.deepcopy(self._confirmed_state)

    def invalidate(self) -> None:
        """Reset baseline forcing a full resync."""
        self.confirmed_tick = 0
        self._history.clear()
        self._confirmed_state.clear()
