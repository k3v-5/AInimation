"""
SurfaceDefinition specifies the complete semantic and physical description of a surface.
UAF-81.4 Sections 4, 5.
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, Any, List
from .channels import ShaderModel, PBRChannel
from ...core.hashing.canonical_hasher import CanonicalHasher


class SemanticSurfaceRole(str, Enum):
    SKIN = "SKIN"
    METAL = "METAL"
    PAINTED_METAL = "PAINTED_METAL"
    RUBBER = "RUBBER"
    CLOTH = "CLOTH"
    LEATHER = "LEATHER"
    PLASTIC = "PLASTIC"
    GLASS = "GLASS"
    CERAMIC = "CERAMIC"
    STONE = "STONE"
    WOOD = "WOOD"
    CONCRETE = "CONCRETE"
    ORGANIC = "ORGANIC"
    ENERGY = "ENERGY"
    EMISSIVE = "EMISSIVE"
    LIQUID = "LIQUID"


@dataclass
class SurfaceDefinition:
    surface_id: str
    semantic_role: SemanticSurfaceRole
    material_family: str
    shader_model: ShaderModel = ShaderModel.DEFAULT_LIT
    texture_policy: str = "hybrid"  # "procedural", "baked", "hybrid"
    channel_policy: List[str] = field(
        default_factory=lambda: [
            PBRChannel.BASE_COLOR.value,
            PBRChannel.METALLIC.value,
            PBRChannel.ROUGHNESS.value,
            PBRChannel.NORMAL.value,
            PBRChannel.AMBIENT_OCCLUSION.value,
        ]
    )
    resolution_policy: int = 2048
    tiling_policy: str = "unique"  # "unique", "tiling", "udim", "trim_sheet"
    detail_policy: str = "normal"  # "geometry", "normal", "displacement"
    target_policy: str = "UE5_PC"
    quality_profile: str = "production"
    parameters: Dict[str, Any] = field(default_factory=dict)

    @property
    def surface_hash(self) -> str:
        return CanonicalHasher.compute_hash(self.to_dict())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "surface_id": self.surface_id,
            "semantic_role": self.semantic_role.value,
            "material_family": self.material_family,
            "shader_model": self.shader_model.value,
            "texture_policy": self.texture_policy,
            "channel_policy": self.channel_policy,
            "resolution_policy": self.resolution_policy,
            "tiling_policy": self.tiling_policy,
            "detail_policy": self.detail_policy,
            "target_policy": self.target_policy,
            "quality_profile": self.quality_profile,
            "parameters": self.parameters,
        }
