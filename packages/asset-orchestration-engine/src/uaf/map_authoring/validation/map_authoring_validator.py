"""
MapAuthoringValidator enforces physical map dimensions, grid snapping, collision, navigation, and path purity.
UAF-81.44 Sections 18, 19, 131, 147, 148, 149, 150, 151.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from ..models.definition import MapAuthoringSpecification


@dataclass
class MapAuthoringQualityScore:
    dimensions_grid_score: float       # 0.0 to 1.0 (width, length > 0, height >= 10m, cell_size >= 10cm)
    modular_connector_score: float     # 0.0 to 1.0 (modular_piece_count >= 1, streaming enabled)
    navigation_collision_score: float  # 0.0 to 1.0 (collision, navigation, lighting enabled)
    unreal_score: float                # 0.0 to 1.0 (valid level, partition, and navmesh paths)

    @property
    def aggregate_score(self) -> float:
        return round(
            0.30 * self.dimensions_grid_score +
            0.25 * self.modular_connector_score +
            0.25 * self.navigation_collision_score +
            0.20 * self.unreal_score,
            3
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "dimensions_grid_score": self.dimensions_grid_score,
            "modular_connector_score": self.modular_connector_score,
            "navigation_collision_score": self.navigation_collision_score,
            "unreal_score": self.unreal_score,
            "aggregate_score": self.aggregate_score,
        }


@dataclass
class MapAuthoringValidationReport:
    is_valid: bool
    quality_score: MapAuthoringQualityScore
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


class MapAuthoringValidator:
    """
    Enforces NON-NEGOTIABLE HARD FAIL CONDITIONS (Sections 131, 148, 149, 150, 151).
    """

    @classmethod
    def validate_map_authoring(
        cls,
        spec: MapAuthoringSpecification,
        level_asset_path: str,
        world_partition_path: str,
        navmesh_path: str,
    ) -> MapAuthoringValidationReport:
        issues = []
        warnings = []

        # 1. Map dimensions and grid validation (Section 4, 9, 149)
        dim_score = 1.0
        if not spec.dimensions.is_valid:
            issues.append(
                f"HARD FAIL CONDITION: INVALID_DIMENSIONS: width={spec.dimensions.width_m}, "
                f"length={spec.dimensions.length_m}, height={spec.dimensions.height_m} must be positive with height >= 10.0m."
            )
            dim_score = 0.0
        if spec.cell_size_cm < 10.0:
            issues.append(f"HARD FAIL CONDITION: INVALID_GRID_OR_PIECES: cell_size_cm={spec.cell_size_cm} < 10.0cm.")
            dim_score = 0.0

        # 2. Modular piece count and streaming (Section 13, 148)
        mod_score = 1.0
        if spec.modular_piece_count < 1:
            issues.append(f"HARD FAIL CONDITION: INVALID_GRID_OR_PIECES: modular_piece_count={spec.modular_piece_count} < 1.")
            mod_score = 0.0
        if not spec.has_streaming_partition:
            issues.append("HARD FAIL CONDITION: MISSING_STREAMING: World streaming partition is strictly required.")
            mod_score = 0.0

        # 3. Core subsystems: collision, navigation, lighting (Section 150, 151)
        sub_score = 1.0
        if not spec.has_collision:
            issues.append("HARD FAIL CONDITION: MISSING_CORE_SUBSYSTEMS: World collision generation is disabled.")
            sub_score = 0.0
        if not spec.has_navigation:
            issues.append("HARD FAIL CONDITION: MISSING_CORE_SUBSYSTEMS: AI navigation mesh is disabled.")
            sub_score = 0.0
        if not spec.has_lighting:
            issues.append("HARD FAIL CONDITION: MISSING_CORE_SUBSYSTEMS: World lighting setup is disabled.")
            sub_score = 0.0

        # 4. Path purity check (Section 130)
        unreal_score = 1.0
        for p in [level_asset_path, world_partition_path, navmesh_path]:
            if ":\\" in p or ":/" in p:
                issues.append(f"HARD FAIL CONDITION: Absolute machine-dependent path detected: '{p}'.")
                unreal_score = 0.0

        q_score = MapAuthoringQualityScore(
            dimensions_grid_score=dim_score,
            modular_connector_score=mod_score,
            navigation_collision_score=sub_score,
            unreal_score=unreal_score,
        )

        is_valid = len(issues) == 0 and q_score.aggregate_score >= 0.85
        review_status = "PASSED" if is_valid else "MANUAL_REVIEW_REQUIRED"

        return MapAuthoringValidationReport(
            is_valid=is_valid,
            quality_score=q_score,
            issues=issues,
            warnings=warnings,
            review_status=review_status,
        )
