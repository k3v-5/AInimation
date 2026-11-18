"""
PBR Channels, Extended Channels, Color Spaces, Shader Models, and Channel Packing contracts.
UAF-81.4 Sections 14, 15, 17, 18, 19, 20.
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional


class PBRChannel(str, Enum):
    BASE_COLOR = "BASE_COLOR"
    METALLIC = "METALLIC"
    ROUGHNESS = "ROUGHNESS"
    NORMAL = "NORMAL"
    AMBIENT_OCCLUSION = "AMBIENT_OCCLUSION"
    SPECULAR = "SPECULAR"
    HEIGHT = "HEIGHT"
    DISPLACEMENT = "DISPLACEMENT"
    EMISSIVE = "EMISSIVE"
    OPACITY = "OPACITY"
    SUBSURFACE = "SUBSURFACE"
    CLEAR_COAT = "CLEAR_COAT"
    CLEAR_COAT_ROUGHNESS = "CLEAR_COAT_ROUGHNESS"
    ANISOTROPY = "ANISOTROPY"


class ColorSpace(str, Enum):
    SRGB = "sRGB"
    LINEAR = "Linear"
    NORMAL_MAP = "NormalMap"
    HDR = "HDR"


class ShaderModel(str, Enum):
    DEFAULT_LIT = "DEFAULT_LIT"
    SUBSURFACE = "SUBSURFACE"
    CLEAR_COAT = "CLEAR_COAT"
    HAIR = "HAIR"
    EYE = "EYE"
    UNLIT = "UNLIT"


@dataclass(frozen=True)
class ChannelPacking:
    """
    Channel packing policy combining grayscale maps into a single RGBA texture (e.g. ORM).
    UAF-81.4 Section 17.
    """
    packed_texture_id: str
    r_channel: str = "AMBIENT_OCCLUSION"
    g_channel: str = "ROUGHNESS"
    b_channel: str = "METALLIC"
    a_channel: Optional[str] = None
    color_space: ColorSpace = ColorSpace.LINEAR

    def to_dict(self) -> Dict[str, Any]:
        return {
            "packed_texture_id": self.packed_texture_id,
            "r_channel": self.r_channel,
            "g_channel": self.g_channel,
            "b_channel": self.b_channel,
            "a_channel": self.a_channel,
            "color_space": self.color_space.value,
        }


class PhysicalClass(str, Enum):
    """
    Physical response classification for surfaces.
    UAF-81.7 Section 6.
    """
    METALLIC = "METALLIC"
    NON_METALLIC = "NON_METALLIC"
    SEMI_TRANSPARENT = "SEMI_TRANSPARENT"
    TRANSPARENT = "TRANSPARENT"
    SUBSURFACE = "SUBSURFACE"
    EMISSIVE = "EMISSIVE"
    TWO_SIDED = "TWO_SIDED"
    MASKED = "MASKED"

