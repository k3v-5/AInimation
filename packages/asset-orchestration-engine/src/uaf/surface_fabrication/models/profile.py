"""
SurfaceProfile, MaterialClassification, MaterialDomain, and SurfaceWearType models.
UAF-81.15 Sections 4, 5, 6, 7, 33, 34.
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from ...core.hashing.canonical_hasher import CanonicalHasher


class MaterialClassification(str, Enum):
    OPAQUE = "OPAQUE"
    MASKED = "MASKED"
    TRANSLUCENT = "TRANSLUCENT"
    ADDITIVE = "ADDITIVE"
    SUBSURFACE = "SUBSURFACE"
    FOLIAGE = "FOLIAGE"
    HAIR = "HAIR"
    DECAL = "DECAL"
    WATER = "WATER"
    VFX = "VFX"


class MaterialDomain(str, Enum):
    SURFACE = "SURFACE"
    DECAL = "DECAL"
    POST_PROCESS = "POST_PROCESS"
    VOLUME = "VOLUME"


class SurfaceWearType(str, Enum):
    EDGE_WEAR = "EDGE_WEAR"
    SCRATCH = "SCRATCH"
    ABRASION = "ABRASION"
    DUST = "DUST"
    DIRT = "DIRT"
    OIL = "OIL"
    OXIDATION = "OXIDATION"
    FADING = "FADING"


@dataclass
class SurfaceProfile:
    surface_id: str
    surface_type: str  # "SKIN", "METAL", "FABRIC", "CONCRETE", "WOOD", "STONE", "GLASS", "VEGETATION", "TERRAIN", "ENERGY"
    material_classification: MaterialClassification = MaterialClassification.OPAQUE
    domain: MaterialDomain = MaterialDomain.SURFACE
    roughness_range: List[float] = field(default_factory=lambda: [0.2, 0.8])
    metallic_range: List[float] = field(default_factory=lambda: [0.0, 0.0])
    base_color_hex: str = "#808080"
    wears: List[SurfaceWearType] = field(default_factory=list)
    seed: int = 42

    @property
    def profile_hash(self) -> str:
        return CanonicalHasher.compute_hash(self.to_dict())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "surface_id": self.surface_id,
            "surface_type": self.surface_type,
            "material_classification": self.material_classification.value,
            "domain": self.domain.value,
            "roughness_range": self.roughness_range,
            "metallic_range": self.metallic_range,
            "base_color_hex": self.base_color_hex,
            "wears": [w.value for w in self.wears],
            "seed": self.seed,
        }
