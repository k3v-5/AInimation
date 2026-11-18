"""
CharacterType33, CharacterGenerationStrategy33, CharacterBodyProportions33, and CharacterCreatureRigDefinition models.
UAF-81.33 Sections 2, 3, 4, 6, 8, 9, 131.
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from ...core.hashing.canonical_hasher import CanonicalHasher


class CharacterType33(str, Enum):
    PLAYER = "PLAYER"
    NPC = "NPC"
    ENEMY = "ENEMY"
    BOSS = "BOSS"
    CREATURE = "CREATURE"
    ROBOT = "ROBOT"
    ANDROID = "ANDROID"
    ALIEN = "ALIEN"
    HUMANOID = "HUMANOID"
    MUTANT = "MUTANT"
    MECHANICAL_CHARACTER = "MECHANICAL_CHARACTER"
    HYBRID_CHARACTER = "HYBRID_CHARACTER"


class CharacterGenerationStrategy33(str, Enum):
    PRIMITIVE = "PRIMITIVE"
    MODULAR = "MODULAR"
    PARAMETRIC = "PARAMETRIC"
    DEFORMED_TEMPLATE = "DEFORMED_TEMPLATE"
    HYBRID = "HYBRID"
    CUSTOM = "CUSTOM"


@dataclass
class CharacterBodyProportions33:
    height_cm: float = 180.0
    shoulder_width_cm: float = 45.0
    chest_width_cm: float = 40.0
    waist_width_cm: float = 32.0
    hip_width_cm: float = 36.0
    arm_length_cm: float = 75.0
    leg_length_cm: float = 90.0

    @property
    def is_valid(self) -> bool:
        return (
            50.0 <= self.height_cm <= 400.0 and
            self.shoulder_width_cm > 0.0 and
            self.chest_width_cm > 0.0 and
            self.waist_width_cm > 0.0 and
            self.hip_width_cm > 0.0 and
            self.arm_length_cm > 0.0 and
            self.leg_length_cm > 0.0
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "height_cm": self.height_cm,
            "shoulder_width_cm": self.shoulder_width_cm,
            "chest_width_cm": self.chest_width_cm,
            "waist_width_cm": self.waist_width_cm,
            "hip_width_cm": self.hip_width_cm,
            "arm_length_cm": self.arm_length_cm,
            "leg_length_cm": self.leg_length_cm,
        }


@dataclass
class CharacterCreatureRigDefinition:
    character_id: str
    character_type: CharacterType33
    strategy: CharacterGenerationStrategy33 = CharacterGenerationStrategy33.HYBRID
    proportions: CharacterBodyProportions33 = field(default_factory=CharacterBodyProportions33)
    bone_count: int = 65
    has_facial_rig: bool = False
    has_clothing: bool = False
    has_armor: bool = False
    seed: int = 42

    @property
    def is_valid_skeleton(self) -> bool:
        return self.bone_count >= 15

    @property
    def definition_hash(self) -> str:
        return CanonicalHasher.compute_hash(self.to_dict())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "character_id": self.character_id,
            "character_type": self.character_type.value,
            "strategy": self.strategy.value,
            "proportions": self.proportions.to_dict(),
            "bone_count": self.bone_count,
            "has_facial_rig": self.has_facial_rig,
            "has_clothing": self.has_clothing,
            "has_armor": self.has_armor,
            "seed": self.seed,
        }
