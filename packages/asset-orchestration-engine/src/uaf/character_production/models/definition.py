"""
CharacterType29, CharacterReadinessClass, ProductionBodyProportions, and ProductionCharacterDefinition models.
UAF-81.29 Sections 2, 3, 4, 5, 6, 7, 80 to 85, 120 to 122.
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from ...core.hashing.canonical_hasher import CanonicalHasher


class CharacterType29(str, Enum):
    HUMANOID = "HUMANOID"
    HUMAN = "HUMAN"
    ANDROID = "ANDROID"
    ROBOT = "ROBOT"
    ALIEN = "ALIEN"
    CREATURE = "CREATURE"
    MONSTER = "MONSTER"
    CYBORG = "CYBORG"
    MUTANT = "MUTANT"
    BOSS = "BOSS"
    NPC = "NPC"
    PLAYER = "PLAYER"
    ENEMY = "ENEMY"
    CUSTOM = "CUSTOM"


class CharacterReadinessClass(str, Enum):
    STATIC_CHARACTER = "STATIC_CHARACTER"
    RIGGED_CHARACTER = "RIGGED_CHARACTER"
    ANIMATABLE_CHARACTER = "ANIMATABLE_CHARACTER"
    GAME_READY_CHARACTER = "GAME_READY_CHARACTER"
    UNREAL_READY_CHARACTER = "UNREAL_READY_CHARACTER"


@dataclass
class ProductionBodyProportions:
    height_cm: float = 180.0
    shoulder_ratio: float = 0.25
    arm_ratio: float = 0.45
    leg_ratio: float = 0.50

    @property
    def is_valid(self) -> bool:
        return 50.0 <= self.height_cm <= 400.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "height_cm": self.height_cm,
            "shoulder_ratio": self.shoulder_ratio,
            "arm_ratio": self.arm_ratio,
            "leg_ratio": self.leg_ratio,
        }


@dataclass
class ProductionCharacterDefinition:
    character_id: str
    character_type: CharacterType29
    proportions: ProductionBodyProportions
    bone_count: int = 54
    has_facial_morphs: bool = True
    has_eye_rig: bool = True
    has_hand_rig: bool = True
    readiness_class: CharacterReadinessClass = CharacterReadinessClass.UNREAL_READY_CHARACTER
    seed: int = 42

    @property
    def definition_hash(self) -> str:
        return CanonicalHasher.compute_hash(self.to_dict())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "character_id": self.character_id,
            "character_type": self.character_type.value,
            "proportions": self.proportions.to_dict(),
            "bone_count": self.bone_count,
            "has_facial_morphs": self.has_facial_morphs,
            "has_eye_rig": self.has_eye_rig,
            "has_hand_rig": self.has_hand_rig,
            "readiness_class": self.readiness_class.value,
            "seed": self.seed,
        }
