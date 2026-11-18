"""
GameModeType, ScenarioLevelState, and PlayableScenarioDefinition models.
UAF-81.20 Sections 3, 4, 5.
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from ...core.hashing.canonical_hasher import CanonicalHasher


class GameModeType(str, Enum):
    LINEAR = "LINEAR"
    MISSION = "MISSION"
    ARENA = "ARENA"
    SURVIVAL = "SURVIVAL"
    ESCORT = "ESCORT"
    DEFENSE = "DEFENSE"
    EXPLORATION = "EXPLORATION"
    BOSS = "BOSS"
    PUZZLE = "PUZZLE"
    HYBRID = "HYBRID"


class ScenarioLevelState(str, Enum):
    NOT_STARTED = "NOT_STARTED"
    STARTED = "STARTED"
    IN_PROGRESS = "IN_PROGRESS"
    OBJECTIVE_ACTIVE = "OBJECTIVE_ACTIVE"
    ENCOUNTER_ACTIVE = "ENCOUNTER_ACTIVE"
    CHECKPOINT_REACHED = "CHECKPOINT_REACHED"
    BOSS_ACTIVE = "BOSS_ACTIVE"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    ABORTED = "ABORTED"


@dataclass
class PlayableScenarioDefinition:
    scenario_id: str
    world_id: str
    game_mode: GameModeType = GameModeType.MISSION
    difficulty_tier: str = "NORMAL"  # "EASY", "NORMAL", "HARD", "NIGHTMARE"
    seed: int = 42

    @property
    def definition_hash(self) -> str:
        return CanonicalHasher.compute_hash(self.to_dict())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "scenario_id": self.scenario_id,
            "world_id": self.world_id,
            "game_mode": self.game_mode.value,
            "difficulty_tier": self.difficulty_tier,
            "seed": self.seed,
        }
