"""
TexelDensityProfile models physical texture scale consistency across components.
UAF-81.7 Sections 16, 17.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Tuple


@dataclass
class TexelDensityProfile:
    target_px_per_meter: float = 512.0
    min_px_per_meter: float = 256.0
    max_px_per_meter: float = 1024.0
    tolerance_percent: float = 20.0

    def validate_density(self, measured_density: float) -> Tuple[bool, str]:
        if measured_density < self.min_px_per_meter:
            return (False, f"Under-density: {measured_density:.1f} px/m is below minimum {self.min_px_per_meter:.1f} px/m.")
        if measured_density > self.max_px_per_meter:
            return (False, f"Over-density: {measured_density:.1f} px/m exceeds maximum {self.max_px_per_meter:.1f} px/m.")
        return (True, f"Texel density {measured_density:.1f} px/m is within acceptable range.")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "target_px_per_meter": self.target_px_per_meter,
            "min_px_per_meter": self.min_px_per_meter,
            "max_px_per_meter": self.max_px_per_meter,
            "tolerance_percent": self.tolerance_percent,
        }
