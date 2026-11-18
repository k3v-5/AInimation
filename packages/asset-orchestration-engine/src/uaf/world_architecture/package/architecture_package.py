"""
WorldArchitecturePackage encapsulates complete, production-ready world architecture packages for Unreal Engine.
UAF-81.24 Sections 156, 157.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from ..models.definition import WorldDefinition24, WorldGridCell
from ..models.graph import ArchitecturalWorldGraph
from ..validation.architecture_validator import WorldArchitectureValidationReport
from ...core.hashing.canonical_hasher import CanonicalHasher


@dataclass
class WorldArchitecturePackage:
    asset_id: str
    world_def: WorldDefinition24
    graph: ArchitecturalWorldGraph
    grid_cells: List[WorldGridCell] = field(default_factory=list)
    landmarks: List[str] = field(default_factory=list)
    validation_report: Optional[WorldArchitectureValidationReport] = None
    version: str = "1.0.0"

    @property
    def package_hash(self) -> str:
        return CanonicalHasher.compute_hash(self.to_dict())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "asset_id": self.asset_id,
            "world_def": self.world_def.to_dict(),
            "graph": self.graph.to_dict(),
            "grid_cells": [c.to_dict() for c in self.grid_cells],
            "landmarks": self.landmarks,
            "validation_report": self.validation_report.to_dict() if self.validation_report else None,
            "version": self.version,
        }
