"""
CharacterCreatureValidator enforces anatomical limits, bone hierarchy, ragdoll presence, and path purity.
UAF-81.49 Sections 139, 145, 146.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from ..models.definition import CharacterCreatureSpecification, CharacterType49


@dataclass
class CharacterCreatureQualityScore:
    dimensions_bones_score: float  # 0.0 to 1.0 (height in [50, 500]cm, bone_count >= 20)
    clothing_armor_score: float    # 0.0 to 1.0 (clothing/armor coherence)
    rig_ragdoll_score: float       # 0.0 to 1.0 (ragdoll physics & rig integrity)
    unreal_score: float            # 0.0 to 1.0 (valid skeletal mesh, ABP, and physics paths)

    @property
    def aggregate_score(self) -> float:
        return round(
            0.30 * self.dimensions_bones_score +
            0.25 * self.clothing_armor_score +
            0.25 * self.rig_ragdoll_score +
            0.20 * self.unreal_score,
            3
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "dimensions_bones_score": self.dimensions_bones_score,
            "clothing_armor_score": self.clothing_armor_score,
            "rig_ragdoll_score": self.rig_ragdoll_score,
            "unreal_score": self.unreal_score,
            "aggregate_score": self.aggregate_score,
        }


@dataclass
class CharacterCreatureValidationReport:
    is_valid: bool
    quality_score: CharacterCreatureQualityScore
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


class CharacterCreatureValidator:
    """
    Enforces NON-NEGOTIABLE HARD FAIL CONDITIONS (Sections 139, 145, 146).
    """

    @classmethod
    def validate_character_creature(
        cls,
        spec: CharacterCreatureSpecification,
        skeletal_mesh_path: str,
        anim_blueprint_path: str,
        physics_asset_path: str,
    ) -> CharacterCreatureValidationReport:
        issues = []
        warnings = []

        # 1. Anatomy and skeletal bone count (Section 10, 139)
        dim_bone_score = 1.0
        if not spec.dimensions.is_valid:
            issues.append(
                f"HARD FAIL CONDITION: INVALID_ANATOMICAL_DIMENSIONS: height={spec.dimensions.height_cm}cm "
                f"outside [50.0, 500.0] or non-positive body spans."
            )
            dim_bone_score = 0.0
        if spec.bone_count < 20:
            issues.append(f"HARD FAIL CONDITION: INVALID_BONE_COUNT: bone_count={spec.bone_count} < 20.")
            dim_bone_score = 0.0

        # 2. Clothing and armor coherence (Section 92, 94, 139)
        cloth_armor_score = 1.0
        # If player character, require clothing or armor
        if spec.character_type == CharacterType49.PLAYER and not (spec.has_clothing or spec.has_armor):
            issues.append("HARD FAIL CONDITION: MISSING_CORE_SUBSYSTEMS: Player character must have clothing or armor.")
            cloth_armor_score = 0.0

        # 3. Ragdoll & Facial Rig (Section 68, 70, 136, 139)
        rig_rag_score = 1.0
        if not spec.has_ragdoll:
            issues.append("HARD FAIL CONDITION: MISSING_CORE_SUBSYSTEMS: Physics ragdoll asset is strictly required.")
            rig_rag_score = 0.0
        if spec.character_type == CharacterType49.PLAYER and not spec.has_facial_rig:
            issues.append("HARD FAIL CONDITION: MISSING_CORE_SUBSYSTEMS: Player character must have a facial rig.")
            rig_rag_score = 0.0

        # 4. Path purity check (Section 73)
        unreal_score = 1.0
        for p in [skeletal_mesh_path, anim_blueprint_path, physics_asset_path]:
            if ":\\" in p or ":/" in p:
                issues.append(f"HARD FAIL CONDITION: Absolute machine-dependent path detected: '{p}'.")
                unreal_score = 0.0

        q_score = CharacterCreatureQualityScore(
            dimensions_bones_score=dim_bone_score,
            clothing_armor_score=cloth_armor_score,
            rig_ragdoll_score=rig_rag_score,
            unreal_score=unreal_score,
        )

        is_valid = len(issues) == 0 and q_score.aggregate_score >= 0.85
        review_status = "PASSED" if is_valid else "MANUAL_REVIEW_REQUIRED"

        return CharacterCreatureValidationReport(
            is_valid=is_valid,
            quality_score=q_score,
            issues=issues,
            warnings=warnings,
            review_status=review_status,
        )
