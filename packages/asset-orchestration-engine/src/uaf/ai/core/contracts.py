"""
UAF-81.92: Core Cognitive AI Contracts, WorldState, GOAP Schemas & Faction Enums.
Defines belief state dictionaries, action preconditions/effects, tactical roles,
and sensory stimulus representations.
"""

from __future__ import annotations

import copy
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple
from pydantic import BaseModel, Field


class FactionId(str, Enum):
    """Major factions inhabiting the world."""
    PLAYER = "PLAYER"
    MILITARY_SYNDICATE = "MILITARY_SYNDICATE"
    RENEGADE_RAIDERS = "RENEGADE_RAIDERS"
    COLONIAL_SECURITY = "COLONIAL_SECURITY"
    FERAL_XENOS = "FERAL_XENOS"


class DispositionType(str, Enum):
    """Categorized diplomatic relationship."""
    HOSTILE = "HOSTILE"
    NEUTRAL = "NEUTRAL"
    ALLIED = "ALLIED"


class TacticalRole(str, Enum):
    """Specialized combat responsibilities inside a squad."""
    POINTMAN = "POINTMAN"
    SUPPRESSOR = "SUPPRESSOR"
    FLANKER = "FLANKER"
    SUPPORT_MEDIC = "SUPPORT_MEDIC"


class StimulusType(str, Enum):
    """Type of sensory signal detected by agents."""
    VISION = "VISION"
    SOUND = "SOUND"
    DAMAGE_HIT = "DAMAGE_HIT"


class PerceptionStimulus(BaseModel):
    """Discrete sensory signal emitted in world coordinates."""
    stimulus_id: str
    stimulus_type: StimulusType
    source_pos: Tuple[float, float, float]  # [X, Y, Z] in Unreal cm
    intensity: float = 1.0
    timestamp: float = 0.0


class WorldState(BaseModel):
    """
    Belief state dictionary representing an agent's internal view of reality.
    Stores boolean, numeric, or categorical atomic variables.
    """
    values: Dict[str, Any] = Field(default_factory=dict)

    def get(self, key: str, default: Any = None) -> Any:
        return self.values.get(key, default)

    def set(self, key: str, value: Any) -> None:
        self.values[key] = value

    def satisfies(self, conditions: Dict[str, Any]) -> bool:
        """Checks if all specified key-value conditions are met by this state."""
        for k, v in conditions.items():
            if self.values.get(k) != v:
                return False
        return True

    def apply_effects(self, effects: Dict[str, Any]) -> WorldState:
        """Returns a new WorldState with the specified effects applied."""
        new_values = copy.deepcopy(self.values)
        new_values.update(effects)
        return WorldState(values=new_values)

    def heuristic_distance(self, target_conditions: Dict[str, Any]) -> int:
        """Returns the number of unsatisfied conditions as an admissible A* heuristic."""
        count = 0
        for k, v in target_conditions.items():
            if self.values.get(k) != v:
                count += 1
        return count

    def clone(self) -> WorldState:
        return WorldState(values=copy.deepcopy(self.values))


class GOAPAction(BaseModel):
    """
    Atomic action available to an agent.
    Transitions WorldState from preconditions to effects at an operational cost.
    """
    action_id: str
    name: str
    preconditions: Dict[str, Any] = Field(default_factory=dict)
    effects: Dict[str, Any] = Field(default_factory=dict)
    cost: float = Field(default=1.0, gt=0.0)
    duration_sec: float = Field(default=1.0, ge=0.0)
    animation_cue: str = ""

    def can_execute(self, state: WorldState) -> bool:
        """Evaluates whether all preconditions are currently satisfied."""
        return state.satisfies(self.preconditions)


class GOAPGoal(BaseModel):
    """
    Desired target state condition that the GOAP planner attempts to achieve.
    """
    goal_id: str
    name: str
    target_state: Dict[str, Any]
    priority: float = Field(default=1.0, ge=0.0)

    def is_satisfied(self, state: WorldState) -> bool:
        """Checks if the agent's current belief satisfies all target conditions."""
        return state.satisfies(self.target_state)
