"""
ParametricAnatomy and ProportionProfile models.
UAF-81.10 Sections 15, 16, 17.
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, Any


class ProportionProfileType(str, Enum):
    REALISTIC = "REALISTIC"
    HEROIC = "HEROIC"
    ATHLETIC = "ATHLETIC"
    SLENDER = "SLENDER"
    HEAVY = "HEAVY"
    STYLIZED = "STYLIZED"
    MONSTROUS = "MONSTROUS"
    CUSTOM = "CUSTOM"


@dataclass
class ParametricAnatomy:
    height_cm: float = 180.0
    shoulder_width_cm: float = 48.0
    chest_depth_cm: float = 28.0
    waist_width_cm: float = 34.0
    hip_width_cm: float = 38.0
    arm_length_cm: float = 75.0
    leg_length_cm: float = 90.0
    head_size_cm: float = 24.0
    hand_size_cm: float = 19.0
    foot_size_cm: float = 27.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "height_cm": self.height_cm,
            "shoulder_width_cm": self.shoulder_width_cm,
            "chest_depth_cm": self.chest_depth_cm,
            "waist_width_cm": self.waist_width_cm,
            "hip_width_cm": self.hip_width_cm,
            "arm_length_cm": self.arm_length_cm,
            "leg_length_cm": self.leg_length_cm,
            "head_size_cm": self.head_size_cm,
            "hand_size_cm": self.hand_size_cm,
            "foot_size_cm": self.foot_size_cm,
        }


@dataclass
class ProportionProfile:
    profile_id: str
    profile_type: ProportionProfileType = ProportionProfileType.HEROIC
    anatomy: ParametricAnatomy = field(default_factory=ParametricAnatomy)

    @classmethod
    def create_heroic_profile(cls, profile_id: str = "Prop_Heroic_Male") -> "ProportionProfile":
        # Broader shoulders, narrower waist, longer limbs
        anatomy = ParametricAnatomy(
            height_cm=188.0,
            shoulder_width_cm=54.0,
            chest_depth_cm=32.0,
            waist_width_cm=32.0,
            hip_width_cm=36.0,
            arm_length_cm=78.0,
            leg_length_cm=95.0,
        )
        return cls(profile_id=profile_id, profile_type=ProportionProfileType.HEROIC, anatomy=anatomy)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "profile_id": self.profile_id,
            "profile_type": self.profile_type.value,
            "anatomy": self.anatomy.to_dict(),
        }
