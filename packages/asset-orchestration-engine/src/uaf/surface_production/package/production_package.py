"""
SurfaceProductionPackage encapsulates complete, production-ready surface packages for Unreal Engine.
UAF-81.18 Sections 218, 219, 220.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from ..models.definition import SurfaceDefinition, MaterialPBRProfile
from ..models.textures import TextureChannelDefinition
from ..validation.production_validator import SurfaceProductionValidationReport
from ...core.hashing.canonical_hasher import CanonicalHasher


@dataclass
class SurfaceProductionPackage:
    asset_id: str
    uv_set_name: str
    surface_def: SurfaceDefinition
    material_profile: MaterialPBRProfile
    textures: List[TextureChannelDefinition] = field(default_factory=list)
    master_material_id: str = "M_Master_DefaultPBR"
    material_instance_id: str = "MI_Default"
    variants: Dict[str, Any] = field(default_factory=dict)
    validation_report: Optional[SurfaceProductionValidationReport] = None
    version: str = "1.0.0"

    @property
    def package_hash(self) -> str:
        return CanonicalHasher.compute_hash(self.to_dict())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "asset_id": self.asset_id,
            "uv_set_name": self.uv_set_name,
            "surface_def": self.surface_def.to_dict(),
            "material_profile": self.material_profile.to_dict(),
            "textures": [t.to_dict() for t in self.textures],
            "master_material_id": self.master_material_id,
            "material_instance_id": self.material_instance_id,
            "variants": self.variants,
            "validation_report": self.validation_report.to_dict() if self.validation_report else None,
            "version": self.version,
        }
