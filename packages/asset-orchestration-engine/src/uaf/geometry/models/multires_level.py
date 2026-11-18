"""
Multi-resolution complexity levels and detail representation policies.
UAF-81.3 Sections 3, 5, 6, 7, 8, 9, 10.
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, Any, List


class MultiResLevel(str, Enum):
    L0_STRUCTURAL = "L0"  # Hierarchy, placement, scale, relationships
    L1_PRIMARY = "L1"     # Silhouette, major masses
    L2_SECONDARY = "L2"   # Muscles, panels, armor plates, frames
    L3_TERTIARY = "L3"    # Seams, bolts, vents, wrinkles, folds
    L4_MICRO = "L4"       # Scratches, pores, micro variation


class DetailRepresentation(str, Enum):
    GEOMETRY = "GEOMETRY"
    DISPLACEMENT = "DISPLACEMENT"
    NORMAL = "NORMAL"
    HEIGHT = "HEIGHT"
    MATERIAL = "MATERIAL"
    SHADER = "SHADER"


@dataclass(frozen=True)
class DetailPolicy:
    feature_name: str
    target_level: MultiResLevel
    representation: DetailRepresentation
    rationale: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "feature_name": self.feature_name,
            "target_level": self.target_level.value,
            "representation": self.representation.value,
            "rationale": self.rationale,
        }
