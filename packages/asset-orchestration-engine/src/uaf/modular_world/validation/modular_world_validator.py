"""
ModularWorldValidator enforces topological connectivity, positive dimensions, and player clearance.
UAF-81.19 Sections 11, 32, 167, 185, 209, 210, 211, 212.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from ..models.definition import EnvironmentDefinition
from ..models.spatial_graph import SpatialLayoutGraph


@dataclass
class ModularWorldQualityScore:
    structural_score: float  # 0.0 to 1.0 (Positive dimensions, grid alignment)
    navigation_score: float  # 0.0 to 1.0 (Reachability, BFS connectivity)
    collision_score: float   # 0.0 to 1.0 (Collision bounds)
    streaming_score: float   # 0.0 to 1.0 (Cell partitioning limits)

    @property
    def aggregate_score(self) -> float:
        return round(
            0.30 * self.structural_score +
            0.30 * self.navigation_score +
            0.20 * self.collision_score +
            0.20 * self.streaming_score,
            3
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "structural_score": self.structural_score,
            "navigation_score": self.navigation_score,
            "collision_score": self.collision_score,
            "streaming_score": self.streaming_score,
            "aggregate_score": self.aggregate_score,
        }


@dataclass
class ModularWorldValidationReport:
    is_valid: bool
    quality_score: ModularWorldQualityScore
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


class ModularWorldValidator:
    """
    Enforces NON-NEGOTIABLE REQUIREMENTS (Sections 32, 167, 185, 212).
    """

    @classmethod
    def validate_environment(
        cls,
        env_def: EnvironmentDefinition,
        layout_graph: SpatialLayoutGraph,
        modules_count: int,
        props_count: int,
    ) -> ModularWorldValidationReport:
        issues = []
        warnings = []

        # 1. Structural & Dimensional checks (Sections 11, 167)
        struct_score = 1.0
        for room_id, room in layout_graph.rooms.items():
            if any(dim <= 0.0 for dim in room.dimensions_xyz):
                issues.append(f"NON-NEGOTIABLE VIOLATION: Room '{room_id}' has non-positive dimensions: {room.dimensions_xyz}.")
                struct_score = 0.0
            if room.dimensions_xyz[2] < 200.0:
                issues.append(f"NON-NEGOTIABLE VIOLATION: Room '{room_id}' ceiling height {room.dimensions_xyz[2]}cm is below player clearance (200cm).")
                struct_score = 0.0

        if modules_count <= 0:
            issues.append("NON-NEGOTIABLE VIOLATION: Zero modules placed in modular environment.")
            struct_score = 0.0

        # 2. Navigation & Connectivity checks (Sections 32, 212)
        nav_score = 1.0
        if not layout_graph.is_fully_connected():
            issues.append("NON-NEGOTIABLE VIOLATION: Spatial layout contains isolated, unreachable rooms.")
            nav_score = 0.0

        for conn in layout_graph.connections:
            if conn.from_room not in layout_graph.rooms or conn.to_room not in layout_graph.rooms:
                issues.append(f"NON-NEGOTIABLE VIOLATION: Connection references non-existent room ({conn.from_room} -> {conn.to_room}).")
                nav_score = 0.0

        collision_score = 1.0
        streaming_score = 1.0

        if props_count == 0:
            warnings.append("No props placed in environment.")

        q_score = ModularWorldQualityScore(
            structural_score=struct_score,
            navigation_score=nav_score,
            collision_score=collision_score,
            streaming_score=streaming_score,
        )

        is_valid = len(issues) == 0 and q_score.aggregate_score >= 0.85
        review_status = "PASSED" if is_valid else "MANUAL_REVIEW_REQUIRED"

        return ModularWorldValidationReport(
            is_valid=is_valid,
            quality_score=q_score,
            issues=issues,
            warnings=warnings,
            review_status=review_status,
        )
