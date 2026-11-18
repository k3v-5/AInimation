"""
SurfaceQualityScore and QualityTier models for physical surface assessment.
UAF-81.7 Sections 105, 106, 107, 111.
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from ..models.texture_set import TextureSet
from ..models.channels import ColorSpace, PBRChannel
from ..uv.uv_definition import UVDefinition, UVOverlapPolicy


class QualityTier(str, Enum):
    FAILED = "FAILED"
    PROTOTYPE = "PROTOTYPE"
    PRODUCTION = "PRODUCTION"
    HIGH_QUALITY = "HIGH_QUALITY"
    CINEMATIC = "CINEMATIC"


@dataclass
class SurfaceQualityScore:
    uv_quality: float            # 0.0 to 1.0
    texture_quality: float       # 0.0 to 1.0
    material_quality: float      # 0.0 to 1.0
    physical_consistency: float  # 0.0 to 1.0
    performance_score: float     # 0.0 to 1.0

    @property
    def aggregate_score(self) -> float:
        return round(
            0.25 * self.uv_quality +
            0.25 * self.texture_quality +
            0.20 * self.material_quality +
            0.15 * self.physical_consistency +
            0.15 * self.performance_score,
            3
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "uv_quality": self.uv_quality,
            "texture_quality": self.texture_quality,
            "material_quality": self.material_quality,
            "physical_consistency": self.physical_consistency,
            "performance_score": self.performance_score,
            "aggregate_score": self.aggregate_score,
        }


@dataclass
class SurfaceQualityReport:
    is_valid: bool
    quality_tier: QualityTier
    quality_score: SurfaceQualityScore
    issues: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    review_status: str = "PASSED"  # "PASSED", "MANUAL_REVIEW_REQUIRED"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "is_valid": self.is_valid,
            "quality_tier": self.quality_tier.value,
            "quality_score": self.quality_score.to_dict(),
            "issues": self.issues,
            "warnings": self.warnings,
            "review_status": self.review_status,
        }


class ComprehensiveSurfaceValidator:
    """
    Validates physical surface consistency, UV overlap rules, color space correctness, and shader costs.
    Enforces NON-NEGOTIABLE PRINCIPLE (Section 111).
    """
    @classmethod
    def validate_surface_suite(
        cls,
        texture_set: TextureSet,
        uv_def: Optional[UVDefinition] = None,
        max_vram_mb: float = 256.0,
    ) -> SurfaceQualityReport:
        issues = []
        warnings = []

        # 1. Color Space & Channel Integrity (Section 12, 13)
        tex_score = 1.0
        for ch_name, tex in texture_set.textures.items():
            if ch_name == PBRChannel.BASE_COLOR.value and tex.color_space != ColorSpace.SRGB:
                issues.append(f"ColorSpace violation: BaseColor map '{tex.texture_id}' must use sRGB, got '{tex.color_space.value}'.")
                tex_score -= 0.4
            elif ch_name == PBRChannel.NORMAL.value and tex.color_space != ColorSpace.NORMAL_MAP:
                issues.append(f"ColorSpace violation: Normal map '{tex.texture_id}' must use NormalMap, got '{tex.color_space.value}'.")
                tex_score -= 0.4
            elif ch_name in ["ORM", PBRChannel.METALLIC.value, PBRChannel.ROUGHNESS.value] and tex.color_space != ColorSpace.LINEAR:
                issues.append(f"ColorSpace violation: Data texture '{tex.texture_id}' must use Linear, got '{tex.color_space.value}'.")
                tex_score -= 0.3

        # 2. UV Integrity (Section 21, 22)
        uv_score = 1.0
        if uv_def:
            if uv_def.has_overlapping_islands and uv_def.overlap_policy == UVOverlapPolicy.FORBIDDEN:
                issues.append("UV overlap violation: Overlapping islands detected when policy is FORBIDDEN.")
                uv_score = 0.0
            elif uv_def.padding_px < 4:
                warnings.append(f"UV padding {uv_def.padding_px}px is narrow, potential texture bleeding.")
                uv_score -= 0.1

        # 3. Performance & Memory Budget (Section 15)
        vram_mb = texture_set.total_memory_bytes / (1024 * 1024)
        perf_score = 1.0
        if vram_mb > max_vram_mb:
            issues.append(f"Memory budget exceeded: {vram_mb:.1f}MB exceeds limit of {max_vram_mb:.1f}MB.")
            perf_score = 0.5

        # 4. Material Consistency
        mat_score = 1.0
        if not texture_set.get_texture(PBRChannel.BASE_COLOR.value):
            issues.append("Missing required BaseColor texture in TextureSet.")
            mat_score -= 0.5

        phys_score = 1.0 if not issues else 0.5

        q_score = SurfaceQualityScore(
            uv_quality=max(0.0, uv_score),
            texture_quality=max(0.0, tex_score),
            material_quality=max(0.0, mat_score),
            physical_consistency=phys_score,
            performance_score=perf_score,
        )

        agg = q_score.aggregate_score
        if len(issues) > 0 or agg < 0.6:
            tier = QualityTier.FAILED
            review_status = "MANUAL_REVIEW_REQUIRED"
            is_valid = False
        elif agg >= 0.90:
            tier = QualityTier.CINEMATIC
            review_status = "PASSED"
            is_valid = True
        elif agg >= 0.80:
            tier = QualityTier.HIGH_QUALITY
            review_status = "PASSED"
            is_valid = True
        else:
            tier = QualityTier.PRODUCTION
            review_status = "PASSED"
            is_valid = True

        return SurfaceQualityReport(
            is_valid=is_valid,
            quality_tier=tier,
            quality_score=q_score,
            issues=issues,
            warnings=warnings,
            review_status=review_status,
        )
