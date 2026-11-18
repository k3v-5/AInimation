"""
UAF-81.83: Server-Side Rollback and Resimulation Engine.
"""

from __future__ import annotations

import copy
from typing import Any, Callable, Dict, List, Optional

from ..models.definition import NetworkEntityId, RollbackError
from .history_buffer import HistoryBuffer


class RollbackEngine:
    """
    Executes authoritative rollback and fast-forward resimulation when late inputs
    or state corrections arrive for a past server tick.
    """

    def __init__(
        self,
        history_buffer: HistoryBuffer,
        simulation_step_fn: Callable[[Dict[NetworkEntityId, Dict[str, Any]], int, float], Dict[NetworkEntityId, Dict[str, Any]]],
        max_rollback_ticks: int = 30,
        fixed_dt: float = 1.0 / 60.0,
    ):
        self.history = history_buffer
        self.simulation_step_fn = simulation_step_fn
        self.max_rollback_ticks = max_rollback_ticks
        self.fixed_dt = fixed_dt
        self.rollback_count: int = 0

    def can_rollback(self, current_tick: int, target_tick: int) -> bool:
        """Check if target tick is within the permitted rollback depth."""
        if target_tick >= current_tick:
            return False
        if current_tick - target_tick > self.max_rollback_ticks:
            return False
        return self.history.get_state_at_tick(target_tick) is not None

    def execute_rollback_resimulation(
        self,
        current_tick: int,
        target_tick: int,
        pre_step_hook: Optional[Callable[[Dict[NetworkEntityId, Dict[str, Any]], int], None]] = None,
    ) -> Dict[NetworkEntityId, Dict[str, Any]]:
        """
        Rewind state to target_tick, apply pre_step_hook (e.g. injecting late input),
        resimulate all ticks up to current_tick, and update history.
        """
        if not self.can_rollback(current_tick, target_tick):
            raise RollbackError(
                f"Cannot rollback to tick {target_tick} from current {current_tick} (max depth: {self.max_rollback_ticks})"
            )

        # 1. Restore historical state
        historical_state = self.history.get_state_at_tick(target_tick)
        if historical_state is None:
            raise RollbackError(f"Historical state for tick {target_tick} missing from buffer")

        state = copy.deepcopy(historical_state)

        # 2. Resimulate tick by tick to current_tick
        for tick in range(target_tick, current_tick):
            if tick == target_tick and pre_step_hook is not None:
                pre_step_hook(state, tick)

            state = self.simulation_step_fn(state, tick, self.fixed_dt)
            # Update history buffer for intermediate resimulated ticks
            self.history.record_state(tick + 1, state)

        self.rollback_count += 1
        return state
