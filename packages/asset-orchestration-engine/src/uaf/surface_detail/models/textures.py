"""
SurfaceDetailChannel model for textures and packed maps.
UAF-81.22 Sections 148, 151.
"""

from dataclasses import dataclass
from typing import Dict, Any


@dataclass
class SurfaceDetailChannel:
    texture_id: str
    channel_name: str  # "ALBEDO", "NORMAL", "ORM", "EMISSIVE", "MASK"
    color_space: str   # "sRGB" or "LINEAR"
    resolution: int    # e.g. 1024, 2048, 4096
    compression: str = "BC7"

    @property
    def is_power_of_two(self) -> bool:
        return self.resolution > 0 and (self.resolution & (self.resolution - 1)) == 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "texture_id": self.texture_id,
            "channel_name": self.channel_name,
            "color_space": self.color_space,
            "resolution": self.resolution,
            "compression": self.compression,
            "is_power_of_two": self.is_power_of_two,
        }
