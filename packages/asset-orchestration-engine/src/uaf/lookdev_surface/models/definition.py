"""
MaterialFamily46, LookdevQualityTier46, SurfacePBRProperties46, LookdevSurfaceSpecification models.
UAF-81.46 Sections 4, 5, 6, 8, 114.
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Tuple
from ...core.hashing.canonical_hasher import CanonicalHasher


class MaterialFamily46(str, Enum):
    SKIN = "SKIN"
    FABRIC = "FABRIC"
    LEATHER = "LEATHER"
    METAL = "METAL"
    PAINTED_METAL = "PAINTED_METAL"
    RUBBER = "RUBBER"
    PLASTIC = "PLASTIC"
    GLASS = "GLASS"
    CERAMIC = "CERAMIC"
    CONCRETE = "CONCRETE"
    STONE = "STONE"
    WOOD = "WOOD"
    SOIL = "SOIL"
    SAND = "SAND"
    GRAVEL = "GRAVEL"
    WATER = "WATER"
    ICE = "ICE"
    EMISSIVE = "EMISSIVE"
    HOLOGRAM = "HOLOGRAM"
    ENERGY = "ENERGY"
    ORGANIC = "ORGANIC"
    MECHANICAL = "MECHANICAL"


class LookdevQualityTier46(str, Enum):
    CINEMATIC = "CINEMATIC"
    HERO = "HERO"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


def _is_power_of_two(n: int) -> bool:
    return n > 0 and (n & (n - 1)) == 0


@dataclass
class SurfacePBRProperties46:
    base_color_rgb: Tuple[float, float, float] = (0.8, 0.8, 0.8)
    metallic: float = 0.0
    roughness: float = 0.5
    ao: float = 1.0
    emission: float = 0.0
    resolution: int = 2048

    @property
    def is_valid(self) -> bool:
        return (
            0.0 <= self.metallic <= 1.0 and
            0.0 <= self.roughness <= 1.0 and
            0.0 <= self.ao <= 1.0 and
            self.emission >= 0.0 and
            _is_power_of_two(self.resolution) and
            self.resolution >= 256 and
            all(0.0 <= c <= 1.0 for c in self.base_color_rgb)
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "base_color_rgb": list(self.base_color_rgb),
            "metallic": self.metallic,
            "roughness": self.roughness,
            "ao": self.ao,
            "emission": self.emission,
            "resolution": self.resolution,
        }


@dataclass
class LookdevSurfaceSpecification:
    surface_id: str
    material_family: MaterialFamily46
    quality_tier: LookdevQualityTier46 = LookdevQualityTier46.HIGH
    pbr: SurfacePBRProperties46 = field(default_factory=SurfacePBRProperties46)
    has_normal: bool = True
    has_displacement: bool = True
    has_material_instance: bool = True
    seed: int = 42

    @property
    def is_valid_surface(self) -> bool:
        return (
            self.pbr.is_valid and
            self.has_normal and
            self.has_displacement and
            self.has_material_instance
        )

    @property
    def definition_hash(self) -> str:
        return CanonicalHasher.compute_hash(self.to_dict())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "surface_id": self.surface_id,
            "material_family": self.material_family.value,
            "quality_tier": self.quality_tier.value,
            "pbr": self.pbr.to_dict(),
            "has_normal": self.has_normal,
            "has_displacement": self.has_displacement,
            "has_material_instance": self.has_material_instance,
            "seed": self.seed,
        }
