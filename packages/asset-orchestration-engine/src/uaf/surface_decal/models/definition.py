"""
MaterialFamily34, WearType34, DamageType34, SurfaceDecalItem, and SurfaceAuthoringSpecification models.
UAF-81.34 Sections 4, 5, 6, 7, 23, 24, 28, 29, 127.
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from ...core.hashing.canonical_hasher import CanonicalHasher


class MaterialFamily34(str, Enum):
    SKIN = "SKIN"
    FLESH = "FLESH"
    BONE = "BONE"
    METAL = "METAL"
    PAINTED_METAL = "PAINTED_METAL"
    RUBBER = "RUBBER"
    PLASTIC = "PLASTIC"
    CERAMIC = "CERAMIC"
    GLASS = "GLASS"
    CONCRETE = "CONCRETE"
    STONE = "STONE"
    BRICK = "BRICK"
    WOOD = "WOOD"
    FABRIC = "FABRIC"
    LEATHER = "LEATHER"
    PAPER = "PAPER"
    LIQUID = "LIQUID"
    SLIME = "SLIME"
    ORGANIC = "ORGANIC"
    ENERGY = "ENERGY"
    HOLOGRAM = "HOLOGRAM"
    EMISSIVE = "EMISSIVE"
    CUSTOM = "CUSTOM"


class WearType34(str, Enum):
    EDGE_WEAR = "EDGE_WEAR"
    SURFACE_WEAR = "SURFACE_WEAR"
    FREQUENCY_WEAR = "FREQUENCY_WEAR"
    CONTACT_WEAR = "CONTACT_WEAR"
    MECHANICAL_WEAR = "MECHANICAL_WEAR"
    ENVIRONMENTAL_WEAR = "ENVIRONMENTAL_WEAR"


class DamageType34(str, Enum):
    SCRATCH = "SCRATCH"
    DENT = "DENT"
    CRACK = "CRACK"
    CHIP = "CHIP"
    BULLET_IMPACT = "BULLET_IMPACT"
    BURN = "BURN"
    CUT = "CUT"


@dataclass
class SurfaceDecalItem:
    decal_id: str
    decal_type: str = "GENERIC_DECAL"
    size_cm: List[float] = field(default_factory=lambda: [50.0, 50.0])
    opacity: float = 1.0  # 0.0 to 1.0

    @property
    def is_valid(self) -> bool:
        return (
            len(self.size_cm) == 2 and
            all(s > 0.0 for s in self.size_cm) and
            0.0 <= self.opacity <= 1.0
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "decal_id": self.decal_id,
            "decal_type": self.decal_type,
            "size_cm": self.size_cm,
            "opacity": self.opacity,
        }


@dataclass
class SurfaceAuthoringSpecification:
    surface_id: str
    material_family: MaterialFamily34
    roughness_base: float = 0.5
    metallic_base: float = 0.0
    wear_types: List[WearType34] = field(default_factory=list)
    damage_types: List[DamageType34] = field(default_factory=list)
    decals: List[SurfaceDecalItem] = field(default_factory=list)
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
            "material_family": self.material_family.value,
            "roughness_base": self.roughness_base,
            "metallic_base": self.metallic_base,
            "wear_types": [w.value for w in self.wear_types],
            "damage_types": [d.value for d in self.damage_types],
            "decals": [dc.to_dict() for dc in self.decals],
            "seed": self.seed,
        }
