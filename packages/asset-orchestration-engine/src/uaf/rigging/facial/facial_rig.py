"""
FacialRigDefinition specifying jaw articulation, gaze tracking, and facial blendshapes.
UAF-81.5 Sections 41, 42, 43, 44, 45.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional


STANDARD_FACIAL_BLENDSHAPES = [
    "jaw_open", "jaw_left", "jaw_right",
    "eye_blink_L", "eye_blink_R",
    "eye_squint_L", "eye_squint_R",
    "brow_up", "brow_down_L", "brow_down_R",
    "mouth_smile_L", "mouth_smile_R",
    "mouth_frown_L", "mouth_frown_R",
    "viseme_aa", "viseme_ee", "viseme_oh", "viseme_ch",
]


@dataclass
class FacialRigDefinition:
    facial_id: str
    jaw_bone_id: str = "jaw"
    eye_bones: List[str] = field(default_factory=lambda: ["eye_L", "eye_R"])
    blendshapes: List[str] = field(default_factory=lambda: list(STANDARD_FACIAL_BLENDSHAPES))
    max_eye_pitch_degrees: float = 30.0
    max_eye_yaw_degrees: float = 35.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "facial_id": self.facial_id,
            "jaw_bone_id": self.jaw_bone_id,
            "eye_bones": self.eye_bones,
            "blendshapes": self.blendshapes,
            "max_eye_pitch_degrees": self.max_eye_pitch_degrees,
            "max_eye_yaw_degrees": self.max_eye_yaw_degrees,
        }
