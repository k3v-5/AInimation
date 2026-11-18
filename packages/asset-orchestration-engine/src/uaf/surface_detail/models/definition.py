"""
PhysicalMaterialClass, SurfaceLayerType, and SurfaceDetailDefinition models.
UAF-81.22 Sections 3, 4, 11, 12, 13.
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from ...core.hashing.canonical_hasher import CanonicalHasher


class PhysicalMaterialClass(str, Enum):
    METAL = "METAL"
    WOOD = "WOOD"
    STONE = "STONE"
    CONCRETE = "CONCRETE"
    PLASTIC = "PLASTIC"
    RUBBER = "RUBBER"
    GLASS = "GLASS"
    CERAMIC = "CERAMIC"
    FABRIC = "FABRIC"
    LEATHER = "LEATHER"
    SKIN = "SKIN"
    ORGANIC = "ORGANIC"
    LIQUID = "LIQUID"
    ENERGY = "ENERGY"
    CUSTOM = "CUSTOM"


class SurfaceLayerType(str, Enum):
    BASE = "BASE"
    PAINT = "PAINT"
    COATING = "COATING"
    DIRT = "DIRT"
    DUST = "DUST"
    MUD = "MUD"
    RUST = "RUST"
    CORROSION = "CORROSION"
    SCRATCH = "SCRATCH"
    DAMAGE = "DAMAGE"
    BLOOD = "BLOOD"
    OIL = "OIL"
    WATER = "WATER"
    DECAL = "DECAL"
    EMISSIVE = "EMISSIVE"


@dataclass
class SurfaceDetailDefinition:
    surface_id: str
    physical_class: PhysicalMaterialClass = PhysicalMaterialClass.METAL
    shader_model: str = "DEFAULT_LIT"
    base_color_hex: str = "#808080"
    roughness: float = 0.5
    metallic: float = 0.0
    normal_intensity: float = 1.0
    layers: List[SurfaceLayerType] = field(default_factory=lambda: [SurfaceLayerType.BASE])
    resolution: int = 2048
    seed: int = 42

    @property
    def definition_hash(self) -> str:
        return CanonicalHasher.compute_hash(self.to_dict())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "surface_id": self.surface_id,
            "physical_class": self.physical_class.value,
            "shader_model": self.shader_model,
            "base_color_hex": self.base_color_hex,
            "roughness": self.roughness,
            "metallic": self.metallic,
            "normal_intensity": self.normal_intensity,
            "layers": [l.value for l in self.layers],
            "resolution": self.resolution,
            "seed": self.seed,
        }
