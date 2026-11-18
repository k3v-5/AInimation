"""
CharacterType49, SpeciesType49, BodyRepresentation49, BodyDimensions49, CharacterCreatureSpecification models.
UAF-81.49 Sections 4, 5, 6, 8, 10, 140, 158.
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from ...core.hashing.canonical_hasher import CanonicalHasher


class CharacterType49(str, Enum):
    PLAYER = "PLAYER"
    NPC = "NPC"
    ENEMY = "ENEMY"
    ELITE = "ELITE"
    BOSS = "BOSS"
    CREATURE = "CREATURE"
    VEHICLE_HYBRID = "VEHICLE_HYBRID"
    DECORATIVE = "DECORATIVE"


class SpeciesType49(str, Enum):
    HUMAN = "HUMAN"
    HUMANOID = "HUMANOID"
    ROBOT = "ROBOT"
    ANDROID = "ANDROID"
    ALIEN = "ALIEN"
    CREATURE = "CREATURE"
    CUSTOM = "CUSTOM"


class BodyRepresentation49(str, Enum):
    MODULAR_MESH = "MODULAR_MESH"
    PARAMETRIC_MESH = "PARAMETRIC_MESH"
    SCULPTED_BASE = "SCULPTED_BASE"
    PROCEDURAL_MESH = "PROCEDURAL_MESH"
    HYBRID = "HYBRID"


@dataclass
class BodyDimensions49:
    height_cm: float = 180.0
    shoulder_width_cm: float = 46.0
    chest_width_cm: float = 38.0
    waist_width_cm: float = 32.0
    pelvis_width_cm: float = 36.0
    arm_length_cm: float = 76.0
    leg_length_cm: float = 96.0

    @property
    def is_valid(self) -> bool:
        return (
            50.0 <= self.height_cm <= 500.0 and
            self.shoulder_width_cm > 0.0 and
            self.chest_width_cm > 0.0 and
            self.waist_width_cm > 0.0 and
            self.pelvis_width_cm > 0.0 and
            self.arm_length_cm > 0.0 and
            self.leg_length_cm > 0.0
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "height_cm": self.height_cm,
            "shoulder_width_cm": self.shoulder_width_cm,
            "chest_width_cm": self.chest_width_cm,
            "waist_width_cm": self.waist_width_cm,
            "pelvis_width_cm": self.pelvis_width_cm,
            "arm_length_cm": self.arm_length_cm,
            "leg_length_cm": self.leg_length_cm,
        }


@dataclass
class CharacterCreatureSpecification:
    character_id: str
    character_type: CharacterType49
    species: SpeciesType49
    body_repr: BodyRepresentation49 = BodyRepresentation49.HYBRID
    dimensions: BodyDimensions49 = field(default_factory=BodyDimensions49)
    bone_count: int = 68
    has_clothing: bool = True
    has_armor: bool = True
    has_hair: bool = True
    has_facial_rig: bool = True
    has_ragdoll: bool = True
    seed: int = 42

    @property
    def is_valid_production(self) -> bool:
        return (
            self.dimensions.is_valid and
            self.bone_count >= 20 and
            self.has_ragdoll
        )

    @property
    def definition_hash(self) -> str:
        return CanonicalHasher.compute_hash(self.to_dict())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "character_id": self.character_id,
            "character_type": self.character_type.value,
            "species": self.species.value,
            "body_repr": self.body_repr.value,
            "dimensions": self.dimensions.to_dict(),
            "bone_count": self.bone_count,
            "has_clothing": self.has_clothing,
            "has_armor": self.has_armor,
            "has_hair": self.has_hair,
            "has_facial_rig": self.has_facial_rig,
            "has_ragdoll": self.has_ragdoll,
            "seed": self.seed,
        }
