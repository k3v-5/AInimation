"""
RetargetProfile maps internal semantic bones to standard engine targets like UE5 Mannequin.
UAF-81.5 Section 76.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List


UE5_MANNEQUIN_BONE_MAP = {
    "root": "root",
    "pelvis": "pelvis",
    "spine_01": "spine_01",
    "chest": "spine_03",
    "neck": "neck_01",
    "head": "head",
    "clavicle_L": "clavicle_l",
    "upperarm_L": "upperarm_l",
    "lowerarm_L": "lowerarm_l",
    "hand_L": "hand_l",
    "clavicle_R": "clavicle_r",
    "upperarm_R": "upperarm_r",
    "lowerarm_R": "lowerarm_r",
    "hand_R": "hand_r",
    "thigh_L": "thigh_l",
    "calf_L": "calf_l",
    "foot_L": "foot_l",
    "thigh_R": "thigh_r",
    "calf_R": "calf_r",
    "foot_R": "foot_r",
}


@dataclass
class RetargetProfile:
    profile_id: str
    target_engine: str = "UE5"
    target_skeleton_type: str = "UE5_MANNEQUIN"
    bone_mapping: Dict[str, str] = field(default_factory=lambda: dict(UE5_MANNEQUIN_BONE_MAP))

    def map_bone(self, source_bone_id: str) -> str:
        return self.bone_mapping.get(source_bone_id, source_bone_id)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "profile_id": self.profile_id,
            "target_engine": self.target_engine,
            "target_skeleton_type": self.target_skeleton_type,
            "bone_mapping": self.bone_mapping,
        }
