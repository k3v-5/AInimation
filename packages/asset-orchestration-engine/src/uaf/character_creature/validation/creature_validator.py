"""
CharacterCreatureValidator enforces anatomical feasibility, equipment clearances, and path purity.
UAF-81.21 Sections 11, 12, 147, 155, 156, 171.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from ..models.definition import CharacterDefinition21
from ..models.equipment import BodyPartType, ModularEquipmentLayer, EquipmentLayerType


@dataclass
class CharacterCreatureQualityScore:
    anatomy_score: float      # 0.0 to 1.0 (Anatomical bounds, proportions)
    topology_score: float     # 0.0 to 1.0 (Body parts coverage)
    deformation_score: float  # 0.0 to 1.0 (Skeleton compatibility)
    equipment_score: float    # 0.0 to 1.0 (Multi-layer clearance, non-clipping)

    @property
    def aggregate_score(self) -> float:
        return round(
            0.30 * self.anatomy_score +
            0.25 * self.topology_score +
            0.25 * self.deformation_score +
            0.20 * self.equipment_score,
            3
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "anatomy_score": self.anatomy_score,
            "topology_score": self.topology_score,
            "deformation_score": self.deformation_score,
            "equipment_score": self.equipment_score,
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
    Enforces NON-NEGOTIABLE REQUIREMENTS (Sections 11, 12, 147, 156, 171).
    """

    @classmethod
    def validate_character(
        cls,
        char_def: CharacterDefinition21,
        body_parts: List[BodyPartType],
        equipment_layers: List[ModularEquipmentLayer],
        skeleton_ref: str,
    ) -> CharacterCreatureValidationReport:
        issues = []
        warnings = []

        # 1. Anatomical constraints (Sections 11, 12)
        anat_score = 1.0
        if char_def.height_cm < 50.0 or char_def.height_cm > 500.0:
            issues.append(f"NON-NEGOTIABLE VIOLATION: Character height {char_def.height_cm}cm is outside anatomical bounds [50cm, 500cm].")
            anat_score = 0.0

        lm = char_def.landmarks
        if lm.arm_length <= 0.0 or lm.leg_length <= 0.0 or lm.shoulder_width <= 0.0:
            issues.append("NON-NEGOTIABLE VIOLATION: Non-positive anatomical limb dimensions detected.")
            anat_score = 0.0

        # 2. Topology & Body parts
        topo_score = 1.0 if len(body_parts) >= 5 else 0.7
        if len(body_parts) < 5:
            warnings.append("Character defines fewer than 5 modular body parts.")

        # 3. Deformation & Skeleton references (Section 156: No absolute machine paths)
        deform_score = 1.0
        if not skeleton_ref or ":\\" in skeleton_ref or ":/" in skeleton_ref or skeleton_ref.startswith("/"):
            issues.append(f"NON-NEGOTIABLE VIOLATION: Invalid or absolute machine-dependent skeleton reference: '{skeleton_ref}'.")
            deform_score = 0.0

        # 4. Equipment clearance and clipping prevention (Section 147)
        equip_score = 1.0
        for layer in equipment_layers:
            if layer.layer_type != EquipmentLayerType.BODY and layer.clearance_mm <= 0.0:
                issues.append(f"NON-NEGOTIABLE VIOLATION: Equipment layer '{layer.layer_id}' has non-positive clearance ({layer.clearance_mm}mm), causing clipping.")
                equip_score = 0.0

        q_score = CharacterCreatureQualityScore(
            anatomy_score=anat_score,
            topology_score=topo_score,
            deformation_score=deform_score,
            equipment_score=equip_score,
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
