"""
WorldValidator enforces structural alignment, path connectivity, and multi-dimensional quality gates.
UAF-81.6 Sections 15, 19, 21, 87, 88, 113, 121.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from ..assembly.assembly_graph import AssemblyGraph
from ..gameplay.navigation import NavigationMeshMetadata
from ..gameplay.spatial_gameplay import SpawnPoint, ObjectiveDefinition


@dataclass
class WorldQualityScore:
    structural_score: float  # 0.0 to 1.0 (no overlaps/floating)
    gameplay_score: float    # 0.0 to 1.0 (spawn, cover, objectives present)
    navigation_score: float  # 0.0 to 1.0 (critical path guaranteed)
    performance_score: float # 0.0 to 1.0 (within budget)

    @property
    def aggregate_score(self) -> float:
        return round(
            0.30 * self.structural_score +
            0.30 * self.navigation_score +
            0.20 * self.gameplay_score +
            0.20 * self.performance_score,
            3
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "structural_score": self.structural_score,
            "gameplay_score": self.gameplay_score,
            "navigation_score": self.navigation_score,
            "performance_score": self.performance_score,
            "aggregate_score": self.aggregate_score,
        }


@dataclass
class WorldValidationReport:
    is_valid: bool
    issues: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    quality_score: Optional[WorldQualityScore] = None
    review_status: str = "PASSED"  # "PASSED", "MANUAL_REVIEW_REQUIRED"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "is_valid": self.is_valid,
            "issues": self.issues,
            "warnings": self.warnings,
            "quality_score": self.quality_score.to_dict() if self.quality_score else None,
            "review_status": self.review_status,
        }


class WorldValidator:
    """
    Automated gate ensuring generated worlds are structurally sound, playable, navigable, and performant.
    Enforces NON-NEGOTIABLE RULE (Section 121).
    """
    @classmethod
    def validate_world(
        cls,
        assembly: AssemblyGraph,
        navigation: Optional[NavigationMeshMetadata] = None,
        spawns: Optional[List[SpawnPoint]] = None,
        objectives: Optional[List[ObjectiveDefinition]] = None,
        spawn_wp: Optional[str] = None,
        objective_wp: Optional[str] = None,
        max_actor_budget: int = 5000,
    ) -> WorldValidationReport:
        issues = []
        warnings = []

        # 1. Structural Validation (Overlaps)
        overlaps = assembly.check_overlaps()
        struct_score = 1.0
        if overlaps:
            for inst_a, inst_b in overlaps:
                issues.append(f"Module overlap collision detected between '{inst_a}' and '{inst_b}'.")
            struct_score = max(0.0, 1.0 - (len(overlaps) * 0.2))

        # 2. Gameplay Validation (Spawns & Objectives)
        gameplay_score = 1.0
        if spawns is not None and not spawns:
            issues.append("World has no player spawn points.")
            gameplay_score -= 0.5
        if objectives is not None and not objectives:
            warnings.append("World has no defined mission objectives.")
            gameplay_score -= 0.2

        # 3. Navigation & Critical Path Guarantee (Section 21)
        nav_score = 1.0
        if navigation and spawn_wp and objective_wp:
            has_route = navigation.has_path(spawn_wp, objective_wp)
            if not has_route:
                issues.append(f"Path guarantee violation: No navigable path between spawn '{spawn_wp}' and objective '{objective_wp}'.")
                nav_score = 0.0
        elif navigation and len(navigation.waypoints) == 0:
            warnings.append("Navigation metadata has no waypoints.")
            nav_score = 0.5

        # 4. Performance Validation
        perf_score = 1.0
        if assembly.node_count > max_actor_budget:
            issues.append(f"Module count {assembly.node_count} exceeds actor budget {max_actor_budget}.")
            perf_score = 0.5

        q_score = WorldQualityScore(
            structural_score=struct_score,
            gameplay_score=max(0.0, gameplay_score),
            navigation_score=nav_score,
            performance_score=perf_score,
        )

        is_valid = len(issues) == 0 and q_score.aggregate_score >= 0.75
        review_status = "PASSED" if is_valid else "MANUAL_REVIEW_REQUIRED"

        return WorldValidationReport(
            is_valid=is_valid,
            issues=issues,
            warnings=warnings,
            quality_score=q_score,
            review_status=review_status,
        )
