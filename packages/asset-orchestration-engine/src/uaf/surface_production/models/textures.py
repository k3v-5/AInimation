"""
TexturePackingType and TextureChannelDefinition models.
UAF-81.18 Sections 21, 22, 23, 24, 26, 27, 28, 29.
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
import math


class TexturePackingType(str, Enum):
    ORM = "ORM"        # R=AO, G=Roughness, B=Metallic
    RGBA = "RGBA"
    SEPARATE = "SEPARATE"


@dataclass
class TextureChannelDefinition:
    texture_id: str
    channel_name: str  # "ALBEDO", "NORMAL", "ORM", "EMISSIVE", "OPACITY"
    color_space: str   # "sRGB", "LINEAR"
    resolution: int = 2048

    @property
    def is_power_of_two(self) -> bool:
        if self.resolution <= 0:
            return False
        return (self.resolution & (self.resolution - 1)) == 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "texture_id": self.texture_id,
            "channel_name": self.channel_name,
            "color_space": self.color_space,
            "resolution": self.resolution,
            "is_power_of_two": self.is_power_of_two,
        }
