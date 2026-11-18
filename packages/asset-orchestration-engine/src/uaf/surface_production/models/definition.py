"""
SurfaceDefinition, MaterialPBRProfile, and SurfaceWeatheringState models.
UAF-81.18 Sections 3, 4, 6, 7, 10, 11, 201.
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from ...core.hashing.canonical_hasher import CanonicalHasher


class SurfaceWeatheringState(str, Enum):
    CLEAN = "CLEAN"
    WORN = "WORN"
    DAMAGED = "DAMAGED"
    WET = "WET"
    FROZEN = "FROZEN"
    CORRODED = "CORRODED"


@dataclass
class MaterialPBRProfile:
    base_color_hex: str = "#A0A0A0"
    metallic: float = 0.0
    roughness: float = 0.5
    normal_strength: float = 1.0
    emissive_hex: Optional[str] = None
    opacity: float = 1.0
    subsurface_color_hex: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "base_color_hex": self.base_color_hex,
            "metallic": self.metallic,
            "roughness": self.roughness,
            "normal_strength": self.normal_strength,
            "emissive_hex": self.emissive_hex,
            "opacity": self.opacity,
            "subsurface_color_hex": self.subsurface_color_hex,
        }


@dataclass
class SurfaceDefinition:
    surface_id: str
    surface_type: str = "METAL"  # "SKIN", "METAL", "ARMOR", "FABRIC", "CONCRETE", "WOOD", "GLASS", etc.
    material_family: str = "STEEL"
    resolution: int = 2048
    texel_density: float = 512.0  # px/m
    weathering_state: SurfaceWeatheringState = SurfaceWeatheringState.CLEAN
    seed: int = 42

    @property
    def definition_hash(self) -> str:
        return CanonicalHasher.compute_hash(self.to_dict())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "surface_id": self.surface_id,
            "surface_type": self.surface_type,
            "material_family": self.material_family,
            "resolution": self.resolution,
            "texel_density": self.texel_density,
            "weathering_state": self.weathering_state.value,
            "seed": self.seed,
        }
