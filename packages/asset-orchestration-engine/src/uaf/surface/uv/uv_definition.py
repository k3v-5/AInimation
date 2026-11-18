"""
UVDefinition, UVChannel, and UVStrategy models.
UAF-81.7 Sections 18, 19, 20, 21, 22.
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional


class UVChannel(str, Enum):
    UV0 = "UV0"  # Base textures
    UV1 = "UV1"  # Lightmaps / Baked AO
    UV2 = "UV2"  # Detail / Trim maps
    UV3 = "UV3"  # Custom / Decals


class UVStrategy(str, Enum):
    SMART_PROJECT = "SMART_PROJECT"
    BOX = "BOX"
    CYLINDRICAL = "CYLINDRICAL"
    PLANAR = "PLANAR"
    CUBIC = "CUBIC"
    SEAM_BASED = "SEAM_BASED"
    ATLAS = "ATLAS"
    TRIM = "TRIM"
    UDIM = "UDIM"
    CUSTOM = "CUSTOM"


class UVOverlapPolicy(str, Enum):
    ALLOWED = "ALLOWED"
    WARNING = "WARNING"
    FORBIDDEN = "FORBIDDEN"


@dataclass
class UVDefinition:
    uv_channel: UVChannel = UVChannel.UV0
    strategy: UVStrategy = UVStrategy.SMART_PROJECT
    resolution: int = 2048
    padding_px: int = 8
    overlap_policy: UVOverlapPolicy = UVOverlapPolicy.FORBIDDEN
    has_overlapping_islands: bool = False
    texel_density_px_m: float = 512.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "uv_channel": self.uv_channel.value,
            "strategy": self.strategy.value,
            "resolution": self.resolution,
            "padding_px": self.padding_px,
            "overlap_policy": self.overlap_policy.value,
            "has_overlapping_islands": self.has_overlapping_islands,
            "texel_density_px_m": self.texel_density_px_m,
        }
