"""
CharacterSuiteValidator enforces non-negotiable character fabrication requirements.
UAF-81.14 Sections 158, 201, 203, 204, 209.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from ..models.profile import CharacterProfile
from ..models.deformation import DeformationProfile, FaceProfile, CharacterLayer


@dataclass
class CharacterQualityScore:
    geometry_score: float        # 0.0 to 1.0
    rig_skin_score: float        # 0.0 to 1.0
    layer_clipping_score: float  # 0.0 to 1.0
    deformation_score: float     # 0.0 to 1.0
    performance_score: float     # 0.0 to 1.0

    @property
    def aggregate_score(self) -> float:
        return round(
            0.25 * self.geometry_score +
            0.25 * self.rig_skin_score +
            0.20 * self.layer_clipping_score +
            0.15 * self.deformation_score +
            0.15 * self.performance_score,
            3
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "geometry_score": self.geometry_score,
            "rig_skin_score": self.rig_skin_score,
            "layer_clipping_score": self.layer_clipping_score,
            "deformation_score": self.deformation_score,
            "performance_score": self.performance_score,
            "aggregate_score": self.aggregate_score,
        }


@dataclass
class CharacterValidationReport:
    is_valid: bool
    quality_score: CharacterQualityScore
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


class CharacterSuiteValidator:
    """
    Enforces NON-NEGOTIABLE REQUIREMENTS (Sections 201, 203, 204, 209).
    """

    @classmethod
    def validate_character(
        cls,
        profile: CharacterProfile,
        deformation: DeformationProfile,
        face: FaceProfile,
        layers: List[CharacterLayer],
    ) -> CharacterValidationReport:
        issues = []
        warnings = []

        # 1. Scale & Anatomy validation (Section 209)
        geom_score = 1.0
        if profile.height_cm <= 0 or profile.body_mass_kg <= 0:
            issues.append(f"NON-NEGOTIABLE VIOLATION: Character has invalid physical dimensions: height={profile.height_cm}, mass={profile.body_mass_kg}.")
            geom_score = 0.0

        # 2. Mandatory Rig & Skinning validation (Section 203)
        rig_score = 1.0
        if deformation.bone_count <= 0:
            issues.append("NON-NEGOTIABLE VIOLATION: Rig is mandatory for animated characters (bone_count <= 0).")
            rig_score = 0.0

        if deformation.max_weights_per_vertex <= 0:
            issues.append("NON-NEGOTIABLE VIOLATION: Skinning weights per vertex must be positive.")
            rig_score = 0.0

        # 3. Layer clipping clearance (Sections 154, 205)
        clipping_score = 1.0
        if not layers:
            issues.append("NON-NEGOTIABLE VIOLATION: Character contains no geometry layers.")
            clipping_score = 0.0
        else:
            for layer in layers:
                if layer.clipping_clearance_mm < 0.0:
                    issues.append(f"NON-NEGOTIABLE VIOLATION: Layer '{layer.layer_id}' has negative clipping clearance: {layer.clipping_clearance_mm}mm.")
                    clipping_score = 0.0

        deform_score = deformation.deformation_quality
        perf_score = 1.0

        q_score = CharacterQualityScore(
            geometry_score=geom_score,
            rig_skin_score=rig_score,
            layer_clipping_score=clipping_score,
            deformation_score=deform_score,
            performance_score=perf_score,
        )

        is_valid = len(issues) == 0 and q_score.aggregate_score >= 0.85
        review_status = "PASSED" if is_valid else "MANUAL_REVIEW_REQUIRED"

        return CharacterValidationReport(
            is_valid=is_valid,
            quality_score=q_score,
            issues=issues,
            warnings=warnings,
            review_status=review_status,
        )
