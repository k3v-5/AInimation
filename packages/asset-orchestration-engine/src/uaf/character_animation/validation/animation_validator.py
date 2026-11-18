"""
CharacterAnimationValidator enforces skeletal hierarchy, weight normalization, and canonical clip coverage.
UAF-81.17 Sections 14, 15, 39, 214, 215, 217.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from ..models.skeleton import SkeletonHierarchy
from ..models.ik import IKChain
from ..models.skinning import SkinningWeightData
from ...animation.models.clip import AnimationClip


@dataclass
class CharacterAnimationQualityScore:
    skeleton_score: float   # 0.0 to 1.0 (Hierarchy, cycles, root)
    skin_score: float       # 0.0 to 1.0 (Normalized weights, no unweighted verts)
    ik_score: float         # 0.0 to 1.0 (IK chains defined)
    animation_score: float  # 0.0 to 1.0 (5 canonical clips present)
    physics_score: float    # 0.0 to 1.0 (Ragdoll bodies)

    @property
    def aggregate_score(self) -> float:
        return round(
            0.25 * self.skeleton_score +
            0.25 * self.skin_score +
            0.15 * self.ik_score +
            0.20 * self.animation_score +
            0.15 * self.physics_score,
            3
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "skeleton_score": self.skeleton_score,
            "skin_score": self.skin_score,
            "ik_score": self.ik_score,
            "animation_score": self.animation_score,
            "physics_score": self.physics_score,
            "aggregate_score": self.aggregate_score,
        }


@dataclass
class CharacterAnimationValidationReport:
    is_valid: bool
    quality_score: CharacterAnimationQualityScore
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


class CharacterAnimationValidator:
    """
    Enforces NON-NEGOTIABLE REQUIREMENTS (Sections 14, 15, 39, 215, 217).
    """

    REQUIRED_CANONICAL_CLIPS = {"IDLE", "WALK", "RUN", "ATTACK", "DEATH"}

    @classmethod
    def validate_animation_suite(
        cls,
        skeleton: SkeletonHierarchy,
        ik_chains: List[IKChain],
        skinning: SkinningWeightData,
        clips: Dict[str, AnimationClip],
        physics_bodies: List[str],
    ) -> CharacterAnimationValidationReport:
        issues = []
        warnings = []

        # 1. Skeleton integrity (Sections 14, 15)
        skel_score = 1.0
        if skeleton.has_cycles():
            issues.append("NON-NEGOTIABLE VIOLATION: Skeleton hierarchy contains cyclic parenting.")
            skel_score = 0.0
        if skeleton.root_bone not in skeleton.bones:
            issues.append(f"NON-NEGOTIABLE VIOLATION: Skeleton root bone '{skeleton.root_bone}' not defined in bones.")
            skel_score = 0.0

        # 2. Skinning normalization & unweighted verts (Section 39, 215)
        skin_score = 1.0
        if not skinning.weights_sum_normalized:
            issues.append("NON-NEGOTIABLE VIOLATION: Vertex skinning weights are not normalized to 1.0.")
            skin_score = 0.0
        if skinning.unweighted_vertices_count > 0:
            issues.append(f"NON-NEGOTIABLE VIOLATION: Mesh contains {skinning.unweighted_vertices_count} unweighted vertices.")
            skin_score = 0.0

        # 3. Canonical animation clips (Section 217)
        anim_score = 1.0
        missing_clips = cls.REQUIRED_CANONICAL_CLIPS - set(clips.keys())
        if missing_clips:
            issues.append(f"NON-NEGOTIABLE VIOLATION: Missing required canonical animation clips: {missing_clips}.")
            anim_score = 0.0

        ik_score = 1.0 if ik_chains else 0.5
        if not ik_chains:
            warnings.append("No IK solver chains configured for character.")

        phys_score = 1.0 if physics_bodies else 0.5
        if not physics_bodies:
            warnings.append("No physics ragdoll collision bodies defined.")

        q_score = CharacterAnimationQualityScore(
            skeleton_score=skel_score,
            skin_score=skin_score,
            ik_score=ik_score,
            animation_score=anim_score,
            physics_score=phys_score,
        )

        is_valid = len(issues) == 0 and q_score.aggregate_score >= 0.85
        review_status = "PASSED" if is_valid else "MANUAL_REVIEW_REQUIRED"

        return CharacterAnimationValidationReport(
            is_valid=is_valid,
            quality_score=q_score,
            issues=issues,
            warnings=warnings,
            review_status=review_status,
        )
