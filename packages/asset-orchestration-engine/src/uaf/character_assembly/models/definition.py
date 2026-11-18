"""
CharacterClassification42, SkeletonProfile42, ControlRigType42, RetargetProfile42, SkeletalDimensions42, CharacterAssemblySpecification models.
UAF-81.42 Sections 3, 5, 8, 15, 24, 29, 147.
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from ...core.hashing.canonical_hasher import CanonicalHasher


class CharacterClassification42(str, Enum):
    HUMANOID = "HUMANOID"
    ROBOT = "ROBOT"
    ANDROID = "ANDROID"
    CREATURE = "CREATURE"
    QUADRUPED = "QUADRUPED"
    INSECTOID = "INSECTOID"
    MECHANICAL = "MECHANICAL"
    HYBRID = "HYBRID"
    CUSTOM = "CUSTOM"


class SkeletonProfile42(str, Enum):
    HUMANOID_STANDARD = "HUMANOID_STANDARD"
    HUMANOID_FULL = "HUMANOID_FULL"
    ROBOT_HUMANOID = "ROBOT_HUMANOID"
    CREATURE = "CREATURE"
    QUADRUPED = "QUADRUPED"
    MECHANICAL = "MECHANICAL"
    CUSTOM = "CUSTOM"


class ControlRigType42(str, Enum):
    TRANSLATION = "TRANSLATION"
    ROTATION = "ROTATION"
    SCALE = "SCALE"
    IK = "IK"
    POLE = "POLE"
    AIM = "AIM"
    SPACE = "SPACE"
    CUSTOM = "CUSTOM"


class RetargetProfile42(str, Enum):
    UNREAL_MANNEQUIN = "UNREAL_MANNEQUIN"
    CUSTOM_HUMANOID = "CUSTOM_HUMANOID"
    CREATURE_RETARGET = "CREATURE_RETARGET"
    DIRECT_MAPPING = "DIRECT_MAPPING"


@dataclass
class SkeletalDimensions42:
    height_cm: float = 180.0
    arm_span_cm: float = 175.0
    leg_height_cm: float = 95.0

    @property
    def is_valid(self) -> bool:
        return (
            50.0 <= self.height_cm <= 450.0 and
            self.arm_span_cm > 0.0 and
            self.leg_height_cm > 0.0
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "height_cm": self.height_cm,
            "arm_span_cm": self.arm_span_cm,
            "leg_height_cm": self.leg_height_cm,
        }


@dataclass
class CharacterAssemblySpecification:
    character_id: str
    classification: CharacterClassification42
    skeleton_profile: SkeletonProfile42
    dimensions: SkeletalDimensions42 = field(default_factory=SkeletalDimensions42)
    retarget_profile: RetargetProfile42 = RetargetProfile42.UNREAL_MANNEQUIN
    bone_count: int = 68
    has_ik_chains: bool = True
    has_retarget_profile: bool = True
    has_ragdoll_physics: bool = True
    seed: int = 42

    @property
    def is_valid_assembly(self) -> bool:
        return (
            self.dimensions.is_valid and
            self.bone_count >= 20 and
            self.has_ik_chains and
            self.has_retarget_profile and
            self.has_ragdoll_physics
        )

    @property
    def definition_hash(self) -> str:
        return CanonicalHasher.compute_hash(self.to_dict())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "character_id": self.character_id,
            "classification": self.classification.value,
            "skeleton_profile": self.skeleton_profile.value,
            "dimensions": self.dimensions.to_dict(),
            "retarget_profile": self.retarget_profile.value,
            "bone_count": self.bone_count,
            "has_ik_chains": self.has_ik_chains,
            "has_retarget_profile": self.has_retarget_profile,
            "has_ragdoll_physics": self.has_ragdoll_physics,
            "seed": self.seed,
        }
