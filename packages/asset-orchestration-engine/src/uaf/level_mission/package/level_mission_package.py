"""
LevelMissionPackage encapsulates complete, production-ready playable levels, missions, encounters, and flow packages for Unreal Engine.
UAF-81.41 Sections 143, 166.
"""

from dataclasses import dataclass
from typing import Dict, Any, Optional
from ..models.definition import PlayableLevelSpecification
from ..validation.level_mission_validator import LevelMissionValidationReport
from ...core.hashing.canonical_hasher import CanonicalHasher


@dataclass
class LevelMissionPackage:
    level_id: str
    spec: PlayableLevelSpecification
    mission_graph_path: str = "/Game/Missions/Graphs/MG_Default"
    gameplay_package_path: str = "/Game/Missions/Packages/GP_Default"
    validation_report: Optional[LevelMissionValidationReport] = None
    version: str = "1.0.0"

    @property
    def package_hash(self) -> str:
        return CanonicalHasher.compute_hash(self.to_dict())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "level_id": self.level_id,
            "spec": self.spec.to_dict(),
            "mission_graph_path": self.mission_graph_path,
            "gameplay_package_path": self.gameplay_package_path,
            "validation_report": self.validation_report.to_dict() if self.validation_report else None,
            "version": self.version,
        }
