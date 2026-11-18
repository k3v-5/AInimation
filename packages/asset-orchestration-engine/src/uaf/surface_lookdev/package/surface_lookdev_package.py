"""
SurfaceLookdevPackage encapsulates complete, production-ready materials, instances, and PBR look-development for Unreal Engine.
UAF-81.38 Sections 143, 149.
"""

from dataclasses import dataclass
from typing import Dict, Any, Optional
from ..models.definition import SurfaceLookdevSpecification
from ..validation.surface_lookdev_validator import SurfaceLookdevValidationReport
from ...core.hashing.canonical_hasher import CanonicalHasher


@dataclass
class SurfaceLookdevPackage:
    surface_id: str
    spec: SurfaceLookdevSpecification
    master_material_path: str = "/Game/Materials/Masters/M_Master_Default"
    material_instance_path: str = "/Game/Materials/Instances/MI_Default"
    validation_report: Optional[SurfaceLookdevValidationReport] = None
    version: str = "1.0.0"

    @property
    def package_hash(self) -> str:
        return CanonicalHasher.compute_hash(self.to_dict())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "surface_id": self.surface_id,
            "spec": self.spec.to_dict(),
            "master_material_path": self.master_material_path,
            "material_instance_path": self.material_instance_path,
            "validation_report": self.validation_report.to_dict() if self.validation_report else None,
            "version": self.version,
        }
