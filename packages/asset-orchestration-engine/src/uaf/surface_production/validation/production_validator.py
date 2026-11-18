"""
SurfaceProductionValidator enforces PBR physical ranges, linear data color-spaces, and power-of-two resolutions.
UAF-81.18 Sections 26, 27, 29, 211, 214, 220.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from ..models.definition import SurfaceDefinition, MaterialPBRProfile
from ..models.textures import TextureChannelDefinition


@dataclass
class SurfaceProductionQualityScore:
    uv_score: float        # 0.0 to 1.0 (UV channels)
    pbr_score: float       # 0.0 to 1.0 (PBR ranges)
    texture_score: float   # 0.0 to 1.0 (Color spaces, power-of-two)
    material_score: float  # 0.0 to 1.0 (Master/Instance, variants)

    @property
    def aggregate_score(self) -> float:
        return round(
            0.25 * self.uv_score +
            0.25 * self.pbr_score +
            0.25 * self.texture_score +
            0.25 * self.material_score,
            3
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "uv_score": self.uv_score,
            "pbr_score": self.pbr_score,
            "texture_score": self.texture_score,
            "material_score": self.material_score,
            "aggregate_score": self.aggregate_score,
        }


@dataclass
class SurfaceProductionValidationReport:
    is_valid: bool
    quality_score: SurfaceProductionQualityScore
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


class SurfaceProductionValidator:
    """
    Enforces NON-NEGOTIABLE REQUIREMENTS (Sections 26, 27, 29, 214, 220).
    """

    @classmethod
    def validate_surface(
        cls,
        uv_set_name: str,
        surface_def: SurfaceDefinition,
        material_profile: MaterialPBRProfile,
        textures: List[TextureChannelDefinition],
        master_material_id: str,
        material_instance_id: str,
        variants: Dict[str, Any],
    ) -> SurfaceProductionValidationReport:
        issues = []
        warnings = []

        # 1. UV validation (Section 214)
        uv_score = 1.0 if uv_set_name else 0.0
        if not uv_set_name:
            issues.append("NON-NEGOTIABLE VIOLATION: Missing UV set channel.")

        # 2. PBR profile range validation (Sections 10, 11, 180)
        pbr_score = 1.0
        if not (0.0 <= material_profile.metallic <= 1.0):
            issues.append(f"NON-NEGOTIABLE VIOLATION: Metallic out of range [0.0, 1.0]: {material_profile.metallic}.")
            pbr_score = 0.0
        if not (0.0 <= material_profile.roughness <= 1.0):
            issues.append(f"NON-NEGOTIABLE VIOLATION: Roughness out of range [0.0, 1.0]: {material_profile.roughness}.")
            pbr_score = 0.0

        # 3. Texture color space & resolution rules (Sections 26, 27, 29)
        tex_score = 1.0
        channel_names = {t.channel_name for t in textures}
        if not {"ALBEDO", "NORMAL", "ORM"}.issubset(channel_names):
            issues.append("NON-NEGOTIABLE VIOLATION: Incomplete PBR texture set (ALBEDO, NORMAL, ORM required).")
            tex_score = 0.0

        for tex in textures:
            if not tex.is_power_of_two or tex.resolution < 256:
                issues.append(f"NON-NEGOTIABLE VIOLATION: Texture '{tex.texture_id}' has invalid resolution {tex.resolution} (must be power of two >= 256).")
                tex_score = 0.0

            # Rule 27: Data maps (NORMAL, ORM) MUST NOT be marked as sRGB
            if tex.channel_name in ["NORMAL", "ORM"] and tex.color_space != "LINEAR":
                issues.append(f"NON-NEGOTIABLE VIOLATION: Data map '{tex.texture_id}' ({tex.channel_name}) must be LINEAR, got '{tex.color_space}'.")
                tex_score = 0.0

            # Albedo should be sRGB
            if tex.channel_name == "ALBEDO" and tex.color_space != "sRGB":
                issues.append(f"NON-NEGOTIABLE VIOLATION: Color map '{tex.texture_id}' (ALBEDO) must be sRGB, got '{tex.color_space}'.")
                tex_score = 0.0

        # 4. Material Instance & Variants (Sections 201, 220)
        mat_score = 1.0
        if not master_material_id or not material_instance_id:
            issues.append("NON-NEGOTIABLE VIOLATION: Missing master material or instance identifier.")
            mat_score = 0.0
        if not variants:
            warnings.append("No surface weathering variants defined.")

        q_score = SurfaceProductionQualityScore(
            uv_score=uv_score,
            pbr_score=pbr_score,
            texture_score=tex_score,
            material_score=mat_score,
        )

        is_valid = len(issues) == 0 and q_score.aggregate_score >= 0.85
        review_status = "PASSED" if is_valid else "MANUAL_REVIEW_REQUIRED"

        return SurfaceProductionValidationReport(
            is_valid=is_valid,
            quality_score=q_score,
            issues=issues,
            warnings=warnings,
            review_status=review_status,
        )
