"""
MissionNodeType41, ObjectiveType41, GameplayState41, CheckpointType41, TriggerType41, MissionFlowMetrics41, PlayableLevelSpecification models.
UAF-81.41 Sections 8, 9, 12, 13, 22, 26, 30, 31, 142.
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from ...core.hashing.canonical_hasher import CanonicalHasher


class MissionNodeType41(str, Enum):
    INTRO = "INTRO"
    TRAVEL = "TRAVEL"
    OBJECTIVE = "OBJECTIVE"
    COMBAT = "COMBAT"
    STEALTH = "STEALTH"
    PUZZLE = "PUZZLE"
    BOSS = "BOSS"
    ESCORT = "ESCORT"
    DEFENSE = "DEFENSE"
    EXTRACTION = "EXTRACTION"
    CHECKPOINT = "CHECKPOINT"
    CUTSCENE = "CUTSCENE"
    END = "END"


class ObjectiveType41(str, Enum):
    REACH = "REACH"
    INTERACT = "INTERACT"
    COLLECT = "COLLECT"
    DESTROY = "DESTROY"
    DEFEND = "DEFEND"
    SURVIVE = "SURVIVE"
    ESCORT = "ESCORT"
    CAPTURE = "CAPTURE"
    ACTIVATE = "ACTIVATE"
    DEACTIVATE = "DEACTIVATE"
    INVESTIGATE = "INVESTIGATE"
    BOSS = "BOSS"
    EXTRACT = "EXTRACT"
    CUSTOM = "CUSTOM"


class GameplayState41(str, Enum):
    INTRO = "INTRO"
    EXPLORATION = "EXPLORATION"
    TRAVEL = "TRAVEL"
    ALERT = "ALERT"
    COMBAT = "COMBAT"
    STEALTH = "STEALTH"
    OBJECTIVE = "OBJECTIVE"
    BOSS = "BOSS"
    EXTRACTION = "EXTRACTION"
    FAILURE = "FAILURE"
    VICTORY = "VICTORY"
    PAUSED = "PAUSED"


class CheckpointType41(str, Enum):
    MISSION_START = "MISSION_START"
    AUTO = "AUTO"
    MANUAL = "MANUAL"
    ENCOUNTER = "ENCOUNTER"
    BOSS = "BOSS"
    OBJECTIVE = "OBJECTIVE"
    EXTRACTION = "EXTRACTION"


class TriggerType41(str, Enum):
    ENTER_VOLUME = "ENTER_VOLUME"
    EXIT_VOLUME = "EXIT_VOLUME"
    INTERACT = "INTERACT"
    KILL_COUNT = "KILL_COUNT"
    OBJECTIVE_COMPLETE = "OBJECTIVE_COMPLETE"
    TIME = "TIME"
    DISTANCE = "DISTANCE"
    HEALTH = "HEALTH"
    ALERT = "ALERT"
    CUSTOM = "CUSTOM"


@dataclass
class MissionFlowMetrics41:
    primary_objective_count: int = 1
    encounter_count: int = 1
    checkpoint_count: int = 1
    has_valid_player_start: bool = True
    has_extraction_or_end: bool = True

    @property
    def is_valid(self) -> bool:
        return (
            self.primary_objective_count >= 1 and
            self.checkpoint_count >= 1 and
            self.has_valid_player_start and
            self.has_extraction_or_end
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "primary_objective_count": self.primary_objective_count,
            "encounter_count": self.encounter_count,
            "checkpoint_count": self.checkpoint_count,
            "has_valid_player_start": self.has_valid_player_start,
            "has_extraction_or_end": self.has_extraction_or_end,
        }


@dataclass
class PlayableLevelSpecification:
    level_id: str
    world_id: str
    mission_type: MissionNodeType41
    metrics: MissionFlowMetrics41 = field(default_factory=MissionFlowMetrics41)
    ai_spaces_count: int = 2
    seed: int = 42

    @property
    def is_valid_mission(self) -> bool:
        return self.metrics.is_valid and self.ai_spaces_count >= 1

    @property
    def definition_hash(self) -> str:
        return CanonicalHasher.compute_hash(self.to_dict())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "level_id": self.level_id,
            "world_id": self.world_id,
            "mission_type": self.mission_type.value,
            "metrics": self.metrics.to_dict(),
            "ai_spaces_count": self.ai_spaces_count,
            "seed": self.seed,
        }
