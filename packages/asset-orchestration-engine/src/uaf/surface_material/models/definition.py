"""
SurfaceType30, MaterialModel30, ColorSpace30, SurfaceMapItem, and ProductionSurfaceDefinition models.
UAF-81.30 Sections 4, 5, 6, 7, 8, 10, 11, 13, 14, 149.
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from ...core.hashing.canonical_hasher import CanonicalHasher


class SurfaceType30(str, Enum):
    ORGANIC = "ORGANIC"
    SKIN = "SKIN"
    FLESH = "FLESH"
    METAL = "METAL"
    PLASTIC = "PLASTIC"
    RUBBER = "RUBBER"
    GLASS = "GLASS"
    CERAMIC = "CERAMIC"
    STONE = "STONE"
    CONCRETE = "CONCRETE"
    WOOD = "WOOD"
    FABRIC = "FABRIC"
    LEATHER = "LEATHER"
    CARBON = "CARBON"
    COMPOSITE = "COMPOSITE"
    ENERGY = "ENERGY"
    HOLOGRAPHIC = "HOLOGRAPHIC"
    LIQUID = "LIQUID"
    ICE = "ICE"
    SNOW = "SNOW"
    SAND = "SAND"
    SOIL = "SOIL"
    VEGETATION = "VEGETATION"
    CUSTOM = "CUSTOM"


class MaterialModel30(str, Enum):
    PBR_METALLIC_ROUGHNESS = "PBR_METALLIC_ROUGHNESS"
    PBR_SPECULAR = "PBR_SPECULAR"
    SUBSURFACE = "SUBSURFACE"
    TRANSLUCENT = "TRANSLUCENT"
    CLEAR_COAT = "CLEAR_COAT"
    EMISSIVE = "EMISSIVE"
    HAIR = "HAIR"
    CLOTH = "CLOTH"
    CUSTOM = "CUSTOM"


class ColorSpace30(str, Enum):
    SRGB = "SRGB"
    LINEAR = "LINEAR"
    NORMAL_MAP = "NORMAL_MAP"
    HDR = "HDR"


@dataclass
class SurfaceMapItem:
    map_id: str
    channel: str  # BASE_COLOR, NORMAL, ORM, EMISSIVE, MASK
    resolution: int  # 256, 512, 1024, 2048, 4096
    color_space: ColorSpace30

    @property
    def is_power_of_two(self) -> bool:
        return self.resolution >= 256 and (self.resolution & (self.resolution - 1)) == 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "map_id": self.map_id,
            "channel": self.channel,
            "resolution": self.resolution,
            "color_space": self.color_space.value,
        }


@dataclass
class ProductionSurfaceDefinition:
    surface_id: str
    surface_type: SurfaceType30
    material_model: MaterialModel30
    maps: List[SurfaceMapItem] = field(default_factory=list)
    roughness_base: float = 0.5
    metallic_base: float = 0.0
    seed: int = 42

    @property
    def is_valid_pbr(self) -> bool:
        return 0.0 <= self.roughness_base <= 1.0 and 0.0 <= self.metallic_base <= 1.0

    @property
    def definition_hash(self) -> str:
        return CanonicalHasher.compute_hash(self.to_dict())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "surface_id": self.surface_id,
            "surface_type": self.surface_type.value,
            "material_model": self.material_model.value,
            "maps": [m.to_dict() for m in self.maps],
            "roughness_base": self.roughness_base,
            "metallic_base": self.metallic_base,
            "seed": self.seed,
        }
