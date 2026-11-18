"""
SurfaceDetailPackage encapsulates complete, production-ready surface detail packages for Unreal Engine.
UAF-81.22 Sections 146, 147, 148, 153.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from ..models.definition import SurfaceDetailDefinition
from ..models.textures import SurfaceDetailChannel
from ..validation.detail_validator import SurfaceDetailValidationReport
from ...core.hashing.canonical_hasher import CanonicalHasher


@dataclass
class SurfaceDetailPackage:
    asset_id: str
    surface_def: SurfaceDetailDefinition
    textures: List[SurfaceDetailChannel] = field(default_factory=list)
    master_material_id: str = "M_Master_PBR"
    material_instance_id: str = "MI_Default"
    validation_report: Optional[SurfaceDetailValidationReport] = None
    version: str = "1.0.0"

    @property
    def package_hash(self) -> str:
        return CanonicalHasher.compute_hash(self.to_dict())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "asset_id": self.asset_id,
            "surface_def": self.surface_def.to_dict(),
            "textures": [t.to_dict() for t in self.textures],
            "master_material_id": self.master_material_id,
            "material_instance_id": self.material_instance_id,
            "validation_report": self.validation_report.to_dict() if self.validation_report else None,
            "version": self.version,
        }
