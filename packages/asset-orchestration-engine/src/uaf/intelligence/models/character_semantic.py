"""
CharacterSemanticModel specifies anatomical regions, attachments, and fidelity parameters.
UAF-81.1 Sections 32, 33, 34, 35.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional


ANATOMICAL_REGIONS = [
    "head", "neck", "torso", "pelvis",
    "upper_arm_L", "lower_arm_L", "hand_L",
    "upper_arm_R", "lower_arm_R", "hand_R",
    "upper_leg_L", "lower_leg_L", "foot_L",
    "upper_leg_R", "lower_leg_R", "foot_R"
]


@dataclass
class CharacterSemanticModel:
    height_meters: float = 1.80
    build: str = "athletic"
    species: str = "humanoid"
    anatomical_regions: Dict[str, Any] = field(default_factory=lambda: {r: {} for r in ANATOMICAL_REGIONS})
    facial_fidelity: str = "standard"
    clothing_complexity: str = "standard"
    armor_tier: Optional[str] = None
    accessories: List[str] = field(default_factory=list)
    equipment: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "height_meters": self.height_meters,
            "build": self.build,
            "species": self.species,
            "anatomical_regions": self.anatomical_regions,
            "facial_fidelity": self.facial_fidelity,
            "clothing_complexity": self.clothing_complexity,
            "armor_tier": self.armor_tier,
            "accessories": self.accessories,
            "equipment": self.equipment,
        }
