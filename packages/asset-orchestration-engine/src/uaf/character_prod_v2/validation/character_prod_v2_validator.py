"""
CharacterProdV2Validator enforces anatomical bounds, clothing/hair presence, facial rig integrity, and path purity.
UAF-81.45 Sections 11, 12, 119, 136, 153, 154, 155, 156, 157.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from ..models.definition import CharacterProdV2Specification


@dataclass
class CharacterProdV2QualityScore:
    anatomy_score: float        # 0.0 to 1.0 (height in [50, 450]cm, bone_count >= 20)
    clothing_hair_score: float  # 0.0 to 1.0 (clothing and hair presence/fit)
    rig_facial_score: float     # 0.0 to 1.0 (facial rig and physics asset)
    unreal_score: float         # 0.0 to 1.0 (valid skeletal mesh, facial ABP, and physics asset paths)

    @property
    def aggregate_score(self) -> float:
        return round(
            0.30 * self.anatomy_score +
            0.25 * self.clothing_hair_score +
            0.25 * self.rig_facial_score +
            0.20 * self.unreal_score,
            3
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "anatomy_score": self.anatomy_score,
            "clothing_hair_score": self.clothing_hair_score,
            "rig_facial_score": self.rig_facial_score,
            "unreal_score": self.unreal_score,
            "aggregate_score": self.aggregate_score,
        }


@dataclass
class CharacterProdV2ValidationReport:
    is_valid: bool
    quality_score: CharacterProdV2QualityScore
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


class CharacterProdV2Validator:
    """
    Enforces NON-NEGOTIABLE HARD FAIL CONDITIONS (Sections 11, 136, 154, 155, 156, 157).
    """

    @classmethod
    def validate_character_prod_v2(
        cls,
        spec: CharacterProdV2Specification,
        skeletal_mesh_path: str,
        facial_anim_blueprint_path: str,
        physics_asset_path: str,
    ) -> CharacterProdV2ValidationReport:
        issues = []
        warnings = []

        # 1. Anatomy and skeletal bone count (Section 8, 154, 156)
        anat_score = 1.0
        if not spec.dimensions.is_valid:
            issues.append(
                f"HARD FAIL CONDITION: INVALID_ANATOMICAL_DIMENSIONS: height={spec.dimensions.height_cm}cm "
                f"outside [50.0, 450.0] or non-positive limb/torso spans."
            )
            anat_score = 0.0
        if spec.bone_count < 20:
            issues.append(f"HARD FAIL CONDITION: INVALID_BONE_COUNT: bone_count={spec.bone_count} < 20.")
            anat_score = 0.0

        # 2. Clothing & Hair presence (Section 58, 60, 155)
        cloth_score = 1.0
        if not spec.has_clothing:
            issues.append("HARD FAIL CONDITION: MISSING_CORE_COMPONENTS: Clothing generation is disabled.")
            cloth_score = 0.0
        if not spec.has_hair:
            issues.append("HARD FAIL CONDITION: MISSING_CORE_COMPONENTS: Hair/fur generation is disabled.")
            cloth_score = 0.0

        # 3. Facial Rig & Physics Asset (Section 66, 68, 157)
        rig_score = 1.0
        if not spec.has_facial_rig:
            issues.append("HARD FAIL CONDITION: MISSING_CORE_COMPONENTS: Facial animation rig is missing.")
            rig_score = 0.0
        if not spec.has_physics_asset:
            issues.append("HARD FAIL CONDITION: MISSING_CORE_COMPONENTS: Physics asset/ragdoll is missing.")
            rig_score = 0.0

        # 4. Path purity check (Section 119)
        unreal_score = 1.0
        for p in [skeletal_mesh_path, facial_anim_blueprint_path, physics_asset_path]:
            if ":\\" in p or ":/" in p:
                issues.append(f"HARD FAIL CONDITION: Absolute machine-dependent path detected: '{p}'.")
                unreal_score = 0.0

        q_score = CharacterProdV2QualityScore(
            anatomy_score=anat_score,
            clothing_hair_score=cloth_score,
            rig_facial_score=rig_score,
            unreal_score=unreal_score,
        )

        is_valid = len(issues) == 0 and q_score.aggregate_score >= 0.85
        review_status = "PASSED" if is_valid else "MANUAL_REVIEW_REQUIRED"

        return CharacterProdV2ValidationReport(
            is_valid=is_valid,
            quality_score=q_score,
            issues=issues,
            warnings=warnings,
            review_status=review_status,
        )
