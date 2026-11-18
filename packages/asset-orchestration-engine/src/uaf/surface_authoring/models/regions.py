"""
MaterialFamilyType, SurfaceRegion, MaterialLayerBlendMode, and MaterialRegionGraph models.
UAF-81.11 Sections 4, 5, 6, 7, 163, 164.
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from ...core.hashing.canonical_hasher import CanonicalHasher


class MaterialFamilyType(str, Enum):
    SKIN = "SKIN"
    METAL = "METAL"
    PAINTED_METAL = "PAINTED_METAL"
    FABRIC = "FABRIC"
    LEATHER = "LEATHER"
    PLASTIC = "PLASTIC"
    GLASS = "GLASS"
    STONE = "STONE"
    CONCRETE = "CONCRETE"
    WOOD = "WOOD"
    ORGANIC = "ORGANIC"
    CERAMIC = "CERAMIC"
    ENERGY = "ENERGY"


class MaterialLayerBlendMode(str, Enum):
    OVERLAY = "OVERLAY"
    MULTIPLY = "MULTIPLY"
    ADD = "ADD"
    MASK_BLEND = "MASK_BLEND"


@dataclass
class SurfaceRegion:
    region_id: str
    material_family: MaterialFamilyType
    roughness_range: List[float] = field(default_factory=lambda: [0.2, 0.8])
    metallic: float = 0.0
    importance: float = 1.0
    uv_channel: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "region_id": self.region_id,
            "material_family": self.material_family.value,
            "roughness_range": self.roughness_range,
            "metallic": self.metallic,
            "importance": self.importance,
            "uv_channel": self.uv_channel,
        }


@dataclass
class MaterialCompositionLayer:
    layer_id: str
    material_family: MaterialFamilyType
    mask_id: str
    blend_mode: MaterialLayerBlendMode = MaterialLayerBlendMode.MASK_BLEND
    opacity: float = 1.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "layer_id": self.layer_id,
            "material_family": self.material_family.value,
            "mask_id": self.mask_id,
            "blend_mode": self.blend_mode.value,
            "opacity": self.opacity,
        }


@dataclass
class MaterialRegionGraph:
    asset_id: str
    regions: Dict[str, SurfaceRegion] = field(default_factory=dict)
    compositions: Dict[str, List[MaterialCompositionLayer]] = field(default_factory=dict)

    def add_region(self, region: SurfaceRegion) -> None:
        self.regions[region.region_id] = region

    def add_composition_layer(self, region_id: str, layer: MaterialCompositionLayer) -> None:
        self.compositions.setdefault(region_id, []).append(layer)

    @property
    def graph_hash(self) -> str:
        return CanonicalHasher.compute_hash(self.to_dict())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "asset_id": self.asset_id,
            "regions": {k: v.to_dict() for k, v in sorted(self.regions.items())},
            "compositions": {
                k: [l.to_dict() for l in v]
                for k, v in sorted(self.compositions.items())
            },
        }
