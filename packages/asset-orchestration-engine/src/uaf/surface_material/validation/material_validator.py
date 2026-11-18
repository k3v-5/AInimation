"""
SurfaceMaterialValidator enforces strict PBR limits, power-of-two resolutions, color space correctness, and relative paths.
UAF-81.30 Sections 10, 11, 13, 14, 140, 142.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from ..models.definition import ProductionSurfaceDefinition, ColorSpace30


@dataclass
class SurfaceMaterialQualityScore:
    pbr_score: float          # 0.0 to 1.0 (Roughness/metallic in bounds [0.0, 1.0])
    texture_score: float      # 0.0 to 1.0 (POT >= 256, maps present)
    color_space_score: float  # 0.0 to 1.0 (Data maps strictly LINEAR / NORMAL_MAP)
    material_score: float     # 0.0 to 1.0 (Valid material master/instance references)

    @property
    def aggregate_score(self) -> float:
        return round(
            0.25 * self.pbr_score +
            0.25 * self.texture_score +
            0.30 * self.color_space_score +
            0.20 * self.material_score,
            3
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "pbr_score": self.pbr_score,
            "texture_score": self.texture_score,
            "color_space_score": self.color_space_score,
            "material_score": self.material_score,
            "aggregate_score": self.aggregate_score,
        }


@dataclass
class SurfaceMaterialValidationReport:
    is_valid: bool
    quality_score: SurfaceMaterialQualityScore
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


class SurfaceMaterialValidator:
    """
    Enforces NON-NEGOTIABLE REQUIREMENTS (Sections 10, 11, 13, 14, 142).
    """

    @classmethod
    def validate_surface_production(
        cls,
        surface_def: ProductionSurfaceDefinition,
        master_material_ref: str,
        instance_material_ref: str,
    ) -> SurfaceMaterialValidationReport:
        issues = []
        warnings = []

        # 1. PBR boundaries validation
        pbr_score = 1.0
        if not surface_def.is_valid_pbr:
            issues.append(f"NON-NEGOTIABLE VIOLATION: Roughness {surface_def.roughness_base} or Metallic {surface_def.metallic_base} out of range [0.0, 1.0].")
            pbr_score = 0.0

        # 2. Textures POT validation (Section 11)
        tex_score = 1.0
        cs_score = 1.0
        if not surface_def.maps:
            issues.append("NON-NEGOTIABLE VIOLATION: Surface definition contains no textures.")
            tex_score = 0.0

        for m in surface_def.maps:
            if not m.is_power_of_two:
                issues.append(f"NON-NEGOTIABLE VIOLATION: Texture '{m.map_id}' resolution {m.resolution} is not a valid power of two >= 256.")
                tex_score = 0.0

            # Color space validation (Sections 14 & 142)
            if m.channel in ("NORMAL", "ORM", "MASK"):
                if m.color_space == ColorSpace30.SRGB:
                    issues.append(f"NON-NEGOTIABLE VIOLATION: Data map '{m.map_id}' ({m.channel}) must be LINEAR or NORMAL_MAP, not sRGB.")
                    cs_score = 0.0

        # 3. Path purity check (Section 142)
        mat_score = 1.0
        for ref in [master_material_ref, instance_material_ref]:
            if ":\\" in ref or ":/" in ref or ref.startswith("/"):
                issues.append(f"NON-NEGOTIABLE VIOLATION: Absolute machine-dependent path detected: '{ref}'.")
                mat_score = 0.0

        q_score = SurfaceMaterialQualityScore(
            pbr_score=pbr_score,
            texture_score=tex_score,
            color_space_score=cs_score,
            material_score=mat_score,
        )

        is_valid = len(issues) == 0 and q_score.aggregate_score >= 0.85
        review_status = "PASSED" if is_valid else "MANUAL_REVIEW_REQUIRED"

        return SurfaceMaterialValidationReport(
            is_valid=is_valid,
            quality_score=q_score,
            issues=issues,
            warnings=warnings,
            review_status=review_status,
        )
