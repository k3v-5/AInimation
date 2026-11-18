"""
ModularKitbashValidator enforces dimensional viability, grid snapping limits, socket presence, and path purity.
UAF-81.39 Sections 7, 8, 10, 23, 29, 30, 141.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from ..models.definition import ModularKitbashSpecification


@dataclass
class ModularKitbashQualityScore:
    dimensions_score: float  # 0.0 to 1.0 (width, depth, height > 0)
    socket_score: float      # 0.0 to 1.0 (socket_count >= 1)
    grid_score: float        # 0.0 to 1.0 (grid_snap_size >= 10.0 cm)
    unreal_score: float      # 0.0 to 1.0 (valid static mesh & blueprint paths)

    @property
    def aggregate_score(self) -> float:
        return round(
            0.30 * self.dimensions_score +
            0.25 * self.socket_score +
            0.25 * self.grid_score +
            0.20 * self.unreal_score,
            3
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "dimensions_score": self.dimensions_score,
            "socket_score": self.socket_score,
            "grid_score": self.grid_score,
            "unreal_score": self.unreal_score,
            "aggregate_score": self.aggregate_score,
        }


@dataclass
class ModularKitbashValidationReport:
    is_valid: bool
    quality_score: ModularKitbashQualityScore
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


class ModularKitbashValidator:
    """
    Enforces NON-NEGOTIABLE HARD FAIL CONDITIONS (Sections 7, 10, 23, 141).
    """

    @classmethod
    def validate_modular_kitbash(
        cls,
        spec: ModularKitbashSpecification,
        static_mesh_path: str,
        blueprint_path: str,
    ) -> ModularKitbashValidationReport:
        issues = []
        warnings = []

        # 1. Dimensional validity (Section 7, 141)
        dim_score = 1.0
        if not spec.dimensions.is_valid:
            issues.append(
                f"HARD FAIL CONDITION: INVALID_DIMENSIONS: "
                f"width={spec.dimensions.width_cm}, depth={spec.dimensions.depth_cm}, "
                f"height={spec.dimensions.height_cm} must be positive."
            )
            dim_score = 0.0

        # 2. Socket connectivity requirement (Section 16, 141)
        soc_score = 1.0
        if spec.socket_count < 1:
            issues.append(f"HARD FAIL CONDITION: ZERO_SOCKETS: socket_count={spec.socket_count} < 1.")
            soc_score = 0.0

        # 3. Grid snap validation (Section 10, 141)
        grid_score = 1.0
        if spec.grid_snap_size_cm < 10.0:
            issues.append(f"HARD FAIL CONDITION: INVALID_GRID_SNAP: grid_snap_size_cm={spec.grid_snap_size_cm} < 10.0 cm.")
            grid_score = 0.0

        # 4. Path purity check (Section 141)
        unreal_score = 1.0
        for p in [static_mesh_path, blueprint_path]:
            if ":\\" in p or ":/" in p:
                issues.append(f"HARD FAIL CONDITION: Absolute machine-dependent path detected: '{p}'.")
                unreal_score = 0.0

        q_score = ModularKitbashQualityScore(
            dimensions_score=dim_score,
            socket_score=soc_score,
            grid_score=grid_score,
            unreal_score=unreal_score,
        )

        is_valid = len(issues) == 0 and q_score.aggregate_score >= 0.85
        review_status = "PASSED" if is_valid else "MANUAL_REVIEW_REQUIRED"

        return ModularKitbashValidationReport(
            is_valid=is_valid,
            quality_score=q_score,
            issues=issues,
            warnings=warnings,
            review_status=review_status,
        )
