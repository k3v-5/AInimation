"""
MaterialCategory43, UVStrategy43, TexelDensityProfile43, PBRProperties43, PBRSurfaceSpecification models.
UAF-81.43 Sections 6, 11, 15, 24, 149.
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Tuple
from ...core.hashing.canonical_hasher import CanonicalHasher


class MaterialCategory43(str, Enum):
    ORGANIC = "ORGANIC"
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
    CONCRETE = "CONCRETE"
    WOOD = "WOOD"
    VEGETATION = "VEGETATION"
    LIQUID = "LIQUID"
    ENERGY = "ENERGY"
    EMISSIVE = "EMISSIVE"
    HOLOGRAPHIC = "HOLOGRAPHIC"
    TECHNICAL = "TECHNICAL"
    MULTI_LAYER = "MULTI_LAYER"
    CUSTOM = "CUSTOM"


class UVStrategy43(str, Enum):
    SMART_PROJECT = "SMART_PROJECT"
    ANGLE_BASED = "ANGLE_BASED"
    CONFORMAL = "CONFORMAL"
    CUBIC = "CUBIC"
    CYLINDRICAL = "CYLINDRICAL"
    SPHERICAL = "SPHERICAL"
    PLANAR = "PLANAR"
    TRIM_SHEET = "TRIM_SHEET"
    UDIM = "UDIM"
    CUSTOM = "CUSTOM"


class TexelDensityProfile43(str, Enum):
    HERO = "HERO"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    BACKGROUND = "BACKGROUND"


def _is_power_of_two(n: int) -> bool:
    return n > 0 and (n & (n - 1)) == 0


@dataclass
class PBRProperties43:
    base_color_rgb: Tuple[float, float, float] = (0.8, 0.8, 0.8)
    metallic: float = 0.0
    roughness: float = 0.5
    emissive_intensity: float = 0.0
    resolution: int = 2048

    @property
    def is_valid(self) -> bool:
        return (
            0.0 <= self.metallic <= 1.0 and
            0.0 <= self.roughness <= 1.0 and
            self.emissive_intensity >= 0.0 and
            _is_power_of_two(self.resolution) and
            self.resolution >= 256 and
            all(0.0 <= c <= 1.0 for c in self.base_color_rgb)
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "base_color_rgb": list(self.base_color_rgb),
            "metallic": self.metallic,
            "roughness": self.roughness,
            "emissive_intensity": self.emissive_intensity,
            "resolution": self.resolution,
        }


@dataclass
class PBRSurfaceSpecification:
    material_id: str
    category: MaterialCategory43
    uv_strategy: UVStrategy43 = UVStrategy43.SMART_PROJECT
    texel_density: TexelDensityProfile43 = TexelDensityProfile43.HIGH
    pbr: PBRProperties43 = field(default_factory=PBRProperties43)
    has_normal_map: bool = True
    has_ao_map: bool = True
    has_material_instance: bool = True
    seed: int = 42

    @property
    def is_valid_surface(self) -> bool:
        return (
            self.pbr.is_valid and
            self.has_normal_map and
            self.has_ao_map and
            self.has_material_instance
        )

    @property
    def definition_hash(self) -> str:
        return CanonicalHasher.compute_hash(self.to_dict())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "material_id": self.material_id,
            "category": self.category.value,
            "uv_strategy": self.uv_strategy.value,
            "texel_density": self.texel_density.value,
            "pbr": self.pbr.to_dict(),
            "has_normal_map": self.has_normal_map,
            "has_ao_map": self.has_ao_map,
            "has_material_instance": self.has_material_instance,
            "seed": self.seed,
        }
