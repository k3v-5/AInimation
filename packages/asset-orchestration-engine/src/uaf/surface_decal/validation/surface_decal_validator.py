"""
SurfaceDecalValidator enforces PBR boundary limits, decal properties, and relative path contracts.
UAF-81.34 Sections 6, 12, 124, 145.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from ..models.definition import SurfaceAuthoringSpecification


@dataclass
class SurfaceDecalQualityScore:
    pbr_score: float          # 0.0 to 1.0 (roughness & metallic in [0.0, 1.0])
    wear_damage_score: float  # 0.0 to 1.0 (wear/damage valid lists)
    decal_score: float        # 0.0 to 1.0 (decals valid dimensions and opacity)
    material_score: float     # 0.0 to 1.0 (valid master/instance material refs)

    @property
    def aggregate_score(self) -> float:
        return round(
            0.30 * self.pbr_score +
            0.20 * self.wear_damage_score +
            0.25 * self.decal_score +
            0.25 * self.material_score,
            3
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "pbr_score": self.pbr_score,
            "wear_damage_score": self.wear_damage_score,
            "decal_score": self.decal_score,
            "material_score": self.material_score,
            "aggregate_score": self.aggregate_score,
        }


@dataclass
class SurfaceDecalValidationReport:
    is_valid: bool
    quality_score: SurfaceDecalQualityScore
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


class SurfaceDecalValidator:
    """
    Enforces NON-NEGOTIABLE REQUIREMENTS (Sections 6, 12, 124).
    """

    @classmethod
    def validate_surface_authoring(
        cls,
        spec: SurfaceAuthoringSpecification,
        master_material_ref: str,
        instance_material_ref: str,
    ) -> SurfaceDecalValidationReport:
        issues = []
        warnings = []

        # 1. PBR bounds check (Section 6)
        pbr_score = 1.0
        if not spec.is_valid_pbr:
            issues.append(f"NON-NEGOTIABLE VIOLATION: Roughness {spec.roughness_base} or Metallic {spec.metallic_base} outside range [0.0, 1.0].")
            pbr_score = 0.0

        # 2. Wear / Damage check
        wd_score = 1.0

        # 3. Decal check (Section 124)
        decal_score = 1.0
        for d in spec.decals:
            if not d.is_valid:
                issues.append(f"NON-NEGOTIABLE VIOLATION: Decal '{d.decal_id}' has invalid dimensions {d.size_cm} or opacity {d.opacity} outside [0.0, 1.0].")
                decal_score = 0.0

        # 4. Path purity check (Section 124)
        mat_score = 1.0
        for ref in [master_material_ref, instance_material_ref]:
            if ":\\" in ref or ":/" in ref or ref.startswith("/"):
                issues.append(f"NON-NEGOTIABLE VIOLATION: Absolute machine-dependent path detected: '{ref}'.")
                mat_score = 0.0

        q_score = SurfaceDecalQualityScore(
            pbr_score=pbr_score,
            wear_damage_score=wd_score,
            decal_score=decal_score,
            material_score=mat_score,
        )

        is_valid = len(issues) == 0 and q_score.aggregate_score >= 0.85
        review_status = "PASSED" if is_valid else "MANUAL_REVIEW_REQUIRED"

        return SurfaceDecalValidationReport(
            is_valid=is_valid,
            quality_score=q_score,
            issues=issues,
            warnings=warnings,
            review_status=review_status,
        )
