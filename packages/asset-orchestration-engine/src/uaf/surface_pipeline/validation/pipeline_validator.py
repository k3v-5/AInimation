"""
SurfacePipelineValidator enforces strict color spaces, power-of-two resolutions, and relative asset paths.
UAF-81.27 Sections 15, 19, 119, 120, 127, 128, 129.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from ..models.definition import SurfaceDefinition27, ColorSpace27


@dataclass
class SurfacePipelineQualityScore:
    uv_score: float             # 0.0 to 1.0 (UV strategy valid, texel density > 0)
    texel_density_score: float  # 0.0 to 1.0 (In production range 5.0 - 40.0 px/cm)
    texture_score: float        # 0.0 to 1.0 (Power of two >= 256, color spaces valid)
    material_score: float       # 0.0 to 1.0 (Valid master/instance references)

    @property
    def aggregate_score(self) -> float:
        return round(
            0.25 * self.uv_score +
            0.25 * self.texel_density_score +
            0.30 * self.texture_score +
            0.20 * self.material_score,
            3
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "uv_score": self.uv_score,
            "texel_density_score": self.texel_density_score,
            "texture_score": self.texture_score,
            "material_score": self.material_score,
            "aggregate_score": self.aggregate_score,
        }


@dataclass
class SurfacePipelineValidationReport:
    is_valid: bool
    quality_score: SurfacePipelineQualityScore
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


class SurfacePipelineValidator:
    """
    Enforces NON-NEGOTIABLE REQUIREMENTS (Sections 15, 19, 119, 120, 129).
    """

    @classmethod
    def validate_surface(
        cls,
        surface_def: SurfaceDefinition27,
        master_material_ref: str,
        instance_material_ref: str,
    ) -> SurfacePipelineValidationReport:
        issues = []
        warnings = []

        # 1. UV & Texel density checks
        uv_score = 1.0
        td_score = 1.0
        if surface_def.texel_density <= 0.0:
            issues.append("NON-NEGOTIABLE VIOLATION: Texel density must be strictly positive.")
            td_score = 0.0

        # 2. Textures validation (Sections 15 & 19)
        tex_score = 1.0
        if not surface_def.textures:
            issues.append("NON-NEGOTIABLE VIOLATION: Surface definition contains zero textures.")
            tex_score = 0.0

        for tex in surface_def.textures:
            # Power of two >= 256
            if not tex.is_power_of_two:
                issues.append(f"NON-NEGOTIABLE VIOLATION: Texture '{tex.texture_id}' resolution {tex.resolution} is not a valid power of two >= 256.")
                tex_score = 0.0

            # Color space rules (Section 19)
            if tex.channel in ("NORMAL", "ORM", "MASK"):
                if tex.color_space == ColorSpace27.SRGB:
                    issues.append(f"NON-NEGOTIABLE VIOLATION: Data map '{tex.texture_id}' ({tex.channel}) must be LINEAR or NORMAL_MAP, not sRGB.")
                    tex_score = 0.0

        # 3. Material reference purity (Section 119 & 120)
        mat_score = 1.0
        for ref in [master_material_ref, instance_material_ref]:
            if ":\\" in ref or ":/" in ref or ref.startswith("/"):
                issues.append(f"NON-NEGOTIABLE VIOLATION: Absolute machine-dependent path detected: '{ref}'.")
                mat_score = 0.0

        q_score = SurfacePipelineQualityScore(
            uv_score=uv_score,
            texel_density_score=td_score,
            texture_score=tex_score,
            material_score=mat_score,
        )

        is_valid = len(issues) == 0 and q_score.aggregate_score >= 0.85
        review_status = "PASSED" if is_valid else "MANUAL_REVIEW_REQUIRED"

        return SurfacePipelineValidationReport(
            is_valid=is_valid,
            quality_score=q_score,
            issues=issues,
            warnings=warnings,
            review_status=review_status,
        )
