"""
CharacterProfile, CharacterClassification, CharacterQualityTier, and CharacterStyle models.
UAF-81.14 Sections 4, 5, 6, 7, 15, 178, 179.
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from ...core.hashing.canonical_hasher import CanonicalHasher


class CharacterClassification(str, Enum):
    HERO = "HERO"
    PLAYER = "PLAYER"
    NPC = "NPC"
    ENEMY = "ENEMY"
    ELITE = "ELITE"
    BOSS = "BOSS"
    CREATURE = "CREATURE"
    PROP_CHARACTER = "PROP_CHARACTER"


class CharacterQualityTier(str, Enum):
    PROXY = "PROXY"
    GAMEPLAY = "GAMEPLAY"
    STANDARD = "STANDARD"
    HIGH = "HIGH"
    HERO = "HERO"
    CINEMATIC = "CINEMATIC"


class CharacterStyle(str, Enum):
    REALISTIC = "REALISTIC"
    SEMI_REALISTIC = "SEMI_REALISTIC"
    STYLIZED = "STYLIZED"
    EXAGGERATED = "EXAGGERATED"
    INDUSTRIAL = "INDUSTRIAL"
    BIO_MECHANICAL = "BIO_MECHANICAL"
    ALIEN = "ALIEN"


@dataclass
class CharacterProfile:
    character_id: str
    classification: CharacterClassification = CharacterClassification.NPC
    quality_tier: CharacterQualityTier = CharacterQualityTier.STANDARD
    style: CharacterStyle = CharacterStyle.REALISTIC
    height_cm: float = 180.0
    body_mass_kg: float = 75.0
    head_scale: float = 1.0
    has_face_rig: bool = True
    has_hands_rig: bool = True
    seed: int = 42

    @property
    def profile_hash(self) -> str:
        return CanonicalHasher.compute_hash(self.to_dict())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "character_id": self.character_id,
            "classification": self.classification.value,
            "quality_tier": self.quality_tier.value,
            "style": self.style.value,
            "height_cm": self.height_cm,
            "body_mass_kg": self.body_mass_kg,
            "head_scale": self.head_scale,
            "has_face_rig": self.has_face_rig,
            "has_hands_rig": self.has_hands_rig,
            "seed": self.seed,
        }
