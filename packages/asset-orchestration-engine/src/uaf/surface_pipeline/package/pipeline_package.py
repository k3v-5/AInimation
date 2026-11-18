"""
SurfacePipelinePackage encapsulates complete, production-ready surface and UV asset packages for Unreal Engine.
UAF-81.27 Sections 117, 121, 122, 128.
"""

from dataclasses import dataclass
from typing import Dict, Any, Optional
from ..models.definition import SurfaceDefinition27
from ..validation.pipeline_validator import SurfacePipelineValidationReport
from ...core.hashing.canonical_hasher import CanonicalHasher


@dataclass
class SurfacePipelinePackage:
    asset_id: str
    surface_def: SurfaceDefinition27
    master_material_ref: str = "M_Master_Default"
    instance_material_ref: str = "MI_Default"
    validation_report: Optional[SurfacePipelineValidationReport] = None
    version: str = "1.0.0"

    @property
    def package_hash(self) -> str:
        return CanonicalHasher.compute_hash(self.to_dict())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "asset_id": self.asset_id,
            "surface_def": self.surface_def.to_dict(),
            "master_material_ref": self.master_material_ref,
            "instance_material_ref": self.instance_material_ref,
            "validation_report": self.validation_report.to_dict() if self.validation_report else None,
            "version": self.version,
        }
