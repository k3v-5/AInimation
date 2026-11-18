"""
UniversalSurfacePackage encapsulates complete, production-ready materials, texture sets, and material instances for Unreal Engine.
UAF-81.52 Sections 147, 150.
"""

from dataclasses import dataclass
from typing import Dict, Any, Optional
from ..models.definition import UniversalSurfaceSpecification
from ..validation.universal_surface_validator import UniversalSurfaceValidationReport
from ...core.hashing.canonical_hasher import CanonicalHasher


@dataclass
class UniversalSurfacePackage:
    surface_id: str
    spec: UniversalSurfaceSpecification
    master_material_path: str = "/Game/Materials/Universal/Master/M_Default"
    material_instance_path: str = "/Game/Materials/Universal/Instances/MI_Default"
    texture_set_path: str = "/Game/Materials/Universal/Textures/T_Default"
    validation_report: Optional[UniversalSurfaceValidationReport] = None
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
            "texture_set_path": self.texture_set_path,
            "validation_report": self.validation_report.to_dict() if self.validation_report else None,
            "version": self.version,
        }
