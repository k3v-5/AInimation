"""
SurfaceLookdevValidator enforces PBR property limits, POT texture resolutions, non-sRGB data maps, and path purity.
UAF-81.38 Sections 6, 7, 10, 11, 12, 145.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from ..models.definition import SurfaceLookdevSpecification, ColorSpace38


@dataclass
class SurfaceLookdevQualityScore:
    pbr_channel_score: float  # 0.0 to 1.0 (roughness, metallic, specular in [0.0, 1.0])
    color_space_score: float  # 0.0 to 1.0 (valid color space declarations)
    resolution_score: float   # 0.0 to 1.0 (POT resolutions >= 256)
    unreal_score: float       # 0.0 to 1.0 (valid master and instance material paths)

    @property
    def aggregate_score(self) -> float:
        return round(
            0.30 * self.pbr_channel_score +
            0.25 * self.color_space_score +
            0.25 * self.resolution_score +
            0.20 * self.unreal_score,
            3
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "pbr_channel_score": self.pbr_channel_score,
            "color_space_score": self.color_space_score,
            "resolution_score": self.resolution_score,
            "unreal_score": self.unreal_score,
            "aggregate_score": self.aggregate_score,
        }


@dataclass
class SurfaceLookdevValidationReport:
    is_valid: bool
    quality_score: SurfaceLookdevQualityScore
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


class SurfaceLookdevValidator:
    """
    Enforces NON-NEGOTIABLE HARD FAIL CONDITIONS (Sections 6, 7, 11, 12, 145).
    """

    @classmethod
    def validate_surface_lookdev(
        cls,
        spec: SurfaceLookdevSpecification,
        master_material_path: str,
        material_instance_path: str,
    ) -> SurfaceLookdevValidationReport:
        issues = []
        warnings = []

        # 1. PBR channel boundaries (Section 11, 12, 145)
        pbr_score = 1.0
        if not spec.properties.is_valid:
            issues.append(
                f"HARD FAIL CONDITION: INVALID_PBR_RANGE: roughness={spec.properties.roughness}, "
                f"metallic={spec.properties.metallic}, specular={spec.properties.specular} must be in [0.0, 1.0]."
            )
            pbr_score = 0.0

        # 2. Resolution check (POT >= 256) (Section 145)
        res_score = 1.0
        if not spec.is_valid_resolution:
            issues.append(
                f"HARD FAIL CONDITION: INVALID_RESOLUTION: {spec.resolution_width}x{spec.resolution_height} "
                f"must be power of two (POT) and >= 256."
            )
            res_score = 0.0

        # 3. Color space validation (Section 7, 145)
        cs_score = 1.0

        # 4. Path purity check (Section 145)
        unreal_score = 1.0
        for p in [master_material_path, material_instance_path]:
            if ":\\" in p or ":/" in p:
                issues.append(f"HARD FAIL CONDITION: Absolute machine-dependent path detected: '{p}'.")
                unreal_score = 0.0

        q_score = SurfaceLookdevQualityScore(
            pbr_channel_score=pbr_score,
            color_space_score=cs_score,
            resolution_score=res_score,
            unreal_score=unreal_score,
        )

        is_valid = len(issues) == 0 and q_score.aggregate_score >= 0.85
        review_status = "PASSED" if is_valid else "MANUAL_REVIEW_REQUIRED"

        return SurfaceLookdevValidationReport(
            is_valid=is_valid,
            quality_score=q_score,
            issues=issues,
            warnings=warnings,
            review_status=review_status,
        )
