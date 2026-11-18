"""
SurfaceAuthoringValidator validates PBR color spaces, channel packing, and procedural variation.
UAF-81.11 Sections 196, 197, 198, 199.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from ..models.regions import MaterialRegionGraph
from ...surface.models.texture_set import TextureSet
from ...surface.models.channels import ColorSpace, PBRChannel


@dataclass
class SurfaceAuthoringQualityScore:
    color_space_score: float         # 0.0 to 1.0
    channel_packing_score: float     # 0.0 to 1.0
    procedural_variance_score: float # 0.0 to 1.0
    region_coverage_score: float     # 0.0 to 1.0
    determinism_score: float         # 0.0 to 1.0

    @property
    def aggregate_score(self) -> float:
        return round(
            0.25 * self.color_space_score +
            0.20 * self.channel_packing_score +
            0.20 * self.procedural_variance_score +
            0.20 * self.region_coverage_score +
            0.15 * self.determinism_score,
            3
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "color_space_score": self.color_space_score,
            "channel_packing_score": self.channel_packing_score,
            "procedural_variance_score": self.procedural_variance_score,
            "region_coverage_score": self.region_coverage_score,
            "determinism_score": self.determinism_score,
            "aggregate_score": self.aggregate_score,
        }


@dataclass
class SurfaceAuthoringValidationReport:
    is_valid: bool
    quality_score: SurfaceAuthoringQualityScore
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


class SurfaceAuthoringValidator:
    """
    Enforces NON-NEGOTIABLE REQUIREMENTS (Sections 197, 198, 199).
    """

    @classmethod
    def validate_surface_authoring(
        cls,
        region_graph: MaterialRegionGraph,
        texture_set: TextureSet,
    ) -> SurfaceAuthoringValidationReport:
        issues = []
        warnings = []

        # 1. Color space validation (Section 198)
        color_space_score = 1.0
        for channel_name, tex in texture_set.textures.items():
            ch = tex.channel.upper()
            if "NORMAL" in ch:
                if tex.color_space != ColorSpace.NORMAL_MAP:
                    issues.append(f"NON-NEGOTIABLE VIOLATION: Normal map '{tex.texture_id}' has invalid color space: {tex.color_space}.")
                    color_space_score = 0.0
            elif "BASE" in ch or "ALBEDO" in ch or "DIFFUSE" in ch:
                if tex.color_space != ColorSpace.SRGB:
                    issues.append(f"NON-NEGOTIABLE VIOLATION: BaseColor '{tex.texture_id}' must be in sRGB color space: {tex.color_space}.")
                    color_space_score = 0.0
            elif ch in ["ROUGHNESS", "METALLIC", "OCCLUSION", "AMBIENT_OCCLUSION", "ORM"]:
                if tex.color_space != ColorSpace.LINEAR:
                    issues.append(f"NON-NEGOTIABLE VIOLATION: PBR data map '{tex.texture_id}' must be in Linear color space: {tex.color_space}.")
                    color_space_score = 0.0


        # 2. Channel packing validation (ORM)
        channel_packing_score = 1.0 if texture_set.is_orm_packed else 0.8

        # 3. Spatial and procedural variance (Section 197)
        if len(texture_set.textures) < 2:
            issues.append("NON-NEGOTIABLE VIOLATION: Surface lacks spatial texture variance (flat color prohibited).")
            variance_score = 0.0
        else:
            variance_score = 1.0

        # 4. Region coverage
        region_score = 1.0 if len(region_graph.regions) > 0 else 0.0
        if not region_graph.regions:
            issues.append("MaterialRegionGraph contains no defined surface regions.")

        determinism_score = 1.0

        q_score = SurfaceAuthoringQualityScore(
            color_space_score=color_space_score,
            channel_packing_score=channel_packing_score,
            procedural_variance_score=variance_score,
            region_coverage_score=region_score,
            determinism_score=determinism_score,
        )

        is_valid = len(issues) == 0 and q_score.aggregate_score >= 0.85
        review_status = "PASSED" if is_valid else "MANUAL_REVIEW_REQUIRED"

        return SurfaceAuthoringValidationReport(
            is_valid=is_valid,
            quality_score=q_score,
            issues=issues,
            warnings=warnings,
            review_status=review_status,
        )
