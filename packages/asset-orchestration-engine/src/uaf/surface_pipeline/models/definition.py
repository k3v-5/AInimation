"""
SurfaceClass27, UVStrategyType, ColorSpace27, TextureMapDefinition, and SurfaceDefinition27 models.
UAF-81.27 Sections 3, 4, 15, 16, 17, 19, 22, 130.
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
import math
from ...core.hashing.canonical_hasher import CanonicalHasher


class SurfaceClass27(str, Enum):
    SKIN = "SKIN"
    FABRIC = "FABRIC"
    LEATHER = "LEATHER"
    METAL = "METAL"
    PAINTED_METAL = "PAINTED_METAL"
    PLASTIC = "PLASTIC"
    RUBBER = "RUBBER"
    GLASS = "GLASS"
    CERAMIC = "CERAMIC"
    STONE = "STONE"
    WOOD = "WOOD"
    CONCRETE = "CONCRETE"
    ORGANIC = "ORGANIC"
    VEGETATION = "VEGETATION"
    ENERGY = "ENERGY"
    EMISSIVE = "EMISSIVE"
    CUSTOM = "CUSTOM"


class UVStrategyType(str, Enum):
    AUTO = "AUTO"
    PLANAR = "PLANAR"
    CYLINDRICAL = "CYLINDRICAL"
    BOX = "BOX"
    SEAM_BASED = "SEAM_BASED"
    ISLAND_BASED = "ISLAND_BASED"
    ATLAS = "ATLAS"
    TRIM = "TRIM"
    UDIM = "UDIM"


class ColorSpace27(str, Enum):
    SRGB = "SRGB"
    LINEAR = "LINEAR"
    NORMAL_MAP = "NORMAL_MAP"
    MASK = "MASK"


@dataclass
class TextureMapDefinition:
    texture_id: str
    channel: str  # BASE_COLOR, NORMAL, ORM, EMISSIVE, MASK
    resolution: int  # 256, 512, 1024, 2048, 4096
    color_space: ColorSpace27

    @property
    def is_power_of_two(self) -> bool:
        return self.resolution >= 256 and (self.resolution & (self.resolution - 1)) == 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "texture_id": self.texture_id,
            "channel": self.channel,
            "resolution": self.resolution,
            "color_space": self.color_space.value,
        }


@dataclass
class SurfaceDefinition27:
    surface_id: str
    asset_id: str
    surface_class: SurfaceClass27
    uv_strategy: UVStrategyType = UVStrategyType.SEAM_BASED
    texel_density: float = 10.24  # px/cm
    textures: List[TextureMapDefinition] = field(default_factory=list)
    seed: int = 42

    @property
    def definition_hash(self) -> str:
        return CanonicalHasher.compute_hash(self.to_dict())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "surface_id": self.surface_id,
            "asset_id": self.asset_id,
            "surface_class": self.surface_class.value,
            "uv_strategy": self.uv_strategy.value,
            "texel_density": self.texel_density,
            "textures": [t.to_dict() for t in self.textures],
            "seed": self.seed,
        }
