"""
SurfaceFabricationPackage encapsulates complete production-ready surface packages for Unreal Engine.
UAF-81.15 Sections 200, 211.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from ..models.profile import SurfaceProfile
from ..models.graph import MaterialGraphContract
from ..validation.fabrication_validator import SurfaceFabricationValidationReport
from ...core.hashing.canonical_hasher import CanonicalHasher


@dataclass
class SurfaceFabricationPackage:
    asset_id: str
    surface_profile: SurfaceProfile
    graph_contract: MaterialGraphContract
    textures: List[str] = field(default_factory=list)
    validation_report: Optional[SurfaceFabricationValidationReport] = None
    version: str = "1.0.0"

    @property
    def package_hash(self) -> str:
        return CanonicalHasher.compute_hash(self.to_dict())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "asset_id": self.asset_id,
            "surface_profile": self.surface_profile.to_dict(),
            "graph_contract": self.graph_contract.to_dict(),
            "textures": self.textures,
            "validation_report": self.validation_report.to_dict() if self.validation_report else None,
            "version": self.version,
        }
