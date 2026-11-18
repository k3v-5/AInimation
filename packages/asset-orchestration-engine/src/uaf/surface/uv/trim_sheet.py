"""
TrimSheetDefinition and TrimRegion models for modular reusable surface trims.
UAF-81.7 Section 23.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional


@dataclass
class TrimRegion:
    region_id: str
    u_min: float
    v_min: float
    u_max: float
    v_max: float
    material_family: str = "PAINTED_METAL"
    label: str = "BorderTrim"

    @property
    def width(self) -> float:
        return self.u_max - self.u_min

    @property
    def height(self) -> float:
        return self.v_max - self.v_min

    def to_dict(self) -> Dict[str, Any]:
        return {
            "region_id": self.region_id,
            "u_min": self.u_min,
            "v_min": self.v_min,
            "u_max": self.u_max,
            "v_max": self.v_max,
            "material_family": self.material_family,
            "label": self.label,
        }


@dataclass
class TrimSheetDefinition:
    sheet_id: str
    resolution: int = 2048
    trim_regions: List[TrimRegion] = field(default_factory=list)

    def get_region(self, region_id: str) -> Optional[TrimRegion]:
        for r in self.trim_regions:
            if r.region_id == region_id:
                return r
        return None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "sheet_id": self.sheet_id,
            "resolution": self.resolution,
            "trim_regions": [r.to_dict() for r in self.trim_regions],
        }
