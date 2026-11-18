"""Knowledge base storing failure symptoms, causes, repairs, and empirical success rates."""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class KnowledgeEntry:
    symptom: str
    cause: str
    repair_action: str
    success_rate: float = 1.0
    times_applied: int = 1


class FailureKnowledgeBase:
    """Historical knowledge base of diagnosed failures and verified automated remedies."""

    def __init__(self) -> None:
        self._entries: Dict[str, KnowledgeEntry] = {}
        self._seed_default_knowledge()

    def _seed_default_knowledge(self) -> None:
        defaults = [
            ("MISSING_TEXTURE_MAP", "Unresolved texture reference in material", "assign_fallback_texture", 1.0),
            ("ORPHAN_ACTOR", "Actor spawned without scene registration", "unregister_orphan_actor", 1.0),
            ("FRAME_SPIKE_VFX", "Emitter particle burst exceeding allocation", "clamp_emitter_spawn_rate", 0.95),
            ("NAV_COLLISION_CLIP", "Actor stuck in geometry collision bounds", "nudge_spawn_position", 1.0),
        ]
        for s, c, r, rate in defaults:
            self._entries[s] = KnowledgeEntry(symptom=s, cause=c, repair_action=r, success_rate=rate)

    def find_remedy(self, symptom: str) -> Optional[KnowledgeEntry]:
        return self._entries.get(symptom)

    def record_repair(self, symptom: str, cause: str, repair_action: str, success: bool) -> None:
        if symptom in self._entries:
            entry = self._entries[symptom]
            entry.times_applied += 1
            entry.success_rate = ((entry.success_rate * (entry.times_applied - 1)) + (1.0 if success else 0.0)) / entry.times_applied
        else:
            self._entries[symptom] = KnowledgeEntry(
                symptom=symptom,
                cause=cause,
                repair_action=repair_action,
                success_rate=1.0 if success else 0.0,
                times_applied=1,
            )
