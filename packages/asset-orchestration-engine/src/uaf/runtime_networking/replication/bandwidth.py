"""
UAF-81.83: Bandwidth Arbiter and Priority Scheduling.
"""

from __future__ import annotations

from typing import Dict, List, Sequence, Set, Tuple

from ..models.definition import (
    BandwidthBudget,
    NetworkEntityId,
    NetworkPriority,
)


class BandwidthArbiter:
    """
    Schedules entity replication according to priority, starvation prevention,
    and configured bandwidth budgets.
    """

    def __init__(self, budget: BandwidthBudget | None = None):
        self.budget = budget or BandwidthBudget()
        self._entity_priorities: Dict[NetworkEntityId, NetworkPriority] = {}
        self._accumulated_priority: Dict[NetworkEntityId, float] = {}
        self._last_sent_tick: Dict[NetworkEntityId, int] = {}

    def register_entity(
        self,
        net_id: NetworkEntityId,
        priority: NetworkPriority = NetworkPriority.NORMAL,
    ) -> None:
        """Register entity replication priority."""
        self._entity_priorities[net_id] = priority
        self._accumulated_priority[net_id] = float(priority.value)
        self._last_sent_tick[net_id] = 0

    def unregister_entity(self, net_id: NetworkEntityId) -> None:
        """Remove entity from bandwidth scheduling."""
        self._entity_priorities.pop(net_id, None)
        self._accumulated_priority.pop(net_id, None)
        self._last_sent_tick.pop(net_id, None)

    def mark_sent(self, net_id: NetworkEntityId, current_tick: int) -> None:
        """Reset accumulated priority when entity state is transmitted."""
        self._last_sent_tick[net_id] = current_tick
        prio = self._entity_priorities.get(net_id, NetworkPriority.NORMAL)
        self._accumulated_priority[net_id] = float(prio.value)

    def prioritize_entities(
        self,
        candidate_ids: Set[NetworkEntityId],
        current_tick: int,
        max_count: int | None = None,
    ) -> List[NetworkEntityId]:
        """
        Rank candidate entities by accumulated priority to prevent starvation,
        and return the top entries within budget.
        """
        scored: List[Tuple[float, NetworkEntityId]] = []

        for net_id in candidate_ids:
            base_prio = self._entity_priorities.get(net_id, NetworkPriority.NORMAL).value
            last_tick = self._last_sent_tick.get(net_id, 0)
            elapsed = max(0, current_tick - last_tick)

            # Accumulate priority: base priority + starvation boost per elapsed tick
            accum = base_prio * 10.0 + elapsed * 2.0
            self._accumulated_priority[net_id] = accum
            scored.append((accum, net_id))

        # Sort descending by score, deterministic tie-breaking on (namespace, value)
        scored.sort(key=lambda item: (-item[0], item[1].namespace, item[1].value))

        limit = max_count if max_count is not None else len(scored)
        return [item[1] for item in scored[:limit]]
