"""
UAF-81.83: Entity Dormancy Management.
"""

from __future__ import annotations

from typing import Dict, Set

from ..models.definition import DormancyState, NetworkEntityId


class DormancyManager:
    """
    Tracks dormancy state of network entities.
    Dormant entities do not consume bandwidth or replication ticks until awakened.
    """

    def __init__(self, default_idle_ticks: int = 120):
        self.default_idle_ticks = default_idle_ticks
        self._states: Dict[NetworkEntityId, DormancyState] = {}
        self._last_active_tick: Dict[NetworkEntityId, int] = {}

    def register_entity(self, net_id: NetworkEntityId, initial_state: DormancyState = DormancyState.ACTIVE, current_tick: int = 0) -> None:
        """Register an entity for dormancy tracking."""
        self._states[net_id] = initial_state
        self._last_active_tick[net_id] = current_tick

    def unregister_entity(self, net_id: NetworkEntityId) -> None:
        """Unregister an entity."""
        self._states.pop(net_id, None)
        self._last_active_tick.pop(net_id, None)

    def is_dormant(self, net_id: NetworkEntityId) -> bool:
        """Return whether entity is currently dormant."""
        return self._states.get(net_id, DormancyState.ACTIVE) == DormancyState.DORMANT

    def set_state(self, net_id: NetworkEntityId, state: DormancyState, current_tick: int = 0) -> None:
        """Explicitly set dormancy state."""
        self._states[net_id] = state
        if state == DormancyState.ACTIVE:
            self._last_active_tick[net_id] = current_tick

    def touch(self, net_id: NetworkEntityId, current_tick: int) -> None:
        """Wake up entity or refresh its active timestamp."""
        self._states[net_id] = DormancyState.ACTIVE
        self._last_active_tick[net_id] = current_tick

    def update_auto_dormancy(self, current_tick: int, idle_ticks: int = 0) -> Set[NetworkEntityId]:
        """
        Transition entities to DORMANT if they haven't been touched in idle_ticks.
        Returns set of entities that newly became dormant.
        """
        threshold = idle_ticks if idle_ticks > 0 else self.default_idle_ticks
        newly_dormant: Set[NetworkEntityId] = set()

        for net_id, state in list(self._states.items()):
            if state == DormancyState.ACTIVE:
                last_tick = self._last_active_tick.get(net_id, 0)
                if current_tick - last_tick >= threshold:
                    self._states[net_id] = DormancyState.DORMANT
                    newly_dormant.add(net_id)

        return newly_dormant
