"""
RigValidator enforces human-level quality gates, weight normalization, and deformation integrity.
UAF-81.5 Sections 88, 89, 90, 101.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from ..skeleton.skeleton_definition import CharacterSkeletonDefinition
from ..skinning.skinning_definition import SkinningDefinition
from ..skinning.weight_normalizer import WeightNormalizer
from ..deformation.deformation_evaluator import DeformationEvaluator, DeformationScore


@dataclass
class RigValidationReport:
    is_valid: bool
    skeleton_issues: List[str] = field(default_factory=list)
    skinning_issues: List[str] = field(default_factory=list)
    deformation_issues: List[str] = field(default_factory=list)
    deformation_score: Optional[DeformationScore] = None
    quality_score: float = 1.0
    review_status: str = "PASSED"  # "PASSED", "MANUAL_REVIEW_REQUIRED"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "is_valid": self.is_valid,
            "skeleton_issues": self.skeleton_issues,
            "skinning_issues": self.skinning_issues,
            "deformation_issues": self.deformation_issues,
            "deformation_score": self.deformation_score.to_dict() if self.deformation_score else None,
            "quality_score": self.quality_score,
            "review_status": self.review_status,
        }


class RigValidator:
    """
    Automated gate ensuring characters meet animation, deformation, and engine export requirements.
    Enforces NON-NEGOTIABLE RULE (Section 101): Failures mark character as MANUAL_REVIEW_REQUIRED.
    """
    @classmethod
    def validate_rig_suite(
        cls,
        skeleton: CharacterSkeletonDefinition,
        skinning: SkinningDefinition,
        min_quality_score: float = 0.75,
    ) -> RigValidationReport:
        skel_issues = []
        skin_issues = []
        deform_issues = []

        # 1. Skeleton validation
        if not skeleton.bones:
            skel_issues.append("Skeleton has no bones.")
        elif skeleton.root_bone_id not in skeleton.bones:
            skel_issues.append(f"Root bone '{skeleton.root_bone_id}' does not exist in skeleton.")

        # Check for circular parenting in skeleton
        for b_id, b in skeleton.bones.items():
            visited = {b_id}
            curr = b.parent_id
            while curr:
                if curr in visited:
                    skel_issues.append(f"Circular bone hierarchy detected at '{b_id}' -> '{curr}'.")
                    break
                visited.add(curr)
                parent_bone = skeleton.get_bone(curr)
                curr = parent_bone.parent_id if parent_bone else None

        # 2. Skinning validation
        is_skin_valid, skin_errs = WeightNormalizer.validate_skinning(skinning)
        skin_issues.extend(skin_errs)

        # 3. Deformation evaluation
        deform_score = DeformationEvaluator.evaluate_deformation(skeleton, skinning)
        if deform_score.aggregate_score < 0.6:
            deform_issues.append(
                f"Deformation score {deform_score.aggregate_score} is below minimum acceptable threshold 0.60."
            )
        if deform_score.failed_poses:
            deform_issues.append(f"Failed stress poses: {', '.join(deform_score.failed_poses)}.")

        # Calculate combined quality score (Section 90)
        # Skeleton: 0.35, Skinning: 0.35, Deformation: 0.30
        skel_factor = 1.0 if not skel_issues else 0.0
        skin_factor = 1.0 if not skin_issues else max(0.0, 1.0 - (len(skin_issues) * 0.1))
        deform_factor = deform_score.aggregate_score

        overall_quality = round(0.35 * skel_factor + 0.35 * skin_factor + 0.30 * deform_factor, 3)

        is_valid = (len(skel_issues) == 0) and (len(skin_issues) == 0) and (overall_quality >= min_quality_score)
        review_status = "PASSED" if is_valid else "MANUAL_REVIEW_REQUIRED"

        return RigValidationReport(
            is_valid=is_valid,
            skeleton_issues=skel_issues,
            skinning_issues=skin_issues,
            deformation_issues=deform_issues,
            deformation_score=deform_score,
            quality_score=overall_quality,
            review_status=review_status,
        )
