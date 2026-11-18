"""
CharacterArchetype26, CharacterProportions, LayeredClothingItem, and OrganicCharacterDefinition models.
UAF-81.26 Sections 3, 4, 6, 7, 20, 115.
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from ...core.hashing.canonical_hasher import CanonicalHasher


class CharacterArchetype26(str, Enum):
    HUMAN = "HUMAN"
    SOLDIER = "SOLDIER"
    CIVILIAN = "CIVILIAN"
    SCIENTIST = "SCIENTIST"
    ENGINEER = "ENGINEER"
    ROBOT = "ROBOT"
    ANDROID = "ANDROID"
    CYBORG = "CYBORG"
    ALIEN = "ALIEN"
    CREATURE = "CREATURE"
    MUTANT = "MUTANT"
    BOSS = "BOSS"


@dataclass
class CharacterProportions:
    height_cm: float = 180.0
    head_ratio: float = 1.0 / 7.5
    shoulder_ratio: float = 0.25
    torso_ratio: float = 0.35
    arm_ratio: float = 0.45
    leg_ratio: float = 0.50

    @property
    def is_valid(self) -> bool:
        return (
            50.0 <= self.height_cm <= 400.0 and
            0.0 < self.head_ratio < 0.5 and
            0.0 < self.leg_ratio < 0.8
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "height_cm": self.height_cm,
            "head_ratio": self.head_ratio,
            "shoulder_ratio": self.shoulder_ratio,
            "torso_ratio": self.torso_ratio,
            "arm_ratio": self.arm_ratio,
            "leg_ratio": self.leg_ratio,
        }


@dataclass
class LayeredClothingItem:
    item_id: str
    slot: str  # HEAD, TORSO, LEGS, FEET, HANDS, ARMOR_OUTER
    thickness_mm: float = 2.0
    clearance_mm: float = 1.0  # Must be >= 0.5mm to avoid mesh clipping/penetration

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item_id": self.item_id,
            "slot": self.slot,
            "thickness_mm": self.thickness_mm,
            "clearance_mm": self.clearance_mm,
        }


@dataclass
class OrganicCharacterDefinition:
    character_id: str
    archetype: CharacterArchetype26
    proportions: CharacterProportions = field(default_factory=CharacterProportions)
    clothing_layers: List[LayeredClothingItem] = field(default_factory=list)
    hair_style: str = "DEFAULT"
    has_facial_landmarks: bool = True
    seed: int = 42

    @property
    def definition_hash(self) -> str:
        return CanonicalHasher.compute_hash(self.to_dict())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "character_id": self.character_id,
            "archetype": self.archetype.value,
            "proportions": self.proportions.to_dict(),
            "clothing_layers": [c.to_dict() for c in self.clothing_layers],
            "hair_style": self.hair_style,
            "has_facial_landmarks": self.has_facial_landmarks,
            "seed": self.seed,
        }
