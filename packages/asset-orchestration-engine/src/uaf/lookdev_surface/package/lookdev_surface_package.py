"""
LookdevSurfacePackage encapsulates complete, production-ready look-development surfaces, master materials, and instances for Unreal Engine.
UAF-81.46 Sections 124, 125.
"""

from dataclasses import dataclass
from typing import Dict, Any, Optional
from ..models.definition import LookdevSurfaceSpecification
from ..validation.lookdev_surface_validator import LookdevSurfaceValidationReport
from ...core.hashing.canonical_hasher import CanonicalHasher


@dataclass
class LookdevSurfacePackage:
    surface_id: str
    spec: LookdevSurfaceSpecification
    master_material_path: str = "/Game/Lookdev/Materials/M_Default"
    material_instance_path: str = "/Game/Lookdev/Instances/MI_Default"
    texture_set_path: str = "/Game/Lookdev/Textures/T_Default"
    validation_report: Optional[LookdevSurfaceValidationReport] = None
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
