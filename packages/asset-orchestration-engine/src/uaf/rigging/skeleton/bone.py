"""
BoneDefinition and BoneRole semantic taxonomy.
UAF-81.5 Sections 5, 6, 7.
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional


class BoneRole(str, Enum):
    # Core Humanoid
    ROOT = "ROOT"
    PELVIS = "PELVIS"
    SPINE = "SPINE"
    SPINE_01 = "SPINE_01"
    SPINE_02 = "SPINE_02"
    CHEST = "CHEST"
    NECK = "NECK"
    HEAD = "HEAD"
    CLAVICLE_L = "CLAVICLE_L"
    CLAVICLE_R = "CLAVICLE_R"
    UPPER_ARM_L = "UPPER_ARM_L"
    UPPER_ARM_R = "UPPER_ARM_R"
    LOWER_ARM_L = "LOWER_ARM_L"
    LOWER_ARM_R = "LOWER_ARM_R"
    HAND_L = "HAND_L"
    HAND_R = "HAND_R"
    THIGH_L = "THIGH_L"
    THIGH_R = "THIGH_R"
    CALF_L = "CALF_L"
    CALF_R = "CALF_R"
    FOOT_L = "FOOT_L"
    FOOT_R = "FOOT_R"
    TOE_L = "TOE_L"
    TOE_R = "TOE_R"

    # Optional / Creature / Secondary
    TWIST_ARM_L = "TWIST_ARM_L"
    TWIST_ARM_R = "TWIST_ARM_R"
    TWIST_LEG_L = "TWIST_LEG_L"
    TWIST_LEG_R = "TWIST_LEG_R"
    FINGER = "FINGER"
    FACIAL = "FACIAL"
    JAW = "JAW"
    EYE_L = "EYE_L"
    EYE_R = "EYE_R"
    TAIL = "TAIL"
    WING = "WING"
    ARMOR = "ARMOR"
    WEAPON = "WEAPON"
    AUXILIARY = "AUXILIARY"


@dataclass
class BoneDefinition:
    bone_id: str
    name: str
    role: BoneRole
    position: List[float] = field(default_factory=lambda: [0.0, 0.0, 0.0])  # Local / Bind position in meters
    rotation: List[float] = field(default_factory=lambda: [0.0, 0.0, 0.0])  # Euler angles
    parent_id: Optional[str] = None
    length: float = 0.1
    deformation_enabled: bool = True
    constraints: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "bone_id": self.bone_id,
            "name": self.name,
            "role": self.role.value,
            "position": self.position,
            "rotation": self.rotation,
            "parent_id": self.parent_id,
            "length": self.length,
            "deformation_enabled": self.deformation_enabled,
            "constraints": self.constraints,
        }
