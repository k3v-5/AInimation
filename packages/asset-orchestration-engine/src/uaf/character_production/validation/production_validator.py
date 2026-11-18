"""
CharacterProductionValidator enforces realistic anatomy, sufficient bone hierarchy, physics assets, and path portability.
UAF-81.29 Sections 2, 6, 120, 121, 122, 134, 135.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from ..models.definition import ProductionCharacterDefinition


@dataclass
class CharacterProductionQualityScore:
    geometry_score: float  # 0.0 to 1.0 (Height in bounds, proportions realistic)
    rig_score: float       # 0.0 to 1.0 (Bone count >= 15, valid skeleton reference)
    skinning_score: float  # 0.0 to 1.0 (Valid physics asset, deformation readiness)
    lod_score: float       # 0.0 to 1.0 (LOD count >= 3)

    @property
    def aggregate_score(self) -> float:
        return round(
            0.25 * self.geometry_score +
            0.30 * self.rig_score +
            0.25 * self.skinning_score +
            0.20 * self.lod_score,
            3
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "geometry_score": self.geometry_score,
            "rig_score": self.rig_score,
            "skinning_score": self.skinning_score,
            "lod_score": self.lod_score,
            "aggregate_score": self.aggregate_score,
        }


@dataclass
class CharacterProductionValidationReport:
    is_valid: bool
    quality_score: CharacterProductionQualityScore
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


class CharacterProductionValidator:
    """
    Enforces NON-NEGOTIABLE REQUIREMENTS (Sections 2, 6, 134, 135).
    """

    MIN_BONE_COUNT = 15

    @classmethod
    def validate_production_character(
        cls,
        char_def: ProductionCharacterDefinition,
        skeletal_mesh_ref: str,
        skeleton_ref: str,
        physics_asset_ref: str,
        lod_count: int,
    ) -> CharacterProductionValidationReport:
        issues = []
        warnings = []

        # 1. Proportions & height check (Section 6 & 135)
        geo_score = 1.0
        if not char_def.proportions.is_valid:
            issues.append(f"NON-NEGOTIABLE VIOLATION: Character height {char_def.proportions.height_cm}cm is outside realistic physical bounds [50.0, 400.0]cm.")
            geo_score = 0.0

        # 2. Rig & bone count check (Section 135)
        rig_score = 1.0
        if char_def.bone_count < cls.MIN_BONE_COUNT:
            issues.append(f"NON-NEGOTIABLE VIOLATION: Character bone count {char_def.bone_count} < minimum required {cls.MIN_BONE_COUNT}.")
            rig_score = 0.0

        # 3. Skinning & physics asset check (Section 2 & 135)
        skin_score = 1.0
        if not physics_asset_ref:
            issues.append("NON-NEGOTIABLE VIOLATION: Character lacks PhysicsAsset reference required for UNREAL_READY status.")
            skin_score = 0.0

        # 4. LOD checks
        lod_score = 1.0 if lod_count >= 3 else 0.5
        if lod_count < 3:
            warnings.append(f"Character declares only {lod_count} LOD levels (minimum 3 recommended).")

        # 5. Path purity check (Section 135)
        for ref in [skeletal_mesh_ref, skeleton_ref, physics_asset_ref]:
            if ":\\" in ref or ":/" in ref or ref.startswith("/"):
                issues.append(f"NON-NEGOTIABLE VIOLATION: Absolute machine-dependent path detected: '{ref}'.")
                rig_score = 0.0

        q_score = CharacterProductionQualityScore(
            geometry_score=geo_score,
            rig_score=rig_score,
            skinning_score=skin_score,
            lod_score=lod_score,
        )

        is_valid = len(issues) == 0 and q_score.aggregate_score >= 0.85
        review_status = "PASSED" if is_valid else "MANUAL_REVIEW_REQUIRED"

        return CharacterProductionValidationReport(
            is_valid=is_valid,
            quality_score=q_score,
            issues=issues,
            warnings=warnings,
            review_status=review_status,
        )
