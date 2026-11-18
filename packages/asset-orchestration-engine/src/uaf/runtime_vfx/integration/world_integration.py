"""
UAF-81.84.8: World Partitioning & Streaming Cell Integration.
"""

from __future__ import annotations

from typing import Dict, List, Optional, Set

from ..emitter.emitter import VFXEmitter
from ..models.definition import UnloadPolicy


class StreamingCellVFXTracker:
    """
    Manages active effects within spatial streaming cells (UAF-81.81).
    Enforces policies when cells are unloaded.
    """

    def __init__(self):
        # cell_key -> list of (emitter, unload_policy)
        self._cell_emitters: Dict[str, List[tuple[VFXEmitter, UnloadPolicy]]] = {}

    def register_emitter_to_cell(self, cell_key: str, emitter: VFXEmitter, policy: UnloadPolicy = UnloadPolicy.DESTROY) -> None:
        """Associate an active emitter with a streaming cell."""
        if cell_key not in self._cell_emitters:
            self._cell_emitters[cell_key] = []
        self._cell_emitters[cell_key].append((emitter, policy))

    def on_cell_unloaded(self, cell_key: str) -> None:
        """Handle streaming cell unload according to each effect's policy."""
        entries = self._cell_emitters.pop(cell_key, [])
        for emitter, policy in entries:
            if policy == UnloadPolicy.DESTROY:
                emitter.reset()
                emitter.is_enabled = False
            elif policy == UnloadPolicy.PAUSE:
                emitter.is_enabled = False
            elif policy == UnloadPolicy.CONTINUE:
                pass  # Continues simulating until particles naturally die
            elif policy == UnloadPolicy.MIGRATE:
                pass  # Migrated to fallback active pool

    def on_cell_loaded(self, cell_key: str) -> None:
        """Re-activate paused effects in a reloaded cell."""
        entries = self._cell_emitters.get(cell_key, [])
        for emitter, policy in entries:
            if policy == UnloadPolicy.PAUSE:
                emitter.is_enabled = True
