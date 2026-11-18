"""
AuthoredSurfacePackage encapsulates complete, validated PBR surfaces for Unreal production.
UAF-81.11 Sections 156, 196.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from ..models.regions import MaterialRegionGraph
from ...surface.models.texture_set import TextureSet
from ..validation.authoring_validator import SurfaceAuthoringValidationReport
from ...core.hashing.canonical_hasher import CanonicalHasher


@dataclass
class AuthoredSurfacePackage:
    asset_id: str
    archetype_name: str
    region_graph: MaterialRegionGraph
    texture_set: TextureSet
    master_material_id: str = "M_Master_PBR"
    material_instances: List[str] = field(default_factory=list)
    validation_report: Optional[SurfaceAuthoringValidationReport] = None
    version: str = "1.0.0"

    @property
    def package_hash(self) -> str:
        return CanonicalHasher.compute_hash(self.to_dict())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "asset_id": self.asset_id,
            "archetype_name": self.archetype_name,
            "region_graph": self.region_graph.to_dict(),
            "texture_set": self.texture_set.to_dict(),
            "master_material_id": self.master_material_id,
            "material_instances": self.material_instances,
            "validation_report": self.validation_report.to_dict() if self.validation_report else None,
            "version": self.version,
        }
