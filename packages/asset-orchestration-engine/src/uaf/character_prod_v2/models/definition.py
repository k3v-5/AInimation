"""
CharacterArchetype45, ProportionProfile45, SymmetryMode45, PlatformProfile45, AnatomicalDimensions45, CharacterProdV2Specification models.
UAF-81.45 Sections 4, 5, 9, 20, 138, 146.
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from ...core.hashing.canonical_hasher import CanonicalHasher


class CharacterArchetype45(str, Enum):
    HUMAN = "HUMAN"
    HUMANOID = "HUMANOID"
    ROBOT = "ROBOT"
    ANDROID = "ANDROID"
    CYBORG = "CYBORG"
    ALIEN = "ALIEN"
    CREATURE = "CREATURE"
    MONSTER = "MONSTER"
    BOSS = "BOSS"
    NPC = "NPC"
    PLAYER = "PLAYER"


class ProportionProfile45(str, Enum):
    REALISTIC = "REALISTIC"
    HEROIC = "HEROIC"
    STYLIZED = "STYLIZED"
    HEAVY = "HEAVY"
    SLENDER = "SLENDER"
    ATHLETIC = "ATHLETIC"
    CHILD = "CHILD"
    ELDERLY = "ELDERLY"
    ROBOTIC = "ROBOTIC"
    CUSTOM = "CUSTOM"


class SymmetryMode45(str, Enum):
    FULL = "FULL"
    PARTIAL = "PARTIAL"
    NONE = "NONE"
    ASYMMETRIC_VARIATION = "ASYMMETRIC_VARIATION"


class PlatformProfile45(str, Enum):
    PC_HIGH = "PC_HIGH"
    PC_MEDIUM = "PC_MEDIUM"
    CONSOLE = "CONSOLE"
    MOBILE = "MOBILE"
    CINEMATIC = "CINEMATIC"


@dataclass
class AnatomicalDimensions45:
    height_cm: float = 180.0
    shoulder_width_cm: float = 45.0
    chest_depth_cm: float = 28.0
    torso_length_cm: float = 60.0
    arm_length_cm: float = 75.0
    leg_length_cm: float = 95.0

    @property
    def is_valid(self) -> bool:
        return (
            50.0 <= self.height_cm <= 450.0 and
            self.shoulder_width_cm > 0.0 and
            self.chest_depth_cm > 0.0 and
            self.torso_length_cm > 0.0 and
            self.arm_length_cm > 0.0 and
            self.leg_length_cm > 0.0
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "height_cm": self.height_cm,
            "shoulder_width_cm": self.shoulder_width_cm,
            "chest_depth_cm": self.chest_depth_cm,
            "torso_length_cm": self.torso_length_cm,
            "arm_length_cm": self.arm_length_cm,
            "leg_length_cm": self.leg_length_cm,
        }


@dataclass
class CharacterProdV2Specification:
    character_id: str
    archetype: CharacterArchetype45
    proportion_profile: ProportionProfile45
    symmetry_mode: SymmetryMode45 = SymmetryMode45.FULL
    platform_profile: PlatformProfile45 = PlatformProfile45.PC_HIGH
    dimensions: AnatomicalDimensions45 = field(default_factory=AnatomicalDimensions45)
    bone_count: int = 72
    has_facial_rig: bool = True
    has_clothing: bool = True
    has_hair: bool = True
    has_physics_asset: bool = True
    seed: int = 42

    @property
    def is_valid_production(self) -> bool:
        return (
            self.dimensions.is_valid and
            self.bone_count >= 20 and
            self.has_facial_rig and
            self.has_clothing and
            self.has_hair and
            self.has_physics_asset
        )

    @property
    def definition_hash(self) -> str:
        return CanonicalHasher.compute_hash(self.to_dict())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "character_id": self.character_id,
            "archetype": self.archetype.value,
            "proportion_profile": self.proportion_profile.value,
            "symmetry_mode": self.symmetry_mode.value,
            "platform_profile": self.platform_profile.value,
            "dimensions": self.dimensions.to_dict(),
            "bone_count": self.bone_count,
            "has_facial_rig": self.has_facial_rig,
            "has_clothing": self.has_clothing,
            "has_hair": self.has_hair,
            "has_physics_asset": self.has_physics_asset,
            "seed": self.seed,
        }
