"""
ModularEnvironmentValidator enforces architectural dimensions, grid snapping, collision, navigation, and path purity.
UAF-81.47 Sections 144, 156, 157, 158, 160, 161, 162, 163, 164, 165.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from ..models.definition import ModularEnvironmentSpecification


@dataclass
class ModularEnvironmentQualityScore:
    dimensions_grid_score: float      # 0.0 to 1.0 (width, length > 0, height >= 3.0m, grid_snap >= 10cm)
    module_assembly_score: float      # 0.0 to 1.0 (module_count >= 1)
    navigation_gameplay_score: float  # 0.0 to 1.0 (collision, navigation, and gameplay anchors enabled)
    unreal_score: float               # 0.0 to 1.0 (valid level, nav, and collision paths)

    @property
    def aggregate_score(self) -> float:
        return round(
            0.30 * self.dimensions_grid_score +
            0.25 * self.module_assembly_score +
            0.25 * self.navigation_gameplay_score +
            0.20 * self.unreal_score,
            3
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "dimensions_grid_score": self.dimensions_grid_score,
            "module_assembly_score": self.module_assembly_score,
            "navigation_gameplay_score": self.navigation_gameplay_score,
            "unreal_score": self.unreal_score,
            "aggregate_score": self.aggregate_score,
        }


@dataclass
class ModularEnvironmentValidationReport:
    is_valid: bool
    quality_score: ModularEnvironmentQualityScore
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


class ModularEnvironmentValidator:
    """
    Enforces NON-NEGOTIABLE HARD FAIL CONDITIONS (Sections 144, 156, 157, 158, 161, 162, 163, 164, 165).
    """

    @classmethod
    def validate_modular_environment(
        cls,
        spec: ModularEnvironmentSpecification,
        level_asset_path: str,
        navmesh_path: str,
        collision_asset_path: str,
    ) -> ModularEnvironmentValidationReport:
        issues = []
        warnings = []

        # 1. Environment dimensions and grid snapping (Section 7, 8, 153, 154, 161)
        dim_score = 1.0
        if not spec.dimensions.is_valid:
            issues.append(
                f"HARD FAIL CONDITION: INVALID_DIMENSIONS: width={spec.dimensions.width_m}, "
                f"length={spec.dimensions.length_m}, height={spec.dimensions.height_m} must be positive with height >= 3.0m."
            )
            dim_score = 0.0
        if spec.grid_snap_cm < 10.0:
            issues.append(f"HARD FAIL CONDITION: INVALID_GRID_OR_MODULES: grid_snap_cm={spec.grid_snap_cm} < 10.0cm.")
            dim_score = 0.0

        # 2. Module count (Section 5, 144)
        mod_score = 1.0
        if spec.module_count < 1:
            issues.append(f"HARD FAIL CONDITION: INVALID_GRID_OR_MODULES: module_count={spec.module_count} < 1.")
            mod_score = 0.0

        # 3. Core subsystems: collision, navigation, gameplay anchors (Section 164, 165)
        nav_game_score = 1.0
        if not spec.has_collision:
            issues.append("HARD FAIL CONDITION: MISSING_CORE_SUBSYSTEMS: Modular collision generation is disabled.")
            nav_game_score = 0.0
        if not spec.has_navigation:
            issues.append("HARD FAIL CONDITION: MISSING_CORE_SUBSYSTEMS: Navigation metadata is missing.")
            nav_game_score = 0.0
        if not spec.has_gameplay_anchors:
            issues.append("HARD FAIL CONDITION: MISSING_CORE_SUBSYSTEMS: Gameplay anchors (spawns/objectives/covers) missing.")
            nav_game_score = 0.0

        # 4. Path purity check (Section 151)
        unreal_score = 1.0
        for p in [level_asset_path, navmesh_path, collision_asset_path]:
            if ":\\" in p or ":/" in p:
                issues.append(f"HARD FAIL CONDITION: Absolute machine-dependent path detected: '{p}'.")
                unreal_score = 0.0

        q_score = ModularEnvironmentQualityScore(
            dimensions_grid_score=dim_score,
            module_assembly_score=mod_score,
            navigation_gameplay_score=nav_game_score,
            unreal_score=unreal_score,
        )

        is_valid = len(issues) == 0 and q_score.aggregate_score >= 0.85
        review_status = "PASSED" if is_valid else "MANUAL_REVIEW_REQUIRED"

        return ModularEnvironmentValidationReport(
            is_valid=is_valid,
            quality_score=q_score,
            issues=issues,
            warnings=warnings,
            review_status=review_status,
        )
