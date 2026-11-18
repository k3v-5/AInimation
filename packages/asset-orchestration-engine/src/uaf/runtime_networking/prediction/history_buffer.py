"""
UAF-81.83: Rolling Ring History Buffer for Historical Entity States.
"""

from __future__ import annotations

import copy
from typing import Any, Dict, List, Optional, Tuple

from ..models.definition import NetworkEntityId, Vec3


class HistoryBuffer:
    """
    Maintains a rolling ring buffer of historical entity states indexed by server tick.
    Used for lag compensation (rewind hit-checks) and server-side resimulation rollbacks.
    """

    def __init__(self, max_history_ticks: int = 120):
        self.max_history_ticks = max_history_ticks
        self._history: Dict[int, Dict[NetworkEntityId, Dict[str, Any]]] = {}
        self._oldest_tick: int = 0
        self._newest_tick: int = 0

    def record_state(
        self,
        server_tick: int,
        states: Dict[NetworkEntityId, Dict[str, Any]],
    ) -> None:
        """Store a deep copy of entity states for a specific server tick."""
        self._history[server_tick] = copy.deepcopy(states)
        if len(self._history) == 1:
            self._oldest_tick = server_tick
            self._newest_tick = server_tick
        else:
            if server_tick > self._newest_tick:
                self._newest_tick = server_tick
            if server_tick < self._oldest_tick:
                self._oldest_tick = server_tick

        # Evict ticks outside retention window
        cutoff = self._newest_tick - self.max_history_ticks
        evict_ticks = [t for t in self._history if t < cutoff]
        for t in evict_ticks:
            del self._history[t]
        if self._history:
            self._oldest_tick = min(self._history.keys())

    def get_state_at_tick(self, server_tick: int) -> Optional[Dict[NetworkEntityId, Dict[str, Any]]]:
        """Retrieve the exact historical state at a given server tick, or None if unavailable."""
        return self._history.get(server_tick)

    def get_interpolated_entity_state(
        self,
        net_id: NetworkEntityId,
        target_tick: float,
    ) -> Optional[Dict[str, Any]]:
        """
        Interpolate an entity's properties (position/rotation) at fractional tick.
        If exact tick exists, returns it. Otherwise lerps between surrounding ticks.
        """
        floor_tick = int(target_tick)
        ceil_tick = floor_tick + 1
        alpha = target_tick - floor_tick

        if alpha == 0.0 or ceil_tick not in self._history:
            state = self.get_state_at_tick(floor_tick)
            return state.get(net_id) if state else None

        state_a = self.get_state_at_tick(floor_tick)
        state_b = self.get_state_at_tick(ceil_tick)

        if not state_a or not state_b or net_id not in state_a or net_id not in state_b:
            # Fall back to nearest available
            nearest = floor_tick if alpha < 0.5 else ceil_tick
            state = self.get_state_at_tick(nearest)
            return state.get(net_id) if state else None

        props_a = state_a[net_id]
        props_b = state_b[net_id]
        interpolated = copy.deepcopy(props_a)

        # Interpolate 3D position if present
        if "position" in props_a and "position" in props_b:
            pa = props_a["position"]
            pb = props_b["position"]
            if isinstance(pa, (list, tuple)) and isinstance(pb, (list, tuple)) and len(pa) == 3 and len(pb) == 3:
                interpolated["position"] = (
                    pa[0] + (pb[0] - pa[0]) * alpha,
                    pa[1] + (pb[1] - pa[1]) * alpha,
                    pa[2] + (pb[2] - pa[2]) * alpha,
                )

        return interpolated

    def get_available_ticks(self) -> List[int]:
        """Return sorted list of currently retained server ticks."""
        return sorted(self._history.keys())

    def clear(self) -> None:
        self._history.clear()
        self._oldest_tick = 0
        self._newest_tick = 0
