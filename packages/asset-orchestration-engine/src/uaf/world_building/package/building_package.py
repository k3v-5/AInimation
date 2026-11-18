"""
WorldBuildingPackage encapsulates complete, production-ready playable world environments for Unreal Engine.
UAF-81.28 Sections 118, 121, 132, 133.
"""

from dataclasses import dataclass
from typing import Dict, Any, Optional
from ..models.definition import PlayableWorldDefinition
from ..models.graph import BlockoutWorldGraph
from ..validation.building_validator import WorldBuildingValidationReport
from ...core.hashing.canonical_hasher import CanonicalHasher


@dataclass
class WorldBuildingPackage:
    asset_id: str
    world_def: PlayableWorldDefinition
    graph: BlockoutWorldGraph
    level_ref: str = "LV_Default"
    validation_report: Optional[WorldBuildingValidationReport] = None
    version: str = "1.0.0"

    @property
    def package_hash(self) -> str:
        return CanonicalHasher.compute_hash(self.to_dict())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "asset_id": self.asset_id,
            "world_def": self.world_def.to_dict(),
            "graph": self.graph.to_dict(),
            "level_ref": self.level_ref,
            "validation_report": self.validation_report.to_dict() if self.validation_report else None,
            "version": self.version,
        }
