"""
Cell State Machine and Lifecycle Engine (UAF-81.81 Section 4).
Strict deterministic state transitions, contract enforcement, and lifecycle notifications.
"""

from __future__ import annotations

from typing import Callable, Dict, List, Optional, Set, Tuple

from ..models.definition import (
    CellKey,
    CellState,
    InvalidCellStateTransitionError,
)

# Set of strictly legal transitions (from_state, to_state)
LEGAL_TRANSITIONS: Set[Tuple[CellState, CellState]] = {
    (CellState.UNLOADED, CellState.LOADING),     # Load request initiated
    (CellState.LOADING, CellState.LOADED),       # Resources staged and ready in memory
    (CellState.LOADED, CellState.ACTIVE),       # Added to simulation tick & scene graph
    (CellState.ACTIVE, CellState.LOADED),       # Suspended from tick, remains in memory
    (CellState.LOADED, CellState.UNLOADING),    # Eviction started
    (CellState.ACTIVE, CellState.UNLOADING),    # Direct eviction with deactivation
    (CellState.UNLOADING, CellState.UNLOADED),  # Resources freed from memory
    (CellState.LOADING, CellState.UNLOADED),    # Load cancelled or rollback on I/O failure
}


class CellStateMachine:
    """
    Authoritative state machine enforcing valid lifecycle transitions per cell.
    Disallows illegal state jumps and maintains monotonic revision tracking.
    """

    def __init__(self):
        self._cell_states: Dict[CellKey, CellState] = {}
        self._cell_revisions: Dict[CellKey, int] = {}
        self._transition_hooks: Dict[Tuple[CellState, CellState], List[Callable[[CellKey], None]]] = {}

    def get_state(self, key: CellKey) -> CellState:
        return self._cell_states.get(key, CellState.UNLOADED)

    def get_revision(self, key: CellKey) -> int:
        return self._cell_revisions.get(key, 0)

    def can_transition(self, from_state: CellState, to_state: CellState) -> bool:
        return (from_state, to_state) in LEGAL_TRANSITIONS

    def transition(self, key: CellKey, target_state: CellState, reason: str = "") -> CellState:
        """
        Transition a cell to target_state.
        Raises InvalidCellStateTransitionError if the transition is illegal.
        """
        current_state = self.get_state(key)

        # Idempotent no-op
        if current_state == target_state:
            return current_state

        if not self.can_transition(current_state, target_state):
            raise InvalidCellStateTransitionError(key, current_state, target_state, reason)

        # Apply state mutation and increment revision
        self._cell_states[key] = target_state
        self._cell_revisions[key] = self.get_revision(key) + 1

        # Dispatch registered hooks
        pair = (current_state, target_state)
        if pair in self._transition_hooks:
            for hook in self._transition_hooks[pair]:
                hook(key)

        return target_state

    def register_hook(
        self,
        from_state: CellState,
        to_state: CellState,
        callback: Callable[[CellKey], None],
    ) -> None:
        """Register a callback for a specific transition."""
        pair = (from_state, to_state)
        if pair not in self._transition_hooks:
            self._transition_hooks[pair] = []
        self._transition_hooks[pair].append(callback)

    def reset_cell(self, key: CellKey) -> None:
        if key in self._cell_states:
            del self._cell_states[key]
        if key in self._cell_revisions:
            del self._cell_revisions[key]
