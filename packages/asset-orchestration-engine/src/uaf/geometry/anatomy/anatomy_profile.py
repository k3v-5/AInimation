"""
AnatomyProfile models morphological proportions and physical build parameters.
UAF-81.3 Sections 27, 28.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List


@dataclass(frozen=True)
class AnatomyProfile:
    height_meters: float = 1.80
    shoulder_ratio: float = 0.26  # shoulder width relative to height
    torso_ratio: float = 0.38     # torso length relative to height
    limb_ratio: float = 0.48      # leg length relative to height
    head_ratio: float = 0.13      # head size relative to height
    muscle_profile: str = "athletic"  # lean, athletic, muscular, heavy
    body_mass_kg: float = 80.0

    def validate_proportions(self) -> List[str]:
        warnings = []
        if self.height_meters < 0.5 or self.height_meters > 3.5:
            warnings.append(f"Height {self.height_meters}m is outside standard humanoid humanoid range (0.5m - 3.5m).")
        if self.shoulder_ratio > 0.45:
            warnings.append("Extreme shoulder ratio (> 0.45).")
        return warnings

    def to_dict(self) -> Dict[str, Any]:
        return {
            "height_meters": self.height_meters,
            "shoulder_ratio": self.shoulder_ratio,
            "torso_ratio": self.torso_ratio,
            "limb_ratio": self.limb_ratio,
            "head_ratio": self.head_ratio,
            "muscle_profile": self.muscle_profile,
            "body_mass_kg": self.body_mass_kg,
        }
