"""
TextureSemanticModel defines texture maps, resolutions, and channels.
UAF-81.1 Section 39.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional


@dataclass
class TextureMapSpecification:
    map_type: str  # albedo, normal, roughness, metallic, ao, height, emission, mask, opacity
    resolution: int = 2048
    format: str = "PNG"
    color_space: str = "sRGB"  # sRGB or Linear
    bit_depth: int = 8

    def to_dict(self) -> Dict[str, Any]:
        return {
            "map_type": self.map_type,
            "resolution": self.resolution,
            "format": self.format,
            "color_space": self.color_space,
            "bit_depth": self.bit_depth,
        }


@dataclass
class TextureSetSemanticModel:
    set_name: str
    target_resolution: int = 2048
    maps: Dict[str, TextureMapSpecification] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "set_name": self.set_name,
            "target_resolution": self.target_resolution,
            "maps": {k: v.to_dict() for k, v in self.maps.items()},
        }
