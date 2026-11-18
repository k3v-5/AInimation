"""
ModularWorldPackage encapsulates complete, production-ready modular world packages for Unreal Engine.
UAF-81.19 Sections 175, 183, 188, 212.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from ..models.definition import EnvironmentDefinition
from ..models.spatial_graph import SpatialLayoutGraph
from ..validation.modular_world_validator import ModularWorldValidationReport
from ...core.hashing.canonical_hasher import CanonicalHasher


@dataclass
class ModularWorldPackage:
    asset_id: str
    environment_def: EnvironmentDefinition
    layout_graph: SpatialLayoutGraph
    modules_placed_count: int = 0
    props_placed_count: int = 0
    nav_mesh_ready: bool = True
    collision_ready: bool = True
    validation_report: Optional[ModularWorldValidationReport] = None
    version: str = "1.0.0"

    @property
    def package_hash(self) -> str:
        return CanonicalHasher.compute_hash(self.to_dict())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "asset_id": self.asset_id,
            "environment_def": self.environment_def.to_dict(),
            "layout_graph": self.layout_graph.to_dict(),
            "modules_placed_count": self.modules_placed_count,
            "props_placed_count": self.props_placed_count,
            "nav_mesh_ready": self.nav_mesh_ready,
            "collision_ready": self.collision_ready,
            "validation_report": self.validation_report.to_dict() if self.validation_report else None,
            "version": self.version,
        }
