"""
UAF-81.82: Sensory Memory with Deterministic Confidence Decay by Logical Ticks.
"""

from __future__ import annotations

from typing import Dict, List, Optional

from ..models.definition import SensoryMemoryEntry, Vec3


class SensoryMemory:
    """
    Episodic sensory memory storing detected stimuli with monotonic time-to-live (TTL)
    and deterministic confidence decay evaluated strictly over logical simulation ticks.
    """

    def __init__(self, default_ttl_ticks: int = 60):
        self.default_ttl_ticks = default_ttl_ticks
        self._entries: Dict[str, SensoryMemoryEntry] = {}  # source_id -> entry

    @property
    def entries(self) -> Dict[str, SensoryMemoryEntry]:
        return self._entries

    def record_stimulus(
        self,
        stimulus_id: str,
        source_id: str,
        stimulus_type: str,
        position: Vec3,
        strength: float,
        current_tick: int,
        initial_confidence: float = 1.0,
    ) -> SensoryMemoryEntry:
        """Register or update a perceived stimulus in sensory memory."""
        first_tick = current_tick
        if source_id in self._entries:
            first_tick = self._entries[source_id].first_seen_tick

        entry = SensoryMemoryEntry(
            stimulus_id=stimulus_id,
            source_id=source_id,
            stimulus_type=stimulus_type,
            position=position,
            strength=strength,
            first_seen_tick=first_tick,
            last_seen_tick=current_tick,
            confidence=initial_confidence,
        )
        self._entries[source_id] = entry
        return entry

    def update_decay(self, current_tick: int, ttl_ticks: Optional[int] = None) -> List[str]:
        """
        Apply confidence decay across all active memory entries.
        Returns list of expired source_ids purged from memory.
        """
        ttl = ttl_ticks if ttl_ticks is not None else self.default_ttl_ticks
        expired_ids: List[str] = []

        updated_entries: Dict[str, SensoryMemoryEntry] = {}
        for source_id in sorted(self._entries.keys()):
            entry = self._entries[source_id]
            elapsed = current_tick - entry.last_seen_tick
            decay_factor = max(0.0, 1.0 - (float(elapsed) / max(1, ttl)))
            new_conf = round(decay_factor, 5)

            if new_conf <= 0.0:
                expired_ids.append(source_id)
            else:
                updated_entries[source_id] = SensoryMemoryEntry(
                    stimulus_id=entry.stimulus_id,
                    source_id=entry.source_id,
                    stimulus_type=entry.stimulus_type,
                    position=entry.position,
                    strength=entry.strength,
                    first_seen_tick=entry.first_seen_tick,
                    last_seen_tick=entry.last_seen_tick,
                    confidence=new_conf,
                )

        self._entries = updated_entries
        return expired_ids

    def get_entry(self, source_id: str) -> Optional[SensoryMemoryEntry]:
        return self._entries.get(source_id)

    def get_all_sorted(self) -> List[SensoryMemoryEntry]:
        """Return all memories ordered deterministically: (-confidence, source_id ASC)."""
        return sorted(
            self._entries.values(),
            key=lambda e: (-e.confidence, e.source_id)
        )
