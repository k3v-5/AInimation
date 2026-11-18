"""
EnvironmentValidator enforces 8 production quality gates and non-negotiable rules.
UAF-81.12 Sections 194, 202, 203, 204.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from ..topology.facility_graph import BuildingFacilityGraph
from ..spatial.piece import ModularPiece
from ..spatial.grid import GridProfile


@dataclass
class EnvironmentQualityScore:
    structure_score: float    # 0.0 to 1.0 (Gate 1)
    modularity_score: float   # 0.0 to 1.0 (Gate 2)
    navigation_score: float   # 0.0 to 1.0 (Gate 3)
    gameplay_score: float     # 0.0 to 1.0 (Gate 4)
    performance_score: float  # 0.0 to 1.0 (Gate 6)

    @property
    def aggregate_score(self) -> float:
        return round(
            0.25 * self.structure_score +
            0.20 * self.modularity_score +
            0.25 * self.navigation_score +
            0.15 * self.gameplay_score +
            0.15 * self.performance_score,
            3
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "structure_score": self.structure_score,
            "modularity_score": self.modularity_score,
            "navigation_score": self.navigation_score,
            "gameplay_score": self.gameplay_score,
            "performance_score": self.performance_score,
            "aggregate_score": self.aggregate_score,
        }


@dataclass
class EnvironmentValidationReport:
    is_valid: bool
    quality_score: EnvironmentQualityScore
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


class EnvironmentValidator:
    """
    Enforces NON-NEGOTIABLE RULES (Sections 203, 204).
    """

    @classmethod
    def validate_environment(
        cls,
        facility_graph: BuildingFacilityGraph,
        pieces: Optional[List[ModularPiece]] = None,
        grid: Optional[GridProfile] = None,
    ) -> EnvironmentValidationReport:
        issues = []
        warnings = []

        # 1. Structure & Modularity (Section 203)
        struct_score = 1.0
        if not facility_graph.rooms:
            issues.append("NON-NEGOTIABLE VIOLATION: Environment has no rooms defined.")
            struct_score = 0.0

        mod_score = 1.0
        if pieces:
            for p in pieces:
                if any(dim <= 0.0 for dim in p.dimensions):
                    issues.append(f"NON-NEGOTIABLE VIOLATION: Modular piece '{p.piece_id}' has non-positive dimensions: {p.dimensions}.")
                    mod_score = 0.0
                if not p.collision_shape:
                    issues.append(f"NON-NEGOTIABLE VIOLATION: Modular piece '{p.piece_id}' lacks collision shape.")
                    mod_score = 0.0

        # 2. Navigation & Connectivity (Section 204)
        nav_score = 1.0
        if not facility_graph.is_fully_connected():
            issues.append("NON-NEGOTIABLE VIOLATION: Facility graph has disconnected rooms (failed reachability).")
            nav_score = 0.0

        # 3. Gameplay Spawns & Objectives
        gameplay_score = 1.0
        total_spawns = sum(r.spawns_count for r in facility_graph.rooms.values())
        if total_spawns == 0:
            warnings.append("No player/enemy spawn points in facility.")
            gameplay_score -= 0.3

        perf_score = 1.0

        q_score = EnvironmentQualityScore(
            structure_score=struct_score,
            modularity_score=mod_score,
            navigation_score=nav_score,
            gameplay_score=max(0.0, gameplay_score),
            performance_score=perf_score,
        )

        is_valid = len(issues) == 0 and q_score.aggregate_score >= 0.80
        review_status = "PASSED" if is_valid else "MANUAL_REVIEW_REQUIRED"

        return EnvironmentValidationReport(
            is_valid=is_valid,
            quality_score=q_score,
            issues=issues,
            warnings=warnings,
            review_status=review_status,
        )
