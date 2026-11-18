"""
LandmarkSystem defines coordinate-independent anatomical landmarks.
UAF-81.3 Sections 25, 26.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any


STANDARD_LANDMARKS = [
    "pelvis", "spine", "chest", "neck", "head",
    "shoulder_L", "shoulder_R", "elbow_L", "elbow_R", "wrist_L", "wrist_R",
    "hip_L", "hip_R", "knee_L", "knee_R", "ankle_L", "ankle_R"
]


@dataclass
class LandmarkSystem:
    landmarks: Dict[str, List[float]] = field(default_factory=dict)

    def set_landmark(self, name: str, position: List[float]) -> None:
        self.landmarks[name] = position

    def get_landmark(self, name: str) -> Optional[List[float]]:
        return self.landmarks.get(name)

    def to_dict(self) -> Dict[str, Any]:
        return {"landmarks": self.landmarks}

    @classmethod
    def create_default_humanoid(cls, height_meters: float = 1.80) -> "LandmarkSystem":
        """Calculates standard proportional landmarks for bipedal humanoid."""
        h = height_meters
        system = cls()
        system.set_landmark("pelvis", [0.0, 0.0, h * 0.53])
        system.set_landmark("spine", [0.0, 0.0, h * 0.65])
        system.set_landmark("chest", [0.0, 0.0, h * 0.75])
        system.set_landmark("neck", [0.0, 0.0, h * 0.85])
        system.set_landmark("head", [0.0, 0.0, h * 0.93])

        # Arms
        shoulder_offset = h * 0.12
        system.set_landmark("shoulder_L", [-shoulder_offset, 0.0, h * 0.82])
        system.set_landmark("shoulder_R", [shoulder_offset, 0.0, h * 0.82])
        system.set_landmark("elbow_L", [-shoulder_offset * 1.6, 0.0, h * 0.62])
        system.set_landmark("elbow_R", [shoulder_offset * 1.6, 0.0, h * 0.62])
        system.set_landmark("wrist_L", [-shoulder_offset * 2.0, 0.0, h * 0.45])
        system.set_landmark("wrist_R", [shoulder_offset * 2.0, 0.0, h * 0.45])

        # Legs
        hip_offset = h * 0.06
        system.set_landmark("hip_L", [-hip_offset, 0.0, h * 0.50])
        system.set_landmark("hip_R", [hip_offset, 0.0, h * 0.50])
        system.set_landmark("knee_L", [-hip_offset, 0.0, h * 0.28])
        system.set_landmark("knee_R", [hip_offset, 0.0, h * 0.28])
        system.set_landmark("ankle_L", [-hip_offset, 0.0, h * 0.05])
        system.set_landmark("ankle_R", [hip_offset, 0.0, h * 0.05])

        return system
