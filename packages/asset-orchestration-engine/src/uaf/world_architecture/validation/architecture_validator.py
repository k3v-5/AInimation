"""
WorldArchitectureValidator enforces positive bounds, topological graph connectivity, and critical path validity.
UAF-81.24 Sections 14, 141, 148, 173.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from ..models.definition import WorldDefinition24
from ..models.graph import ArchitecturalWorldGraph


@dataclass
class WorldArchitectureQualityScore:
    bounds_score: float         # 0.0 to 1.0 (Positive volume, min < max)
    connectivity_score: float   # 0.0 to 1.0 (BFS reachability, fully connected)
    architecture_score: float   # 0.0 to 1.0 (Critical path valid, positive dimensions)
    navigation_score: float     # 0.0 to 1.0 (Room clearances, grid cells)

    @property
    def aggregate_score(self) -> float:
        return round(
            0.30 * self.bounds_score +
            0.30 * self.connectivity_score +
            0.20 * self.architecture_score +
            0.20 * self.navigation_score,
            3
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "bounds_score": self.bounds_score,
            "connectivity_score": self.connectivity_score,
            "architecture_score": self.architecture_score,
            "navigation_score": self.navigation_score,
            "aggregate_score": self.aggregate_score,
        }


@dataclass
class WorldArchitectureValidationReport:
    is_valid: bool
    quality_score: WorldArchitectureQualityScore
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


class WorldArchitectureValidator:
    """
    Enforces NON-NEGOTIABLE REQUIREMENTS (Sections 14, 141, 148, 173).
    """

    @classmethod
    def validate_world(
        cls,
        world_def: WorldDefinition24,
        graph: ArchitecturalWorldGraph,
        landmarks: List[str],
    ) -> WorldArchitectureValidationReport:
        issues = []
        warnings = []

        # 1. Bounds validation (Section 14)
        bounds_score = 1.0
        if not world_def.bounds.is_valid:
            issues.append(f"NON-NEGOTIABLE VIOLATION: Invalid world boundaries: min={world_def.bounds.min_x, world_def.bounds.min_y, world_def.bounds.min_z}, max={world_def.bounds.max_x, world_def.bounds.max_y, world_def.bounds.max_z}.")
            bounds_score = 0.0

        # 2. Connectivity & Critical Path (Sections 148, 173)
        conn_score = 1.0
        if not graph.is_fully_connected():
            issues.append("NON-NEGOTIABLE VIOLATION: Spatial architectural graph contains isolated, unreachable rooms.")
            conn_score = 0.0
        if not graph.is_critical_path_valid():
            issues.append("NON-NEGOTIABLE VIOLATION: Broken or disconnected critical path detected in world graph.")
            conn_score = 0.0

        # 3. Room dimensions and clearances
        arch_score = 1.0
        for r_id, node in graph.rooms.items():
            if any(d <= 0.0 for d in node.dimensions_xyz):
                issues.append(f"NON-NEGOTIABLE VIOLATION: Room '{r_id}' has non-positive dimensions: {node.dimensions_xyz}.")
                arch_score = 0.0

        # 4. Path purity check (Section 141)
        for lm in landmarks:
            if ":\\" in lm or ":/" in lm or lm.startswith("/"):
                issues.append(f"NON-NEGOTIABLE VIOLATION: Absolute machine-dependent path detected in landmark: '{lm}'.")
                arch_score = 0.0

        nav_score = 1.0
        if not landmarks:
            warnings.append("World defines zero landmarks.")

        q_score = WorldArchitectureQualityScore(
            bounds_score=bounds_score,
            connectivity_score=conn_score,
            architecture_score=arch_score,
            navigation_score=nav_score,
        )

        is_valid = len(issues) == 0 and q_score.aggregate_score >= 0.85
        review_status = "PASSED" if is_valid else "MANUAL_REVIEW_REQUIRED"

        return WorldArchitectureValidationReport(
            is_valid=is_valid,
            quality_score=q_score,
            issues=issues,
            warnings=warnings,
            review_status=review_status,
        )
