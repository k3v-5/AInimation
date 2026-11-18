"""
EnvironmentPackage encapsulates complete, production-ready environment data for Unreal Engine.
UAF-81.12 Sections 174, 175, 202.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from ..topology.facility_graph import BuildingFacilityGraph
from ..spatial.grid import GridProfile
from ..spatial.piece import ModularPiece
from ..validation.environment_validator import EnvironmentValidationReport
from ...core.hashing.canonical_hasher import CanonicalHasher


@dataclass
class EnvironmentPackage:
    asset_id: str
    environment_type: str
    facility_graph: BuildingFacilityGraph
    grid_profile: GridProfile
    pieces: List[ModularPiece] = field(default_factory=list)
    validation_report: Optional[EnvironmentValidationReport] = None
    version: str = "1.0.0"

    @property
    def package_hash(self) -> str:
        return CanonicalHasher.compute_hash(self.to_dict())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "asset_id": self.asset_id,
            "environment_type": self.environment_type,
            "facility_graph": self.facility_graph.to_dict(),
            "grid_profile": self.grid_profile.to_dict(),
            "pieces": [p.to_dict() for p in self.pieces],
            "validation_report": self.validation_report.to_dict() if self.validation_report else None,
            "version": self.version,
        }
