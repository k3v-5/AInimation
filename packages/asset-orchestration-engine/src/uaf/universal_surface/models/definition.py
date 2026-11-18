"""
SurfaceType52, PBRChannelType52, TextureResolution52, PBRSurfaceProperties52, UniversalSurfaceSpecification models.
UAF-81.52 Sections 4, 5, 55, 143, 145.
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Tuple
from ...core.hashing.canonical_hasher import CanonicalHasher


class SurfaceType52(str, Enum):
    METAL = "METAL"
    WOOD = "WOOD"
    STONE = "STONE"
    CONCRETE = "CONCRETE"
    BRICK = "BRICK"
    CERAMIC = "CERAMIC"
    GLASS = "GLASS"
    PLASTIC = "PLASTIC"
    RUBBER = "RUBBER"
    FABRIC = "FABRIC"
    LEATHER = "LEATHER"
    PAPER = "PAPER"
    SOIL = "SOIL"
    SAND = "SAND"
    MUD = "MUD"
    GRASS = "GRASS"
    ROCK = "ROCK"
    ICE = "ICE"
    SNOW = "SNOW"
    WATER = "WATER"
    FOLIAGE = "FOLIAGE"
    VEGETATION = "VEGETATION"
    TERRAIN = "TERRAIN"
    SKIN = "SKIN"
    ORGANIC = "ORGANIC"
    EMISSIVE = "EMISSIVE"
    CUSTOM = "CUSTOM"


class PBRChannelType52(str, Enum):
    BASE_COLOR = "BASE_COLOR"
    METALLIC = "METALLIC"
    ROUGHNESS = "ROUGHNESS"
    SPECULAR = "SPECULAR"
    NORMAL = "NORMAL"
    DISPLACEMENT = "DISPLACEMENT"
    AMBIENT_OCCLUSION = "AMBIENT_OCCLUSION"
    EMISSIVE = "EMISSIVE"
    OPACITY = "OPACITY"
    CLEAR_COAT = "CLEAR_COAT"
    SUBSURFACE = "SUBSURFACE"


@dataclass
class TextureResolution52:
    width_px: int = 2048
    height_px: int = 2048

    @property
    def is_power_of_two(self) -> bool:
        def is_pot(n: int) -> bool:
            return n >= 128 and (n & (n - 1) == 0)
        return is_pot(self.width_px) and is_pot(self.height_px)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "width_px": self.width_px,
            "height_px": self.height_px,
        }


@dataclass
class PBRSurfaceProperties52:
    base_color_rgb: Tuple[float, float, float] = (0.5, 0.5, 0.5)
    metallic: float = 0.0
    roughness: float = 0.5
    specular: float = 0.5
    opacity: float = 1.0

    @property
    def is_valid(self) -> bool:
        return (
            all(0.0 <= c <= 1.0 for c in self.base_color_rgb) and
            0.0 <= self.metallic <= 1.0 and
            0.0 <= self.roughness <= 1.0 and
            0.0 <= self.specular <= 1.0 and
            0.0 <= self.opacity <= 1.0
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "base_color_rgb": list(self.base_color_rgb),
            "metallic": self.metallic,
            "roughness": self.roughness,
            "specular": self.specular,
            "opacity": self.opacity,
        }


@dataclass
class UniversalSurfaceSpecification:
    surface_id: str
    surface_type: SurfaceType52
    properties: PBRSurfaceProperties52 = field(default_factory=PBRSurfaceProperties52)
    resolution: TextureResolution52 = field(default_factory=TextureResolution52)
    has_normal: bool = True
    has_roughness: bool = True
    has_metallic: bool = True
    has_ambient_occlusion: bool = True
    has_material_instance: bool = True
    seed: int = 42

    @property
    def is_valid_surface(self) -> bool:
        return (
            self.properties.is_valid and
            self.resolution.is_power_of_two and
            self.has_normal and
            self.has_roughness and
            self.has_metallic and
            self.has_ambient_occlusion and
            self.has_material_instance
        )

    @property
    def definition_hash(self) -> str:
        return CanonicalHasher.compute_hash(self.to_dict())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "surface_id": self.surface_id,
            "surface_type": self.surface_type.value,
            "properties": self.properties.to_dict(),
            "resolution": self.resolution.to_dict(),
            "has_normal": self.has_normal,
            "has_roughness": self.has_roughness,
            "has_metallic": self.has_metallic,
            "has_ambient_occlusion": self.has_ambient_occlusion,
            "has_material_instance": self.has_material_instance,
            "seed": self.seed,
        }
