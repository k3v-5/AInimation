"""
BuildingAssemblyValidator enforces scale limits, grid validation, connectivity, and path portability.
UAF-81.35 Sections 6, 10, 127, 137.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from ..models.definition import BuildingAssemblySpecification


@dataclass
class BuildingAssemblyQualityScore:
    grid_score: float          # 0.0 to 1.0 (cell_size_cm >= 50.0)
    scale_score: float         # 0.0 to 1.0 (room dimensions positive and height >= 240.0 cm)
    connectivity_score: float  # 0.0 to 1.0 (no isolated rooms when rooms count > 1)
    gameplay_score: float      # 0.0 to 1.0 (spawns >= 1, valid level asset reference)

    @property
    def aggregate_score(self) -> float:
        return round(
            0.25 * self.grid_score +
            0.25 * self.scale_score +
            0.25 * self.connectivity_score +
            0.25 * self.gameplay_score,
            3
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "grid_score": self.grid_score,
            "scale_score": self.scale_score,
            "connectivity_score": self.connectivity_score,
            "gameplay_score": self.gameplay_score,
            "aggregate_score": self.aggregate_score,
        }


@dataclass
class BuildingAssemblyValidationReport:
    is_valid: bool
    quality_score: BuildingAssemblyQualityScore
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


class BuildingAssemblyValidator:
    """
    Enforces NON-NEGOTIABLE HARD FAIL CONDITIONS (Section 127).
    """

    @classmethod
    def validate_building_assembly(
        cls,
        spec: BuildingAssemblySpecification,
        level_asset_path: str,
    ) -> BuildingAssemblyValidationReport:
        issues = []
        warnings = []

        # 1. Grid validation (Section 10, 127)
        grid_score = 1.0
        if not spec.is_valid_grid:
            issues.append(f"HARD FAIL CONDITION: INVALID_CELL_SIZE cell_size_cm {spec.cell_size_cm} < 50.0 cm.")
            grid_score = 0.0

        # 2. Scale validation (Section 6, 127)
        scale_score = 1.0
        for r in spec.rooms:
            if not r.is_valid_scale:
                issues.append(f"HARD FAIL CONDITION: INVALID_SCALE room '{r.room_id}' dimensions {r.dimensions_cm} invalid or height < 240.0 cm.")
                scale_score = 0.0

        # 3. Connectivity validation (Section 127)
        conn_score = 1.0
        if len(spec.rooms) > 1:
            for r in spec.rooms:
                if not r.connected_room_ids:
                    issues.append(f"HARD FAIL CONDITION: ISOLATED_REQUIRED_ROOM room '{r.room_id}' has no connected rooms.")
                    conn_score = 0.0

        # 4. Gameplay & Spawns check (Section 127)
        gameplay_score = 1.0
        if spec.spawn_points_count < 1:
            issues.append(f"HARD FAIL CONDITION: INVALID_SPAWN spawn_points_count {spec.spawn_points_count} < 1.")
            gameplay_score = 0.0

        # 5. Path purity check
        if ":\\" in level_asset_path or ":/" in level_asset_path:
            issues.append(f"HARD FAIL CONDITION: Absolute machine-dependent path detected: '{level_asset_path}'.")
            gameplay_score = 0.0

        q_score = BuildingAssemblyQualityScore(
            grid_score=grid_score,
            scale_score=scale_score,
            connectivity_score=conn_score,
            gameplay_score=gameplay_score,
        )

        is_valid = len(issues) == 0 and q_score.aggregate_score >= 0.85
        review_status = "PASSED" if is_valid else "MANUAL_REVIEW_REQUIRED"

        return BuildingAssemblyValidationReport(
            is_valid=is_valid,
            quality_score=q_score,
            issues=issues,
            warnings=warnings,
            review_status=review_status,
        )
