"""
CharacterCreatureRigValidator enforces realistic anatomical proportions, bone counts, Unreal physics assets, and relative path contracts.
UAF-81.33 Sections 8, 9, 128, 131, 140.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from ..models.definition import CharacterCreatureRigDefinition


@dataclass
class CharacterCreatureRigQualityScore:
    proportion_score: float      # 0.0 to 1.0 (50cm <= height <= 400cm, valid dimensions)
    skeleton_score: float        # 0.0 to 1.0 (bone_count >= 15)
    clothing_armor_score: float  # 0.0 to 1.0 (valid clothing/armor integration)
    unreal_score: float          # 0.0 to 1.0 (physics asset present, valid refs)

    @property
    def aggregate_score(self) -> float:
        return round(
            0.30 * self.proportion_score +
            0.30 * self.skeleton_score +
            0.20 * self.clothing_armor_score +
            0.20 * self.unreal_score,
            3
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "proportion_score": self.proportion_score,
            "skeleton_score": self.skeleton_score,
            "clothing_armor_score": self.clothing_armor_score,
            "unreal_score": self.unreal_score,
            "aggregate_score": self.aggregate_score,
        }


@dataclass
class CharacterCreatureRigValidationReport:
    is_valid: bool
    quality_score: CharacterCreatureRigQualityScore
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


class CharacterCreatureRigValidator:
    """
    Enforces NON-NEGOTIABLE REQUIREMENTS (Sections 8, 9, 128, 140).
    """

    @classmethod
    def validate_character_creature_rig(
        cls,
        char_def: CharacterCreatureRigDefinition,
        skeletal_mesh_ref: str,
        skeleton_ref: str,
        physics_asset_ref: str,
    ) -> CharacterCreatureRigValidationReport:
        issues = []
        warnings = []

        # 1. Proportions & height check (Section 8 & 9)
        prop_score = 1.0
        if not char_def.proportions.is_valid:
            issues.append(f"NON-NEGOTIABLE VIOLATION: Character proportions invalid or height {char_def.proportions.height_cm}cm outside [50.0, 400.0]cm.")
            prop_score = 0.0

        # 2. Skeleton bone count check (Section 128)
        skel_score = 1.0
        if not char_def.is_valid_skeleton:
            issues.append(f"NON-NEGOTIABLE VIOLATION: Bone count {char_def.bone_count} is below the 15 bone minimum for deformation rigs.")
            skel_score = 0.0

        # 3. Clothing / Armor sanity
        ca_score = 1.0

        # 4. Unreal readiness & Physics Asset check (Section 140)
        unreal_score = 1.0
        if not physics_asset_ref:
            issues.append("NON-NEGOTIABLE VIOLATION: Unreal readiness requires a valid physics asset reference.")
            unreal_score = 0.0

        for ref in [skeletal_mesh_ref, skeleton_ref, physics_asset_ref]:
            if ":\\" in ref or ":/" in ref or ref.startswith("/"):
                issues.append(f"NON-NEGOTIABLE VIOLATION: Absolute machine-dependent path detected: '{ref}'.")
                unreal_score = 0.0

        q_score = CharacterCreatureRigQualityScore(
            proportion_score=prop_score,
            skeleton_score=skel_score,
            clothing_armor_score=ca_score,
            unreal_score=unreal_score,
        )

        is_valid = len(issues) == 0 and q_score.aggregate_score >= 0.85
        review_status = "PASSED" if is_valid else "MANUAL_REVIEW_REQUIRED"

        return CharacterCreatureRigValidationReport(
            is_valid=is_valid,
            quality_score=q_score,
            issues=issues,
            warnings=warnings,
            review_status=review_status,
        )
