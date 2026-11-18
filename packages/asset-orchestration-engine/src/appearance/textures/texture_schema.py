from enum import Enum
from dataclasses import dataclass, field
from typing import Tuple, Optional, Dict, Any

class TextureUsage(str, Enum):
    BASE_COLOR = "BASE_COLOR"
    ROUGHNESS = "ROUGHNESS"
    METALLIC = "METALLIC"
    NORMAL = "NORMAL"
    AO = "AO"
    EMISSION = "EMISSION"
    MASK = "MASK"
    OPACITY = "OPACITY"

class ColorSpace(str, Enum):
    SRGB = "sRGB"
    NON_COLOR = "Non-Color"

@dataclass
class TextureMetadata:
    texture_id: str
    source_path: str
    usage: TextureUsage
    color_space: ColorSpace
    resolution: Tuple[int, int] = (1024, 1024)
    format: str = "PNG"
    version: int = 1
    tiling: Tuple[float, float] = (1.0, 1.0)
    offset: Tuple[float, float] = (0.0, 0.0)
