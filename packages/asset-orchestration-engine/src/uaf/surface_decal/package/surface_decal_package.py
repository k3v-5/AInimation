"""
SurfaceDecalPackage encapsulates complete, production-ready procedural surfaces, wear, and decals for Unreal Engine.
UAF-81.34 Sections 145, 146.
"""

from dataclasses import dataclass
from typing import Dict, Any, Optional
from ..models.definition import SurfaceAuthoringSpecification
from ..validation.surface_decal_validator import SurfaceDecalValidationReport
from ...core.hashing.canonical_hasher import CanonicalHasher


@dataclass
class SurfaceDecalPackage:
    asset_id: str
    surface_spec: SurfaceAuthoringSpecification
    master_material_ref: str = "M_Master_Default"
    instance_material_ref: str = "MI_Default"
    validation_report: Optional[SurfaceDecalValidationReport] = None
    version: str = "1.0.0"

    @property
    def package_hash(self) -> str:
        return CanonicalHasher.compute_hash(self.to_dict())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "asset_id": self.asset_id,
            "surface_spec": self.surface_spec.to_dict(),
            "master_material_ref": self.master_material_ref,
            "instance_material_ref": self.instance_material_ref,
            "validation_report": self.validation_report.to_dict() if self.validation_report else None,
            "version": self.version,
        }
