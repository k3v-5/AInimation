"""
MotionClipType and MotionClip models.
UAF-81.23 Sections 98, 99, 105, 106.
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, Any


class MotionClipType(str, Enum):
    LOOP = "LOOP"
    MONTAGE = "MONTAGE"
    TRANSITION = "TRANSITION"
    ADDITIVE = "ADDITIVE"
    ONE_SHOT = "ONE_SHOT"


@dataclass
class MotionClip:
    clip_id: str
    clip_type: MotionClipType
    duration_seconds: float
    frame_rate: float = 30.0
    is_looping: bool = False
    root_motion_enabled: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "clip_id": self.clip_id,
            "clip_type": self.clip_type.value,
            "duration_seconds": self.duration_seconds,
            "frame_rate": self.frame_rate,
            "is_looping": self.is_looping,
            "root_motion_enabled": self.root_motion_enabled,
        }
