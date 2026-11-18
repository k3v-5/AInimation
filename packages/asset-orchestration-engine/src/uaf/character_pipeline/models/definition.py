"""
CharacterArchetype37, RigType37, ControlType37, CharacterProportions37, CharacterProductionSpecification models.
UAF-81.37 Sections 4, 5, 6, 7, 8, 9, 10, 18, 20, 136.
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from ...core.hashing.canonical_hasher import CanonicalHasher


class CharacterArchetype37(str, Enum):
    HUMAN = "HUMAN"
    HUMANOID = "HUMANOID"
    ROBOT = "ROBOT"
    ANDROID = "ANDROID"
    ALIEN = "ALIEN"
    CREATURE = "CREATURE"
    BOSS = "BOSS"
    HEAVY = "HEAVY"
    LIGHT = "LIGHT"
    CUSTOM = "CUSTOM"


class RigType37(str, Enum):
    HUMANOID = "HUMANOID"
    QUADRUPED = "QUADRUPED"
    ROBOT = "ROBOT"
    CREATURE = "CREATURE"
    CUSTOM = "CUSTOM"


class ControlType37(str, Enum):
    ROOT = "ROOT"
    IK = "IK"
    FK = "FK"
    AIM = "AIM"
    LOOK_AT = "LOOK_AT"
    POLE_VECTOR = "POLE_VECTOR"
    SPACE_SWITCH = "SPACE_SWITCH"
    CUSTOM = "CUSTOM"


@dataclass
class CharacterProportions37:
    height_cm: float = 180.0
    shoulder_width_cm: float = 45.0
    arm_length_cm: float = 75.0
    leg_length_cm: float = 90.0

    @property
    def is_valid(self) -> bool:
        return (
            50.0 <= self.height_cm <= 450.0 and
            self.shoulder_width_cm > 0.0 and
            self.arm_length_cm > 0.0 and
            self.leg_length_cm > 0.0
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "height_cm": self.height_cm,
            "shoulder_width_cm": self.shoulder_width_cm,
            "arm_length_cm": self.arm_length_cm,
            "leg_length_cm": self.leg_length_cm,
        }


@dataclass
class CharacterProductionSpecification:
    character_id: str
    archetype: CharacterArchetype37
    proportions: CharacterProportions37 = field(default_factory=CharacterProportions37)
    bone_count: int = 65
    has_physics_asset: bool = True
    has_facial_rig: bool = True
    clothing_items_count: int = 1
    seed: int = 42

    @property
    def is_valid_rig_structure(self) -> bool:
        return self.proportions.is_valid and self.bone_count >= 15 and self.has_physics_asset

    @property
    def definition_hash(self) -> str:
        return CanonicalHasher.compute_hash(self.to_dict())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "character_id": self.character_id,
            "archetype": self.archetype.value,
            "proportions": self.proportions.to_dict(),
            "bone_count": self.bone_count,
            "has_physics_asset": self.has_physics_asset,
            "has_facial_rig": self.has_facial_rig,
            "clothing_items_count": self.clothing_items_count,
            "seed": self.seed,
        }
