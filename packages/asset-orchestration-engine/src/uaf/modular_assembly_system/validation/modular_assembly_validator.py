"""
ModularAssemblyValidator enforces physical clearances, modular grid consistency, spatial subsystems, and path purity.
UAF-81.50 Sections 148, 157, 158, 161.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from ..models.definition import ModularAssemblySpecification


@dataclass
class ModularAssemblyQualityScore:
    dimensions_grid_score: float        # 0.0 to 1.0 (width, length > 0, height >= 3m, grid_snap >= 10cm)
    modular_connectivity_score: float  # 0.0 to 1.0 (module_count >= 1, collision & lighting enabled)
    navigation_partition_score: float  # 0.0 to 1.0 (navigation & world partition enabled)
    unreal_score: float                # 0.0 to 1.0 (valid level, partition, and nav paths)

    @property
    def aggregate_score(self) -> float:
        return round(
            0.30 * self.dimensions_grid_score +
            0.25 * self.modular_connectivity_score +
            0.25 * self.navigation_partition_score +
            0.20 * self.unreal_score,
            3
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "dimensions_grid_score": self.dimensions_grid_score,
            "modular_connectivity_score": self.modular_connectivity_score,
            "navigation_partition_score": self.navigation_partition_score,
            "unreal_score": self.unreal_score,
            "aggregate_score": self.aggregate_score,
        }


@dataclass
class ModularAssemblyValidationReport:
    is_valid: bool
    quality_score: ModularAssemblyQualityScore
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


class ModularAssemblyValidator:
    """
    Enforces NON-NEGOTIABLE HARD FAIL CONDITIONS (Sections 148, 157, 158, 161).
    """

    @classmethod
    def validate_modular_assembly(
        cls,
        spec: ModularAssemblySpecification,
        level_asset_path: str,
        world_partition_path: str,
        navmesh_path: str,
    ) -> ModularAssemblyValidationReport:
        issues = []
        warnings = []

        # 1. Dimensions and grid snap (Section 8, 148, 161)
        dim_grid_score = 1.0
        if not spec.dimensions.is_valid:
            issues.append(
                f"HARD FAIL CONDITION: INVALID_ASSEMBLY_DIMENSIONS: width={spec.dimensions.width_m}, "
                f"length={spec.dimensions.length_m}, height={spec.dimensions.height_m} (height must be >= 3.0m)."
            )
            dim_grid_score = 0.0
        if spec.grid_snap_cm < 10.0:
            issues.append(f"HARD FAIL CONDITION: INVALID_GRID_OR_MODULES: grid_snap_cm={spec.grid_snap_cm} < 10.0cm.")
            dim_grid_score = 0.0

        # 2. Modular count and structural components (Section 12, 148, 161)
        mod_conn_score = 1.0
        if spec.module_count < 1:
            issues.append(f"HARD FAIL CONDITION: INVALID_GRID_OR_MODULES: module_count={spec.module_count} < 1.")
            mod_conn_score = 0.0
        if not spec.has_collision:
            issues.append("HARD FAIL CONDITION: MISSING_CORE_SUBSYSTEMS: Collision architecture is disabled.")
            mod_conn_score = 0.0
        if not spec.has_lighting:
            issues.append("HARD FAIL CONDITION: MISSING_CORE_SUBSYSTEMS: Lighting setup is disabled.")
            mod_conn_score = 0.0

        # 3. Navigation and World Partition (Section 71, 75, 142, 144)
        nav_part_score = 1.0
        if not spec.has_navigation:
            issues.append("HARD FAIL CONDITION: MISSING_CORE_SUBSYSTEMS: Navigation metadata is disabled.")
            nav_part_score = 0.0
        if not spec.has_world_partition:
            issues.append("HARD FAIL CONDITION: MISSING_CORE_SUBSYSTEMS: World partition streaming is disabled.")
            nav_part_score = 0.0

        # 4. Path purity check (Section 153)
        unreal_score = 1.0
        for p in [level_asset_path, world_partition_path, navmesh_path]:
            if ":\\" in p or ":/" in p:
                issues.append(f"HARD FAIL CONDITION: Absolute machine-dependent path detected: '{p}'.")
                unreal_score = 0.0

        q_score = ModularAssemblyQualityScore(
            dimensions_grid_score=dim_grid_score,
            modular_connectivity_score=mod_conn_score,
            navigation_partition_score=nav_part_score,
            unreal_score=unreal_score,
        )

        is_valid = len(issues) == 0 and q_score.aggregate_score >= 0.85
        review_status = "PASSED" if is_valid else "MANUAL_REVIEW_REQUIRED"

        return ModularAssemblyValidationReport(
            is_valid=is_valid,
            quality_score=q_score,
            issues=issues,
            warnings=warnings,
            review_status=review_status,
        )
