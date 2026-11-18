"""
CharacterPipelineValidator enforces proportion ranges, bone hierarchies, physics asset presence, and path purity.
UAF-81.37 Sections 7, 30, 32, 133, 151, 152, 153.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from ..models.definition import CharacterProductionSpecification


@dataclass
class CharacterPipelineQualityScore:
    proportion_score: float      # 0.0 to 1.0 (height in [50.0, 450.0], limbs > 0)
    skeleton_score: float        # 0.0 to 1.0 (bone_count >= 15)
    rig_physics_score: float     # 0.0 to 1.0 (has_physics_asset is True)
    gameplay_unreal_score: float # 0.0 to 1.0 (valid skeletal mesh & physics paths)

    @property
    def aggregate_score(self) -> float:
        return round(
            0.30 * self.proportion_score +
            0.25 * self.skeleton_score +
            0.25 * self.rig_physics_score +
            0.20 * self.gameplay_unreal_score,
            3
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "proportion_score": self.proportion_score,
            "skeleton_score": self.skeleton_score,
            "rig_physics_score": self.rig_physics_score,
            "gameplay_unreal_score": self.gameplay_unreal_score,
            "aggregate_score": self.aggregate_score,
        }


@dataclass
class CharacterPipelineValidationReport:
    is_valid: bool
    quality_score: CharacterPipelineQualityScore
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


class CharacterPipelineValidator:
    """
    Enforces NON-NEGOTIABLE HARD FAIL CONDITIONS (Sections 7, 133, 151, 153).
    """

    @classmethod
    def validate_character_pipeline(
        cls,
        spec: CharacterProductionSpecification,
        skeletal_mesh_path: str,
        physics_asset_path: str,
    ) -> CharacterPipelineValidationReport:
        issues = []
        warnings = []

        # 1. Proportion validation (Section 7, 133)
        prop_score = 1.0
        if not spec.proportions.is_valid:
            issues.append(
                f"HARD FAIL CONDITION: INVALID_PROPORTIONS height {spec.proportions.height_cm}cm outside [50.0, 450.0] "
                f"or non-positive limb dimensions."
            )
            prop_score = 0.0

        # 2. Skeleton bone count validation (Section 11, 133)
        skel_score = 1.0
        if spec.bone_count < 15:
            issues.append(f"HARD FAIL CONDITION: INVALID_BONE_COUNT bone_count {spec.bone_count} < 15.")
            skel_score = 0.0

        # 3. Physics asset validation (Section 133, 153)
        phys_score = 1.0
        if not spec.has_physics_asset:
            issues.append("HARD FAIL CONDITION: MISSING_PHYSICS_ASSET physics asset must be present for Unreal ragdoll readiness.")
            phys_score = 0.0

        # 4. Path purity check (Section 133)
        gp_score = 1.0
        for path_ref in [skeletal_mesh_path, physics_asset_path]:
            if ":\\" in path_ref or ":/" in path_ref:
                issues.append(f"HARD FAIL CONDITION: Absolute machine-dependent path detected: '{path_ref}'.")
                gp_score = 0.0

        q_score = CharacterPipelineQualityScore(
            proportion_score=prop_score,
            skeleton_score=skel_score,
            rig_physics_score=phys_score,
            gameplay_unreal_score=gp_score,
        )

        is_valid = len(issues) == 0 and q_score.aggregate_score >= 0.85
        review_status = "PASSED" if is_valid else "MANUAL_REVIEW_REQUIRED"

        return CharacterPipelineValidationReport(
            is_valid=is_valid,
            quality_score=q_score,
            issues=issues,
            warnings=warnings,
            review_status=review_status,
        )
