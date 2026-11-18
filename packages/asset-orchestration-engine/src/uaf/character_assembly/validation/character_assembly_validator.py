"""
CharacterAssemblyValidator enforces skeletal limits, bone counts, IK/retargeting compliance, and path purity.
UAF-81.42 Sections 17, 18, 20, 21, 137, 154, 155, 156, 158, 160.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from ..models.definition import CharacterAssemblySpecification


@dataclass
class CharacterAssemblyQualityScore:
    skeleton_score: float      # 0.0 to 1.0 (dimensions in [50, 450]cm, bone_count >= 20)
    ik_retarget_score: float   # 0.0 to 1.0 (has_ik_chains, has_retarget_profile)
    skin_physics_score: float  # 0.0 to 1.0 (has_ragdoll_physics)
    unreal_score: float        # 0.0 to 1.0 (valid skeletal mesh, anim blueprint, physics asset paths)

    @property
    def aggregate_score(self) -> float:
        return round(
            0.30 * self.skeleton_score +
            0.25 * self.ik_retarget_score +
            0.25 * self.skin_physics_score +
            0.20 * self.unreal_score,
            3
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "skeleton_score": self.skeleton_score,
            "ik_retarget_score": self.ik_retarget_score,
            "skin_physics_score": self.skin_physics_score,
            "unreal_score": self.unreal_score,
            "aggregate_score": self.aggregate_score,
        }


@dataclass
class CharacterAssemblyValidationReport:
    is_valid: bool
    quality_score: CharacterAssemblyQualityScore
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


class CharacterAssemblyValidator:
    """
    Enforces NON-NEGOTIABLE HARD FAIL CONDITIONS (Sections 17, 18, 137, 155, 158).
    """

    @classmethod
    def validate_character_assembly(
        cls,
        spec: CharacterAssemblySpecification,
        skeletal_mesh_path: str,
        anim_blueprint_path: str,
        physics_asset_path: str,
    ) -> CharacterAssemblyValidationReport:
        issues = []
        warnings = []

        # 1. Skeletal dimensions validation (Section 5, 137)
        skel_score = 1.0
        if not spec.dimensions.is_valid:
            issues.append(
                f"HARD FAIL CONDITION: INVALID_SKELETAL_DIMENSIONS: height={spec.dimensions.height_cm}cm "
                f"outside [50.0, 450.0] or non-positive limb spans."
            )
            skel_score = 0.0
        if spec.bone_count < 20:
            issues.append(f"HARD FAIL CONDITION: INVALID_BONE_COUNT: bone_count={spec.bone_count} < 20.")
            skel_score = 0.0

        # 2. IK & Retarget profile requirements (Section 30, 48, 158, 160)
        ik_score = 1.0
        if not spec.has_ik_chains:
            issues.append("HARD FAIL CONDITION: MISSING_IK_OR_RETARGET: IK chains required for character ground contact.")
            ik_score = 0.0
        if not spec.has_retarget_profile:
            issues.append("HARD FAIL CONDITION: MISSING_IK_OR_RETARGET: Retarget profile required for Unreal locomotion.")
            ik_score = 0.0

        # 3. Ragdoll physics requirement (Section 161)
        phys_score = 1.0
        if not spec.has_ragdoll_physics:
            issues.append("HARD FAIL CONDITION: MISSING_RAGDOLL: Character must declare ragdoll physics asset.")
            phys_score = 0.0

        # 4. Path purity check (Section 163)
        unreal_score = 1.0
        for p in [skeletal_mesh_path, anim_blueprint_path, physics_asset_path]:
            if ":\\" in p or ":/" in p:
                issues.append(f"HARD FAIL CONDITION: Absolute machine-dependent path detected: '{p}'.")
                unreal_score = 0.0

        q_score = CharacterAssemblyQualityScore(
            skeleton_score=skel_score,
            ik_retarget_score=ik_score,
            skin_physics_score=phys_score,
            unreal_score=unreal_score,
        )

        is_valid = len(issues) == 0 and q_score.aggregate_score >= 0.85
        review_status = "PASSED" if is_valid else "MANUAL_REVIEW_REQUIRED"

        return CharacterAssemblyValidationReport(
            is_valid=is_valid,
            quality_score=q_score,
            issues=issues,
            warnings=warnings,
            review_status=review_status,
        )
