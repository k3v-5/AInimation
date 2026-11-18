"""
ObjectiveType, ScenarioObjective, EncounterType, and ScenarioEncounter models.
UAF-81.20 Sections 11, 12, 13, 21, 22, 23.
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional


class ObjectiveType(str, Enum):
    REACH = "REACH"
    CAPTURE = "CAPTURE"
    DEFEND = "DEFEND"
    DESTROY = "DESTROY"
    KILL = "KILL"
    COLLECT = "COLLECT"
    RETRIEVE = "RETRIEVE"
    ESCORT = "ESCORT"
    SURVIVE = "SURVIVE"
    ACTIVATE = "ACTIVATE"
    DISABLE = "DISABLE"
    HACK = "HACK"
    BOSS = "BOSS"


@dataclass
class ScenarioObjective:
    objective_id: str
    objective_type: ObjectiveType
    target_id: str
    is_primary: bool = True
    is_reachable: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "objective_id": self.objective_id,
            "objective_type": self.objective_type.value,
            "target_id": self.target_id,
            "is_primary": self.is_primary,
            "is_reachable": self.is_reachable,
        }


class EncounterType(str, Enum):
    AMBUSH = "AMBUSH"
    PATROL = "PATROL"
    ARENA = "ARENA"
    DEFENSE = "DEFENSE"
    HOLDOUT = "HOLDOUT"
    WAVE = "WAVE"
    BOSS = "BOSS"


@dataclass
class ScenarioEncounter:
    encounter_id: str
    encounter_type: EncounterType
    enemy_count: int = 4
    is_solvable: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "encounter_id": self.encounter_id,
            "encounter_type": self.encounter_type.value,
            "enemy_count": self.enemy_count,
            "is_solvable": self.is_solvable,
        }
