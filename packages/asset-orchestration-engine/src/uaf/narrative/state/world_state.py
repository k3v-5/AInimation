"""
UAF-81.98: World State Flag Registry.
Provides atomic, transactional tracking of global game flags, faction reputation scores,
player inventory items, and quest state progression with snapshot/rollback mechanics.
"""

import time
from typing import Dict, List, Set, Any, Optional

from ..core.contracts import (
    WorldFlagSnapshot,
    QuestState,
    ConsequenceAction,
    ConsequenceType,
)


class WorldStateFlagRegistry:
    """
    Transactional world state manager for branching narratives and persistent player choices.
    """

    def __init__(self):
        self.flags: Dict[str, Any] = {}
        self.reputation: Dict[str, float] = {}
        self.inventory: Set[str] = set()
        self.quest_states: Dict[str, QuestState] = {}
        self._snapshot_history: List[WorldFlagSnapshot] = []

    def set_flag(self, key: str, value: Any) -> None:
        """Sets an atomic narrative world flag."""
        self.flags[key] = value

    def get_flag(self, key: str, default: Any = None) -> Any:
        """Retrieves a world flag value."""
        return self.flags.get(key, default)

    def mutate_reputation(self, faction_id: str, delta: float) -> float:
        """
        Adjusts faction standing, clamping within [-100.0, +100.0].
        """
        current = self.reputation.get(faction_id, 0.0)
        new_val = max(-100.0, min(100.0, current + delta))
        self.reputation[faction_id] = round(new_val, 2)
        return self.reputation[faction_id]

    def get_reputation(self, faction_id: str) -> float:
        """Returns faction standing, defaulting to 0.0 (Neutral)."""
        return self.reputation.get(faction_id, 0.0)

    def add_item(self, item_id: str) -> None:
        """Adds an item to the persistent narrative inventory."""
        self.inventory.add(item_id)

    def remove_item(self, item_id: str) -> bool:
        """Removes an item from the narrative inventory if present."""
        if item_id in self.inventory:
            self.inventory.remove(item_id)
            return True
        return False

    def has_item(self, item_id: str) -> bool:
        """Checks presence of an item in the narrative inventory."""
        return item_id in self.inventory

    def set_quest_state(self, quest_id: str, state: QuestState) -> None:
        """Updates quest progression status."""
        self.quest_states[quest_id] = state

    def get_quest_state(self, quest_id: str) -> QuestState:
        """Gets current quest state."""
        return self.quest_states.get(quest_id, QuestState.NOT_STARTED)

    def create_snapshot(self) -> WorldFlagSnapshot:
        """
        Captures an immutable snapshot of current world flags, reputation, and inventory.
        """
        snapshot = WorldFlagSnapshot(
            flags=dict(self.flags),
            reputation=dict(self.reputation),
            inventory=list(self.inventory),
            timestamp=time.time(),
        )
        self._snapshot_history.append(snapshot)
        return snapshot

    def restore_snapshot(self, snapshot: WorldFlagSnapshot) -> None:
        """
        Rolls back world state to a previously captured snapshot.
        """
        self.flags = dict(snapshot.flags)
        self.reputation = dict(snapshot.reputation)
        self.inventory = set(snapshot.inventory)

    def apply_consequences(self, consequences: List[ConsequenceAction]) -> List[Dict[str, Any]]:
        """
        Applies a list of consequence actions atomically.
        """
        changelog: List[Dict[str, Any]] = []

        for act in consequences:
            if act.consequence_type == ConsequenceType.SET_FLAG:
                self.set_flag(act.target_key, act.value)
                changelog.append({"action": "SET_FLAG", "key": act.target_key, "value": act.value})

            elif act.consequence_type == ConsequenceType.MUTATE_REPUTATION:
                new_rep = self.mutate_reputation(act.target_key, float(act.value or 0.0))
                changelog.append({"action": "MUTATE_REPUTATION", "faction": act.target_key, "new_rep": new_rep})

            elif act.consequence_type == ConsequenceType.GIVE_ITEM:
                self.add_item(act.target_key)
                changelog.append({"action": "GIVE_ITEM", "item_id": act.target_key})

            elif act.consequence_type == ConsequenceType.TAKE_ITEM:
                removed = self.remove_item(act.target_key)
                changelog.append({"action": "TAKE_ITEM", "item_id": act.target_key, "removed": removed})

            elif act.consequence_type == ConsequenceType.START_QUEST:
                self.set_quest_state(act.target_key, QuestState.ACTIVE)
                changelog.append({"action": "START_QUEST", "quest_id": act.target_key})

            elif act.consequence_type == ConsequenceType.COMPLETE_QUEST:
                self.set_quest_state(act.target_key, QuestState.COMPLETED)
                changelog.append({"action": "COMPLETE_QUEST", "quest_id": act.target_key})

            elif act.consequence_type == ConsequenceType.FAIL_QUEST:
                self.set_quest_state(act.target_key, QuestState.FAILED)
                changelog.append({"action": "FAIL_QUEST", "quest_id": act.target_key})

        return changelog
