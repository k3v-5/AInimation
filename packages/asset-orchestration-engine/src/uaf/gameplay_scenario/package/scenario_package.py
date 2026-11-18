"""
PlayableScenarioPackage encapsulates complete, production-ready playable scenario packages for Unreal Engine.
UAF-81.20 Sections 182, 183.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from ..models.scenario_def import PlayableScenarioDefinition
from ..models.graph import GameplayGraph
from ..models.elements import ScenarioObjective, ScenarioEncounter
from ..validation.scenario_validator import GameplayValidationReport
from ...core.hashing.canonical_hasher import CanonicalHasher


@dataclass
class PlayableScenarioPackage:
    asset_id: str
    scenario_def: PlayableScenarioDefinition
    gameplay_graph: GameplayGraph
    objectives: List[ScenarioObjective] = field(default_factory=list)
    encounters: List[ScenarioEncounter] = field(default_factory=list)
    checkpoints_count: int = 1
    validation_report: Optional[GameplayValidationReport] = None
    version: str = "1.0.0"

    @property
    def package_hash(self) -> str:
        return CanonicalHasher.compute_hash(self.to_dict())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "asset_id": self.asset_id,
            "scenario_def": self.scenario_def.to_dict(),
            "gameplay_graph": self.gameplay_graph.to_dict(),
            "objectives": [o.to_dict() for o in self.objectives],
            "encounters": [e.to_dict() for e in self.encounters],
            "checkpoints_count": self.checkpoints_count,
            "validation_report": self.validation_report.to_dict() if self.validation_report else None,
            "version": self.version,
        }
