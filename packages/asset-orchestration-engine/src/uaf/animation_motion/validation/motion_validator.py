"""
AnimationMotionValidator enforces acyclic skeletons, single root, positive motion durations, and relative references.
UAF-81.23 Sections 5, 34, 99, 117, 122.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from ..models.skeleton import CharacterRigDefinition
from ..models.motion import MotionClip


@dataclass
class AnimationMotionQualityScore:
    skeleton_score: float  # 0.0 to 1.0 (Single root, hierarchy integrity, acyclic)
    skinning_score: float  # 0.0 to 1.0 (Deform bones ratio, weights)
    ik_score: float        # 0.0 to 1.0 (Limb joints presence for IK)
    motion_score: float    # 0.0 to 1.0 (Clips validity, durations)

    @property
    def aggregate_score(self) -> float:
        return round(
            0.35 * self.skeleton_score +
            0.25 * self.skinning_score +
            0.20 * self.ik_score +
            0.20 * self.motion_score,
            3
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "skeleton_score": self.skeleton_score,
            "skinning_score": self.skinning_score,
            "ik_score": self.ik_score,
            "motion_score": self.motion_score,
            "aggregate_score": self.aggregate_score,
        }


@dataclass
class AnimationMotionValidationReport:
    is_valid: bool
    quality_score: AnimationMotionQualityScore
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


class AnimationMotionValidator:
    """
    Enforces NON-NEGOTIABLE REQUIREMENTS (Sections 5, 99, 117, 122).
    """

    @classmethod
    def validate_rig_and_motion(
        cls,
        rig_def: CharacterRigDefinition,
        clips: List[MotionClip],
        physics_asset_ref: str,
        control_rig_ref: str,
    ) -> AnimationMotionValidationReport:
        issues = []
        warnings = []

        # 1. Skeleton hierarchy checks (Section 5 & 122)
        skel = rig_def.skeleton
        skel_score = 1.0

        if not skel.bones:
            issues.append("NON-NEGOTIABLE VIOLATION: Zero bones declared in skeleton hierarchy.")
            skel_score = 0.0
        else:
            root_bone = skel.find_root()
            if not root_bone:
                issues.append("NON-NEGOTIABLE VIOLATION: Skeleton does not have exactly one unique root bone.")
                skel_score = 0.0
            if skel.has_cycles():
                issues.append("NON-NEGOTIABLE VIOLATION: Cycle detected in skeleton bone hierarchy.")
                skel_score = 0.0

        # 2. Skinning deform bones check
        deform_count = sum(1 for b in skel.bones.values() if b.is_deform)
        skinning_score = 1.0 if deform_count >= 10 else 0.8

        # 3. IK & Limbs presence
        ik_score = 1.0 if any(b.role.value == "LIMB_UPPER" for b in skel.bones.values()) else 0.7

        # 4. Motion clips checks (Section 99)
        motion_score = 1.0
        if not clips:
            issues.append("NON-NEGOTIABLE VIOLATION: Zero motion clips provided for animated character.")
            motion_score = 0.0
        for clip in clips:
            if clip.duration_seconds <= 0.0:
                issues.append(f"NON-NEGOTIABLE VIOLATION: Clip '{clip.clip_id}' has non-positive duration: {clip.duration_seconds}s.")
                motion_score = 0.0

        # 5. Path purity check (Section 117)
        for ref in [physics_asset_ref, control_rig_ref]:
            if ":\\" in ref or ":/" in ref or ref.startswith("/"):
                issues.append(f"NON-NEGOTIABLE VIOLATION: Absolute machine-dependent reference path: '{ref}'.")
                skel_score = 0.0

        q_score = AnimationMotionQualityScore(
            skeleton_score=skel_score,
            skinning_score=skinning_score,
            ik_score=ik_score,
            motion_score=motion_score,
        )

        is_valid = len(issues) == 0 and q_score.aggregate_score >= 0.85
        review_status = "PASSED" if is_valid else "MANUAL_REVIEW_REQUIRED"

        return AnimationMotionValidationReport(
            is_valid=is_valid,
            quality_score=q_score,
            issues=issues,
            warnings=warnings,
            review_status=review_status,
        )
