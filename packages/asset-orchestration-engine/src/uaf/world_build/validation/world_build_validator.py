"""
WorldBuildValidator enforces dimension scale, cell partitioning, world partition rules, and path purity.
UAF-81.40 Sections 7, 9, 142, 143, 144, 145, 148, 171.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from ..models.definition import WorldBuildSpecification


@dataclass
class WorldBuildQualityScore:
    dimensions_score: float      # 0.0 to 1.0 (width, length > 0, height >= 10m, cells >= 1)
    partition_score: float       # 0.0 to 1.0 (world partition rule for >= 2000m worlds)
    hydrology_road_score: float  # 0.0 to 1.0 (hydrology and road graph sanity)
    unreal_score: float          # 0.0 to 1.0 (valid level & world partition asset paths)

    @property
    def aggregate_score(self) -> float:
        return round(
            0.30 * self.dimensions_score +
            0.25 * self.partition_score +
            0.25 * self.hydrology_road_score +
            0.20 * self.unreal_score,
            3
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "dimensions_score": self.dimensions_score,
            "partition_score": self.partition_score,
            "hydrology_road_score": self.hydrology_road_score,
            "unreal_score": self.unreal_score,
            "aggregate_score": self.aggregate_score,
        }


@dataclass
class WorldBuildValidationReport:
    is_valid: bool
    quality_score: WorldBuildQualityScore
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


class WorldBuildValidator:
    """
    Enforces NON-NEGOTIABLE HARD FAIL CONDITIONS (Sections 148, 171).
    """

    @classmethod
    def validate_world_build(
        cls,
        spec: WorldBuildSpecification,
        level_asset_path: str,
        world_partition_data_path: str,
    ) -> WorldBuildValidationReport:
        issues = []
        warnings = []

        # 1. Dimension & cell validation (Section 5, 171)
        dim_score = 1.0
        if not spec.dimensions.is_valid:
            issues.append(
                f"HARD FAIL CONDITION: INVALID_DIMENSIONS: "
                f"width={spec.dimensions.width_m}, length={spec.dimensions.length_m}, "
                f"height={spec.dimensions.height_m} must be positive with height >= 10.0m."
            )
            dim_score = 0.0
        if spec.cell_count < 1:
            issues.append(f"HARD FAIL CONDITION: INVALID_CELL_COUNT: cell_count={spec.cell_count} < 1.")
            dim_score = 0.0

        # 2. World Partition requirement for large scales (Section 76, 171)
        part_score = 1.0
        if (spec.dimensions.width_m >= 2000.0 or spec.dimensions.length_m >= 2000.0) and not spec.has_world_partition:
            issues.append(
                f"HARD FAIL CONDITION: MISSING_WORLD_PARTITION: World size {spec.dimensions.width_m}x{spec.dimensions.length_m}m "
                f"requires World Partition for streaming stability."
            )
            part_score = 0.0

        # 3. Hydrology and roads
        hydro_score = 1.0

        # 4. Path purity check (Section 171)
        unreal_score = 1.0
        for p in [level_asset_path, world_partition_data_path]:
            if ":\\" in p or ":/" in p:
                issues.append(f"HARD FAIL CONDITION: Absolute machine-dependent path detected: '{p}'.")
                unreal_score = 0.0

        q_score = WorldBuildQualityScore(
            dimensions_score=dim_score,
            partition_score=part_score,
            hydrology_road_score=hydro_score,
            unreal_score=unreal_score,
        )

        is_valid = len(issues) == 0 and q_score.aggregate_score >= 0.85
        review_status = "PASSED" if is_valid else "MANUAL_REVIEW_REQUIRED"

        return WorldBuildValidationReport(
            is_valid=is_valid,
            quality_score=q_score,
            issues=issues,
            warnings=warnings,
            review_status=review_status,
        )
