"""
MaterialType38, ColorSpace38, NormalProfile38, PBRSurfaceProperties38, SurfaceLookdevSpecification models.
UAF-81.38 Sections 3, 4, 5, 7, 9, 11, 12, 147.
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from ...core.hashing.canonical_hasher import CanonicalHasher


class MaterialType38(str, Enum):
    PBR_OPAQUE = "PBR_OPAQUE"
    PBR_MASKED = "PBR_MASKED"
    PBR_TRANSLUCENT = "PBR_TRANSLUCENT"
    PBR_SUBSURFACE = "PBR_SUBSURFACE"
    PBR_TWOSIDED = "PBR_TWOSIDED"
    EMISSIVE = "EMISSIVE"
    GLASS = "GLASS"
    METAL = "METAL"
    SKIN = "SKIN"
    HAIR = "HAIR"
    FABRIC = "FABRIC"
    LEATHER = "LEATHER"
    RUBBER = "RUBBER"
    STONE = "STONE"
    WOOD = "WOOD"
    CONCRETE = "CONCRETE"
    CERAMIC = "CERAMIC"
    PLASTIC = "PLASTIC"
    LIQUID = "LIQUID"
    ENERGY = "ENERGY"
    CUSTOM = "CUSTOM"


class ColorSpace38(str, Enum):
    SRGB = "SRGB"
    LINEAR = "LINEAR"
    DATA = "DATA"
    NORMAL = "NORMAL"
    MASK = "MASK"


class NormalProfile38(str, Enum):
    DIRECTX = "DIRECTX"  # Unreal Engine default (inverted green / -Y)
    OPENGL = "OPENGL"    # Maya / Blender default (+Y)


@dataclass
class PBRSurfaceProperties38:
    roughness: float = 0.5
    metallic: float = 0.0
    specular: float = 0.5
    emissive_intensity: float = 0.0

    @property
    def is_valid(self) -> bool:
        return (
            0.0 <= self.roughness <= 1.0 and
            0.0 <= self.metallic <= 1.0 and
            0.0 <= self.specular <= 1.0 and
            self.emissive_intensity >= 0.0
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "roughness": self.roughness,
            "metallic": self.metallic,
            "specular": self.specular,
            "emissive_intensity": self.emissive_intensity,
        }


@dataclass
class SurfaceLookdevSpecification:
    surface_id: str
    material_type: MaterialType38
    properties: PBRSurfaceProperties38 = field(default_factory=PBRSurfaceProperties38)
    normal_profile: NormalProfile38 = NormalProfile38.DIRECTX
    color_space: ColorSpace38 = ColorSpace38.SRGB
    resolution_width: int = 2048
    resolution_height: int = 2048
    seed: int = 42

    @property
    def is_valid_resolution(self) -> bool:
        # POT resolution check >= 256
        return (
            self.resolution_width >= 256 and
            self.resolution_height >= 256 and
            (self.resolution_width & (self.resolution_width - 1)) == 0 and
            (self.resolution_height & (self.resolution_height - 1)) == 0
        )

    @property
    def definition_hash(self) -> str:
        return CanonicalHasher.compute_hash(self.to_dict())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "surface_id": self.surface_id,
            "material_type": self.material_type.value,
            "properties": self.properties.to_dict(),
            "normal_profile": self.normal_profile.value,
            "color_space": self.color_space.value,
            "resolution_width": self.resolution_width,
            "resolution_height": self.resolution_height,
            "seed": self.seed,
        }
