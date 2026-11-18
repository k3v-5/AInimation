"""
UAF-81.98: Procedural Quest Graph & Narrative Core Contracts.
Pydantic v2 domain models and enums for quests, branching DAGs, dialogue nodes,
prerequisites, consequences, skill checks, and world state snapshots.
"""

from enum import Enum
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field


class QuestType(str, Enum):
    MAIN_STORY = "MAIN_STORY"
    FACTION_CONTRACT = "FACTION_CONTRACT"
    SIDE_INVESTIGATION = "SIDE_INVESTIGATION"
    EMERGENT_OPPORTUNITY = "EMERGENT_OPPORTUNITY"


class QuestState(str, Enum):
    NOT_STARTED = "NOT_STARTED"
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    ABANDONED = "ABANDONED"


class MoralAlignment(str, Enum):
    SYNDICATE_LOYAL = "SYNDICATE_LOYAL"
    REBEL_SYMPATHIZER = "REBEL_SYMPATHIZER"
    PRAGMATIC_MERCENARY = "PRAGMATIC_MERCENARY"
    TRUE_NEUTRAL = "TRUE_NEUTRAL"


class DialogueNodeType(str, Enum):
    NPC_STATEMENT = "NPC_STATEMENT"
    PLAYER_CHOICE = "PLAYER_CHOICE"
    SKILL_CHECK = "SKILL_CHECK"
    EVENT_TRIGGER = "EVENT_TRIGGER"
    TERMINAL_RESOLUTION = "TERMINAL_RESOLUTION"


class SkillCheckAttribute(str, Enum):
    PERSUASION = "PERSUASION"
    INTIMIDATION = "INTIMIDATION"
    TECHNICAL_HACK = "TECHNICAL_HACK"
    COMBAT_INTEL = "COMBAT_INTEL"
    PERCEPTION = "PERCEPTION"


class ConditionOperator(str, Enum):
    EQUALS = "EQUALS"
    NOT_EQUALS = "NOT_EQUALS"
    GREATER_THAN = "GREATER_THAN"
    LESS_THAN = "LESS_THAN"
    HAS_ITEM = "HAS_ITEM"
    FACTION_REPUTATION_GE = "FACTION_REPUTATION_GE"


class ConsequenceType(str, Enum):
    SET_FLAG = "SET_FLAG"
    MUTATE_REPUTATION = "MUTATE_REPUTATION"
    GIVE_ITEM = "GIVE_ITEM"
    TAKE_ITEM = "TAKE_ITEM"
    START_QUEST = "START_QUEST"
    COMPLETE_QUEST = "COMPLETE_QUEST"
    FAIL_QUEST = "FAIL_QUEST"


class PrerequisiteCondition(BaseModel):
    condition_key: str
    operator: ConditionOperator
    target_value: Any
    failure_message: str = ""


class ConsequenceAction(BaseModel):
    consequence_type: ConsequenceType
    target_key: str
    value: Any = None


class DialogueChoice(BaseModel):
    choice_id: str
    prompt_text: str
    target_node_id: str
    prerequisites: List[PrerequisiteCondition] = Field(default_factory=list)
    consequences: List[ConsequenceAction] = Field(default_factory=list)
    skill_check_attr: Optional[SkillCheckAttribute] = None
    skill_check_difficulty: int = 0
    fallback_node_id: Optional[str] = None


class DialogueNode(BaseModel):
    node_id: str
    speaker_name: str
    speaker_faction: str = "NEUTRAL"
    dialogue_text: str
    node_type: DialogueNodeType = DialogueNodeType.NPC_STATEMENT
    audio_voice_cue: Optional[str] = None
    choices: List[DialogueChoice] = Field(default_factory=list)
    is_start_node: bool = False
    is_terminal_node: bool = False


class DialogueTreeSpec(BaseModel):
    tree_id: str
    tree_name: str = ""
    nodes: Dict[str, DialogueNode] = Field(default_factory=dict)
    start_node_id: str


class QuestStep(BaseModel):
    step_id: str
    title: str
    description: str
    target_room_id: Optional[str] = None
    is_optional: bool = False
    prerequisite_step_ids: List[str] = Field(default_factory=list)
    completion_consequences: List[ConsequenceAction] = Field(default_factory=list)


class QuestDefinition(BaseModel):
    quest_id: str
    title: str
    quest_type: QuestType = QuestType.MAIN_STORY
    description: str = ""
    recommended_level: int = 1
    faction_id: str = "NEUTRAL"
    steps: Dict[str, QuestStep] = Field(default_factory=dict)
    prerequisite_quest_ids: List[str] = Field(default_factory=list)
    mutually_exclusive_quest_ids: List[str] = Field(default_factory=list)
    rewards: Dict[str, Any] = Field(default_factory=dict)


class WorldFlagSnapshot(BaseModel):
    flags: Dict[str, Any] = Field(default_factory=dict)
    reputation: Dict[str, float] = Field(default_factory=dict)
    inventory: List[str] = Field(default_factory=list)
    timestamp: float = 0.0


class SkillCheckResult(BaseModel):
    attribute: SkillCheckAttribute
    player_skill_level: int
    difficulty: int
    success: bool
    probability: float
