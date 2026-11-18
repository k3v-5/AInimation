"""
GameplayScenarioValidator enforces graph solvability, objective reachability, and lock prevention.
UAF-81.20 Sections 18, 19, 20, 153, 154, 155, 157, 180.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from ..models.scenario_def import PlayableScenarioDefinition
from ..models.graph import GameplayGraph, GameplayNodeType
from ..models.elements import ScenarioObjective, ScenarioEncounter


@dataclass
class GameplayQualityScore:
    graph_score: float      # 0.0 to 1.0 (Valid START/END, directed path solvability)
    objective_score: float  # 0.0 to 1.0 (Primary objectives reachable, non-circular)
    encounter_score: float  # 0.0 to 1.0 (Encounters solvable, valid spawns)
    balance_score: float    # 0.0 to 1.0 (Checkpoints, pacing)

    @property
    def aggregate_score(self) -> float:
        return round(
            0.35 * self.graph_score +
            0.30 * self.objective_score +
            0.20 * self.encounter_score +
            0.15 * self.balance_score,
            3
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "graph_score": self.graph_score,
            "objective_score": self.objective_score,
            "encounter_score": self.encounter_score,
            "balance_score": self.balance_score,
            "aggregate_score": self.aggregate_score,
        }


@dataclass
class GameplayValidationReport:
    is_valid: bool
    quality_score: GameplayQualityScore
    issues: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    review_status: str = "PASSED"  # "PASSED", "MANUAL_REVIEW_REQUIRED"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "is_valid": self.is_valid,
            "quality_score": self.quality_score.to_dict(),
            "issues": self.issues,
            "warnings": self.warnings,
            "review_status": self.review_status,
        }


class GameplayScenarioValidator:
    """
    Enforces NON-NEGOTIABLE REQUIREMENTS (Sections 18, 19, 153, 155, 157, 180).
    """

    @classmethod
    def validate_scenario(
        cls,
        scenario_def: PlayableScenarioDefinition,
        graph: GameplayGraph,
        objectives: List[ScenarioObjective],
        encounters: List[ScenarioEncounter],
        checkpoints_count: int,
    ) -> GameplayValidationReport:
        issues = []
        warnings = []

        # 1. Graph solvability check (Sections 153, 157)
        graph_score = 1.0
        if not graph.has_start_and_end():
            issues.append("NON-NEGOTIABLE VIOLATION: Gameplay graph lacks START or END node.")
            graph_score = 0.0
        elif not graph.is_solvable_path_exists():
            issues.append("NON-NEGOTIABLE VIOLATION: No reachable path from START to END node (hardlock detected).")
            graph_score = 0.0

        # 2. Objective reachability & softlock detection (Sections 18, 19, 154)
        obj_score = 1.0
        if not objectives:
            warnings.append("Scenario defines zero gameplay objectives.")
        for obj in objectives:
            if obj.is_primary and not obj.is_reachable:
                issues.append(f"NON-NEGOTIABLE VIOLATION: Primary objective '{obj.objective_id}' is unreachable (softlock detected).")
                obj_score = 0.0

        # 3. Encounter solvability (Sections 155, 157)
        enc_score = 1.0
        for enc in encounters:
            if not enc.is_solvable:
                issues.append(f"NON-NEGOTIABLE VIOLATION: Encounter '{enc.encounter_id}' is flagged unwinnable/unsolvable.")
                enc_score = 0.0

        balance_score = 1.0 if checkpoints_count > 0 else 0.8
        if checkpoints_count == 0:
            warnings.append("Scenario defines no checkpoints for player recovery.")

        q_score = GameplayQualityScore(
            graph_score=graph_score,
            objective_score=obj_score,
            encounter_score=enc_score,
            balance_score=balance_score,
        )

        is_valid = len(issues) == 0 and q_score.aggregate_score >= 0.85
        review_status = "PASSED" if is_valid else "MANUAL_REVIEW_REQUIRED"

        return GameplayValidationReport(
            is_valid=is_valid,
            quality_score=q_score,
            issues=issues,
            warnings=warnings,
            review_status=review_status,
        )
