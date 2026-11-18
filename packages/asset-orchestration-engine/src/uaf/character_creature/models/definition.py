"""
CharacterSpecies, AnatomicalLandmarks, and CharacterDefinition21 models.
UAF-81.21 Sections 3, 4, 8, 9, 10, 11, 12.
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from ...core.hashing.canonical_hasher import CanonicalHasher


class CharacterSpecies(str, Enum):
    HUMAN = "HUMAN"
    ROBOT = "ROBOT"
    ALIEN = "ALIEN"
    CREATURE = "CREATURE"
    HYBRID = "HYBRID"
    CUSTOM = "CUSTOM"


@dataclass
class AnatomicalLandmarks:
    pelvis_height: float = 100.0  # cm
    shoulder_width: float = 45.0  # cm
    chest_depth: float = 28.0     # cm
    arm_length: float = 75.0      # cm
    leg_length: float = 95.0      # cm
    head_height: float = 24.0     # cm

    def to_dict(self) -> Dict[str, Any]:
        return {
            "pelvis_height": self.pelvis_height,
            "shoulder_width": self.shoulder_width,
            "chest_depth": self.chest_depth,
            "arm_length": self.arm_length,
            "leg_length": self.leg_length,
            "head_height": self.head_height,
        }


@dataclass
class CharacterDefinition21:
    character_id: str
    species: CharacterSpecies = CharacterSpecies.HUMAN
    height_cm: float = 180.0
    mass_kg: float = 75.0
    generation_strategy: str = "HYBRID"  # "HYBRID", "PARAMETRIC", "MODULAR"
    landmarks: AnatomicalLandmarks = field(default_factory=AnatomicalLandmarks)
    seed: int = 42

    @property
    def definition_hash(self) -> str:
        return CanonicalHasher.compute_hash(self.to_dict())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "character_id": self.character_id,
            "species": self.species.value,
            "height_cm": self.height_cm,
            "mass_kg": self.mass_kg,
            "generation_strategy": self.generation_strategy,
            "landmarks": self.landmarks.to_dict(),
            "seed": self.seed,
        }
