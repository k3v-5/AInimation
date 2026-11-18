"""
CharacterOrganicValidator enforces realistic physical proportions, mesh clearance to avoid clothing penetration, and path purity.
UAF-81.26 Sections 6, 114, 129, 135.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from ..models.definition import OrganicCharacterDefinition


@dataclass
class CharacterOrganicQualityScore:
    proportions_score: float         # 0.0 to 1.0 (Height in bounds, ratios realistic)
    clothing_clearance_score: float  # 0.0 to 1.0 (No penetration, clearance >= 0.5mm)
    skeleton_score: float            # 0.0 to 1.0 (Valid skeleton reference)
    lod_score: float                 # 0.0 to 1.0 (Adequate LOD count >= 3)

    @property
    def aggregate_score(self) -> float:
        return round(
            0.30 * self.proportions_score +
            0.30 * self.clothing_clearance_score +
            0.20 * self.skeleton_score +
            0.20 * self.lod_score,
            3
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "proportions_score": self.proportions_score,
            "clothing_clearance_score": self.clothing_clearance_score,
            "skeleton_score": self.skeleton_score,
            "lod_score": self.lod_score,
            "aggregate_score": self.aggregate_score,
        }


@dataclass
class CharacterOrganicValidationReport:
    is_valid: bool
    quality_score: CharacterOrganicQualityScore
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


class CharacterOrganicValidator:
    """
    Enforces NON-NEGOTIABLE REQUIREMENTS (Sections 6, 114, 129, 135).
    """

    MIN_CLEARANCE_MM = 0.5

    @classmethod
    def validate_character(
        cls,
        character_def: OrganicCharacterDefinition,
        skeletal_mesh_ref: str,
        skeleton_ref: str,
        lod_count: int,
    ) -> CharacterOrganicValidationReport:
        issues = []
        warnings = []

        # 1. Proportions validation (Section 6 & 114)
        prop_score = 1.0
        if not character_def.proportions.is_valid:
            issues.append(f"NON-NEGOTIABLE VIOLATION: Character height {character_def.proportions.height_cm} cm is out of realistic physical bounds [50.0, 400.0] cm.")
            prop_score = 0.0

        # 2. Clothing clearance and penetration check (Section 114 & 135)
        cloth_score = 1.0
        for item in character_def.clothing_layers:
            if item.clearance_mm < cls.MIN_CLEARANCE_MM:
                issues.append(f"NON-NEGOTIABLE VIOLATION: Clothing item '{item.item_id}' clearance {item.clearance_mm}mm < {cls.MIN_CLEARANCE_MM}mm causes mesh penetration/clipping.")
                cloth_score = 0.0

        # 3. Skeleton reference & path purity (Section 129)
        skel_score = 1.0
        for ref in [skeletal_mesh_ref, skeleton_ref]:
            if ":\\" in ref or ":/" in ref or ref.startswith("/"):
                issues.append(f"NON-NEGOTIABLE VIOLATION: Absolute machine-dependent path in asset reference: '{ref}'.")
                skel_score = 0.0

        # 4. LOD validation
        lod_score = 1.0 if lod_count >= 3 else 0.5
        if lod_count < 3:
            warnings.append(f"Character declares only {lod_count} LOD levels (recommended >= 3).")

        q_score = CharacterOrganicQualityScore(
            proportions_score=prop_score,
            clothing_clearance_score=cloth_score,
            skeleton_score=skel_score,
            lod_score=lod_score,
        )

        is_valid = len(issues) == 0 and q_score.aggregate_score >= 0.85
        review_status = "PASSED" if is_valid else "MANUAL_REVIEW_REQUIRED"

        return CharacterOrganicValidationReport(
            is_valid=is_valid,
            quality_score=q_score,
            issues=issues,
            warnings=warnings,
            review_status=review_status,
        )
