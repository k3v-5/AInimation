"""
Universal Character Validator & Character Quality Score.
UAF-81.54 Sections 137-141, 168, 171, 176, 177.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
import re

from ..models.definition import (
    CharacterDefinition,
    SkeletonDefinition,
    RigDefinition,
    SkinningDefinition,
    DeformationProfile,
    MorphTargetSystem,
    FacialRigDefinition,
    ClothingDefinition,
    ArmorDefinition,
    CharacterCollisionDefinition,
    CharacterLODChain,
    ValidationSeverity,
    ValidationCategory,
)


@dataclass
class CharacterQualityScore:
    geometry_score: float = 1.0      # 0.0 to 1.0
    anatomy_score: float = 1.0       # 0.0 to 1.0
    deformation_score: float = 1.0   # 0.0 to 1.0
    rig_score: float = 1.0           # 0.0 to 1.0
    material_score: float = 1.0      # 0.0 to 1.0
    optimization_score: float = 1.0  # 0.0 to 1.0
    export_score: float = 1.0        # 0.0 to 1.0

    @property
    def aggregate_score(self) -> float:
        return round(
            0.20 * self.geometry_score +
            0.15 * self.anatomy_score +
            0.15 * self.deformation_score +
            0.15 * self.rig_score +
            0.10 * self.material_score +
            0.15 * self.optimization_score +
            0.10 * self.export_score,
            3
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "geometry_score": self.geometry_score,
            "anatomy_score": self.anatomy_score,
            "deformation_score": self.deformation_score,
            "rig_score": self.rig_score,
            "material_score": self.material_score,
            "optimization_score": self.optimization_score,
            "export_score": self.export_score,
            "aggregate_score": self.aggregate_score,
        }


@dataclass
class CharacterValidationReport:
    is_valid: bool
    quality_score: CharacterQualityScore
    issues: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    category_results: Dict[str, bool] = field(default_factory=dict)
    review_status: str = "PASSED"  # "PASSED", "WARNING", "FAILED"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "is_valid": self.is_valid,
            "quality_score": self.quality_score.to_dict(),
            "issues": self.issues,
            "warnings": self.warnings,
            "category_results": self.category_results,
            "review_status": self.review_status,
        }


class CharacterValidator:
    """
    Enforces NON-NEGOTIABLE HARD FAIL CONDITIONS & MULTI-CATEGORY VALIDATION (Sections 137-141, 168).
    """

    MACHINE_PATH_PATTERN = re.compile(r"^[A-Za-z]:[\\/]", re.IGNORECASE)

    @classmethod
    def validate_character(
        cls,
        character_def: CharacterDefinition,
        skeleton: SkeletonDefinition,
        rig: RigDefinition,
        skinning: SkinningDefinition,
        deformation: DeformationProfile,
        morphs: MorphTargetSystem,
        clothings: List[ClothingDefinition],
        armors: List[ArmorDefinition],
        collision: CharacterCollisionDefinition,
        lod_chain: CharacterLODChain,
        skeletal_mesh_path: str = "/Game/Characters/SK_Character.uasset",
        skeleton_path: str = "/Game/Characters/SKEL_Character.uasset",
        physics_asset_path: str = "/Game/Characters/PHYS_Character.uasset",
    ) -> CharacterValidationReport:
        issues = []
        warnings = []
        category_results = {cat.value: True for cat in ValidationCategory}

        geom_score = 1.0
        anat_score = 1.0
        deform_score = 1.0
        rig_score = 1.0
        mat_score = 1.0
        opt_score = 1.0
        exp_score = 1.0

        # 1. IDENTITY & ANATOMY (Sections 3, 5, 143, 168)
        if not character_def.is_valid:
            issues.append("HARD FAIL CONDITION: INVALID_BODY: Character definition or proportions are invalid.")
            category_results[ValidationCategory.IDENTITY.value] = False
            category_results[ValidationCategory.ANATOMY.value] = False
            anat_score = 0.0

        if not character_def.proportions.is_valid:
            issues.append("HARD FAIL CONDITION: INVALID_PROPORTIONS: All body dimensions must be strictly positive.")
            category_results[ValidationCategory.ANATOMY.value] = False
            anat_score = 0.0

        # 2. SKELETON (Sections 64, 70, 153, 168)
        if skeleton.has_duplicate_bones():
            issues.append("HARD FAIL CONDITION: INVALID_SKELETON_DUPLICATES: Skeleton contains duplicate bone names.")
            category_results[ValidationCategory.SKELETON.value] = False
            rig_score = 0.0

        if skeleton.has_cyclic_hierarchy():
            issues.append("HARD FAIL CONDITION: CYCLIC_SKELETON: Skeleton hierarchy contains a cycle.")
            category_results[ValidationCategory.SKELETON.value] = False
            rig_score = 0.0

        if skeleton.has_missing_parents():
            issues.append("HARD FAIL CONDITION: MISSING_PARENT_BONE: Bone references non-existent parent.")
            category_results[ValidationCategory.SKELETON.value] = False
            rig_score = 0.0

        if len(skeleton.bones) == 0:
            issues.append("HARD FAIL CONDITION: EMPTY_SKELETON: Skeleton contains zero bones.")
            category_results[ValidationCategory.SKELETON.value] = False
            rig_score = 0.0

        # 3. RIG & IK (Sections 72-79, 82-85, 154, 168)
        bone_names = set(skeleton.bone_names)
        for ik in rig.ik_chains:
            if ik.root not in bone_names or ik.effector not in bone_names:
                issues.append(f"HARD FAIL CONDITION: INVALID_IK_CHAIN: Chain '{ik.name}' references non-existent bones ({ik.root}, {ik.effector}).")
                category_results[ValidationCategory.RIG.value] = False
                rig_score = 0.0

        # Check constraint cycle
        constraint_map = {}
        for c in rig.constraints:
            constraint_map[c.source] = c.target
        for start_c in constraint_map:
            visited = set()
            curr = start_c
            while curr in constraint_map:
                if curr in visited:
                    issues.append(f"HARD FAIL CONDITION: CONSTRAINT_CYCLE: Constraint cycle detected at {curr}.")
                    category_results[ValidationCategory.RIG.value] = False
                    rig_score = 0.0
                    break
                visited.add(curr)
                curr = constraint_map[curr]

        # 4. SKINNING & WEIGHTS (Sections 86-94, 155, 168)
        if not skinning.is_normalized(tolerance=1e-2):
            issues.append("HARD FAIL CONDITION: UNNORMALIZED_WEIGHTS: Vertex skinning weights do not sum to 1.0.")
            category_results[ValidationCategory.WEIGHTS.value] = False
            category_results[ValidationCategory.SKIN.value] = False
            deform_score = 0.0

        if skinning.exceeds_influence_limit():
            issues.append(f"HARD FAIL CONDITION: MAX_INFLUENCES_EXCEEDED: Vertex exceeds {skinning.max_influences_per_vertex} bone influences.")
            category_results[ValidationCategory.WEIGHTS.value] = False
            deform_score = 0.0

        # 5. DEFORMATION & CORRECTIVES (Sections 95-103, 156, 157)
        if deformation.joint_scores.average_score < 0.7:
            warnings.append(f"DEFORMATION_WARNING: Joint deformation quality below threshold ({deformation.joint_scores.average_score}).")
            category_results[ValidationCategory.ANIMATION.value] = False
            deform_score = min(deform_score, 0.7)

        # 6. MORPH TARGETS (Sections 104-107, 158, 168)
        morph_valid, morph_errs = morphs.validate_morphs()
        if not morph_valid:
            for err in morph_errs:
                issues.append(f"HARD FAIL CONDITION: INVALID_MORPH: {err}")
            category_results[ValidationCategory.MORPHS.value] = False
            geom_score = 0.0

        # 7. FACIAL RIG (Sections 108-111, 159)
        if morphs.facial_rig.eye_blink_l < 0.0 or morphs.facial_rig.eye_blink_l > 1.0:
            warnings.append("FACIAL_WARNING: Eye blink control out of normalized [0, 1] range.")

        # 8. CLOTHING (Sections 48-54, 149, 168)
        for cloth in clothings:
            if cloth.maximum_intersection > cloth.minimum_clearance:
                issues.append(f"HARD FAIL CONDITION: CLOTHING_PENETRATION: Clothing '{cloth.clothing_id}' violates clearance limits.")
                category_results[ValidationCategory.CLOTHING.value] = False
                geom_score = 0.0

        # 9. ARMOR (Sections 55-58, 150, 168)
        for arm in armors:
            if arm.clearance < 0.0:
                issues.append(f"HARD FAIL CONDITION: ARMOR_PENETRATION: Armor '{arm.armor_id}' has negative clearance ({arm.clearance}cm).")
                category_results[ValidationCategory.ARMOR.value] = False
                geom_score = 0.0

        # 10. COLLISION & RAGDOLL (Sections 118-121, 162, 168)
        if collision.capsules_count == 0 and collision.boxes_count == 0:
            issues.append("HARD FAIL CONDITION: INVALID_COLLISION: Character has no collision primitives.")
            category_results[ValidationCategory.COLLISION.value] = False
            opt_score = 0.0

        # 11. LOD CHAIN (Sections 122-128, 163, 168)
        if lod_chain.lod_count < 1 or len(lod_chain.reduction_per_lod) != lod_chain.lod_count:
            issues.append("HARD FAIL CONDITION: INVALID_LOD: LOD chain structure or reduction factors corrupted.")
            category_results[ValidationCategory.LOD.value] = False
            opt_score = 0.0

        # 12. EXPORT & PATH PURITY (Sections 176, 177)
        for path_name, p in [
            ("skeletal_mesh_path", skeletal_mesh_path),
            ("skeleton_path", skeleton_path),
            ("physics_asset_path", physics_asset_path),
        ]:
            if cls.MACHINE_PATH_PATTERN.match(p):
                issues.append(
                    f"HARD FAIL CONDITION: MACHINE_DEPENDENT_PATH: Absolute path '{p}' detected for {path_name}. "
                    "Unreal character engine must use agnostic relative/game package paths (/Game/...)."
                )
                category_results[ValidationCategory.EXPORT.value] = False
                exp_score = 0.0

            if not p.startswith("/Game/"):
                warnings.append(f"Non-standard Unreal path '{p}' (expected /Game/...).")

        is_valid = len(issues) == 0
        review_status = "PASSED" if is_valid and len(warnings) == 0 else ("WARNING" if is_valid else "FAILED")

        quality_score = CharacterQualityScore(
            geometry_score=geom_score,
            anatomy_score=anat_score,
            deformation_score=deform_score,
            rig_score=rig_score,
            material_score=mat_score,
            optimization_score=opt_score,
            export_score=exp_score,
        )

        return CharacterValidationReport(
            is_valid=is_valid,
            quality_score=quality_score,
            issues=issues,
            warnings=warnings,
            category_results=category_results,
            review_status=review_status,
        )
