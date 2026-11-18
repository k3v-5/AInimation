"""
AnimatedCharacterValidator enforces character runtime readiness, animation validity, and quality gates.
UAF-81.9 Sections 143, 144, 159, 160, 161.
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from ..models.clip import AnimationClip
from ..models.state_machine import AnimationBlueprintContract
from ..models.lod import AnimationLODProfile
from ...rigging.skeleton.skeleton_definition import CharacterSkeletonDefinition
from ...rigging.skinning.skinning_definition import SkinningDefinition
from ...rigging.physics.physics_asset import PhysicsAssetDefinition


class CharacterBuildState(str, Enum):
    SOURCE = "SOURCE"
    RIGGED = "RIGGED"
    SKINNED = "SKINNED"
    ANIMATABLE = "ANIMATABLE"
    VALIDATED = "VALIDATED"
    OPTIMIZED = "OPTIMIZED"
    RUNTIME_READY = "RUNTIME_READY"
    PUBLISHED = "PUBLISHED"
    REJECTED = "REJECTED"


@dataclass
class AnimatedCharacterQualityScore:
    geometry_score: float     # 0.0 to 1.0
    skeleton_score: float     # 0.0 to 1.0
    skin_score: float         # 0.0 to 1.0
    deformation_score: float  # 0.0 to 1.0
    animation_score: float    # 0.0 to 1.0
    physics_score: float      # 0.0 to 1.0
    runtime_score: float      # 0.0 to 1.0

    @property
    def aggregate_score(self) -> float:
        return round(
            0.15 * self.geometry_score +
            0.15 * self.skeleton_score +
            0.15 * self.skin_score +
            0.15 * self.deformation_score +
            0.15 * self.animation_score +
            0.10 * self.physics_score +
            0.15 * self.runtime_score,
            3
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "geometry_score": self.geometry_score,
            "skeleton_score": self.skeleton_score,
            "skin_score": self.skin_score,
            "deformation_score": self.deformation_score,
            "animation_score": self.animation_score,
            "physics_score": self.physics_score,
            "runtime_score": self.runtime_score,
            "aggregate_score": self.aggregate_score,
        }


@dataclass
class AnimatedCharacterQualityReport:
    is_valid: bool
    quality_score: AnimatedCharacterQualityScore
    build_state: CharacterBuildState
    issues: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    review_status: str = "PASSED"  # "PASSED", "MANUAL_REVIEW_REQUIRED"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "is_valid": self.is_valid,
            "build_state": self.build_state.value,
            "quality_score": self.quality_score.to_dict(),
            "issues": self.issues,
            "warnings": self.warnings,
            "review_status": self.review_status,
        }


class AnimatedCharacterValidator:
    """
    Automated gate ensuring character assets meet all rigging, skinning, and runtime requirements.
    Enforces NON-NEGOTIABLE RULE (Section 161).
    """
    @classmethod
    def validate_character(
        cls,
        has_mesh: bool,
        skeleton: Optional[CharacterSkeletonDefinition],
        skinning: Optional[SkinningDefinition],
        physics: Optional[PhysicsAssetDefinition] = None,
        animation_clips: Optional[List[AnimationClip]] = None,
        blueprint_contract: Optional[AnimationBlueprintContract] = None,
        min_quality_score: float = 0.75,
    ) -> AnimatedCharacterQualityReport:
        issues = []
        warnings = []

        # 1. Non-Negotiable Rule (Section 161): Must have Mesh + Skeleton + Skin
        geom_score = 1.0 if has_mesh else 0.0
        if not has_mesh:
            issues.append("Character has no render geometry.")

        skel_score = 1.0 if skeleton and skeleton.bone_count > 0 else 0.0
        if not skeleton or skeleton.bone_count == 0:
            issues.append("NON-NEGOTIABLE VIOLATION: Character lacks a structural Skeleton.")

        skin_score = 1.0 if skinning and skinning.vertex_count > 0 else 0.0
        if not skinning or skinning.vertex_count == 0:
            issues.append("NON-NEGOTIABLE VIOLATION: Character lacks Skinning weights.")

        # 2. Deformation verification
        deform_score = 1.0 if (skel_score > 0 and skin_score > 0) else 0.0

        # 3. Animation verification
        anim_score = 1.0
        if not animation_clips:
            warnings.append("No locomotion animation clips provided.")
            anim_score = 0.7

        # 4. Physics verification
        phys_score = 1.0 if physics and len(physics.bodies) > 0 else 0.5
        if not physics:
            warnings.append("No physics ragdoll asset assigned.")

        # 5. Runtime & Blueprint contract
        runtime_score = 1.0 if blueprint_contract else 0.8
        if not blueprint_contract:
            warnings.append("No Animation Blueprint contract defined.")

        q_score = AnimatedCharacterQualityScore(
            geometry_score=geom_score,
            skeleton_score=skel_score,
            skin_score=skin_score,
            deformation_score=deform_score,
            animation_score=anim_score,
            physics_score=phys_score,
            runtime_score=runtime_score,
        )

        is_valid = len(issues) == 0 and q_score.aggregate_score >= min_quality_score
        if is_valid:
            build_state = CharacterBuildState.RUNTIME_READY
            review_status = "PASSED"
        else:
            build_state = CharacterBuildState.REJECTED
            review_status = "MANUAL_REVIEW_REQUIRED"

        return AnimatedCharacterQualityReport(
            is_valid=is_valid,
            quality_score=q_score,
            build_state=build_state,
            issues=issues,
            warnings=warnings,
            review_status=review_status,
        )
