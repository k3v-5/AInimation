"""
WorldBuildingValidator enforces valid grid scaling, complete spatial graph connectivity, and relative path contracts.
UAF-81.28 Sections 5, 114, 119, 122, 124.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from ..models.definition import PlayableWorldDefinition
from ..models.graph import BlockoutWorldGraph


@dataclass
class WorldBuildingQualityScore:
    grid_score: float          # 0.0 to 1.0 (Grid size >= 100cm, modular alignment)
    connectivity_score: float  # 0.0 to 1.0 (Graph BFS reachability, critical path connected)
    clearance_score: float     # 0.0 to 1.0 (Positive zone dimensions)
    streaming_score: float     # 0.0 to 1.0 (Valid level reference)

    @property
    def aggregate_score(self) -> float:
        return round(
            0.25 * self.grid_score +
            0.35 * self.connectivity_score +
            0.20 * self.clearance_score +
            0.20 * self.streaming_score,
            3
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "grid_score": self.grid_score,
            "connectivity_score": self.connectivity_score,
            "clearance_score": self.clearance_score,
            "streaming_score": self.streaming_score,
            "aggregate_score": self.aggregate_score,
        }


@dataclass
class WorldBuildingValidationReport:
    is_valid: bool
    quality_score: WorldBuildingQualityScore
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


class WorldBuildingValidator:
    """
    Enforces NON-NEGOTIABLE REQUIREMENTS (Sections 5, 114, 119, 124).
    """

    @classmethod
    def validate_world_build(
        cls,
        world_def: PlayableWorldDefinition,
        graph: BlockoutWorldGraph,
        level_ref: str,
    ) -> WorldBuildingValidationReport:
        issues = []
        warnings = []

        # 1. Grid scaling checks (Section 5 & 114)
        grid_score = 1.0
        if not world_def.is_valid_grid:
            issues.append(f"NON-NEGOTIABLE VIOLATION: World grid size {world_def.grid_size_cm}cm is below minimum 100.0cm threshold.")
            grid_score = 0.0

        # 2. Connectivity & Critical Path checks (Section 124)
        conn_score = 1.0
        if not graph.is_fully_connected():
            issues.append("NON-NEGOTIABLE VIOLATION: World contains isolated, unreachable rooms or blockout zones.")
            conn_score = 0.0

        if not graph.is_critical_path_connected():
            issues.append("NON-NEGOTIABLE VIOLATION: Broken critical path detected; one or more critical gameplay zones are unreachable.")
            conn_score = 0.0

        # 3. Zone dimensions checks
        clearance_score = 1.0
        for z_id, node in graph.zones.items():
            if any(dim <= 0.0 for dim in node.dimensions_xyz):
                issues.append(f"NON-NEGOTIABLE VIOLATION: Zone '{z_id}' has non-positive dimensions: {node.dimensions_xyz}.")
                clearance_score = 0.0

        # 4. Path purity (Section 119)
        stream_score = 1.0
        if ":\\" in level_ref or ":/" in level_ref or level_ref.startswith("/"):
            issues.append(f"NON-NEGOTIABLE VIOLATION: Absolute machine-dependent path in level reference: '{level_ref}'.")
            stream_score = 0.0

        q_score = WorldBuildingQualityScore(
            grid_score=grid_score,
            connectivity_score=conn_score,
            clearance_score=clearance_score,
            streaming_score=stream_score,
        )

        is_valid = len(issues) == 0 and q_score.aggregate_score >= 0.85
        review_status = "PASSED" if is_valid else "MANUAL_REVIEW_REQUIRED"

        return WorldBuildingValidationReport(
            is_valid=is_valid,
            quality_score=q_score,
            issues=issues,
            warnings=warnings,
            review_status=review_status,
        )
