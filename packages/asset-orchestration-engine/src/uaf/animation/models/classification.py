"""
CharacterClassification and RigProfile models.
UAF-81.9 Sections 5, 6.
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional


class CharacterClassification(str, Enum):
    HUMANOID = "HUMANOID"
    CREATURE = "CREATURE"
    QUADRUPED = "QUADRUPED"
    INSECTOID = "INSECTOID"
    SERPENTINE = "SERPENTINE"
    AVIAN = "AVIAN"
    ROBOT = "ROBOT"
    MECHANICAL = "MECHANICAL"
    HYBRID = "HYBRID"
    CUSTOM = "CUSTOM"


@dataclass
class RigProfile:
    profile_id: str
    classification: CharacterClassification = CharacterClassification.HUMANOID
    bone_topology: str = "BIPED_CANONICAL"
    max_bones: int = 64
    supports_ik: bool = True
    supports_facial: bool = True
    supports_ragdoll: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "profile_id": self.profile_id,
            "classification": self.classification.value,
            "bone_topology": self.bone_topology,
            "max_bones": self.max_bones,
            "supports_ik": self.supports_ik,
            "supports_facial": self.supports_facial,
            "supports_ragdoll": self.supports_ragdoll,
        }
