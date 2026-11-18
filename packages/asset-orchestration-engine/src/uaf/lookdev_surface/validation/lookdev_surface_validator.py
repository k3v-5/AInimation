"""
LookdevSurfaceValidator enforces physically accurate PBR ranges, power-of-two texture resolutions, core map integrity, and path purity.
UAF-81.46 Sections 99, 100, 101, 112, 120, 121, 122, 124.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from ..models.definition import LookdevSurfaceSpecification, _is_power_of_two


@dataclass
class LookdevSurfaceQualityScore:
    pbr_range_score: float             # 0.0 to 1.0 (metallic, roughness, ao in [0, 1], emission >= 0, RGB in [0, 1])
    normal_displacement_score: float   # 0.0 to 1.0 (normal map and displacement map presence)
    resolution_score: float            # 0.0 to 1.0 (POT resolution >= 256)
    unreal_score: float                # 0.0 to 1.0 (valid master material, instance, and texture set paths)

    @property
    def aggregate_score(self) -> float:
        return round(
            0.35 * self.pbr_range_score +
            0.25 * self.normal_displacement_score +
            0.20 * self.resolution_score +
            0.20 * self.unreal_score,
            3
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "pbr_range_score": self.pbr_range_score,
            "normal_displacement_score": self.normal_displacement_score,
            "resolution_score": self.resolution_score,
            "unreal_score": self.unreal_score,
            "aggregate_score": self.aggregate_score,
        }


@dataclass
class LookdevSurfaceValidationReport:
    is_valid: bool
    quality_score: LookdevSurfaceQualityScore
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


class LookdevSurfaceValidator:
    """
    Enforces NON-NEGOTIABLE HARD FAIL CONDITIONS (Sections 99, 100, 101, 112, 121, 122, 124).
    """

    @classmethod
    def validate_lookdev_surface(
        cls,
        spec: LookdevSurfaceSpecification,
        master_material_path: str,
        material_instance_path: str,
        texture_set_path: str,
    ) -> LookdevSurfaceValidationReport:
        issues = []
        warnings = []

        # 1. PBR physical range validation (Section 6, 99, 100, 101, 122)
        pbr_score = 1.0
        pbr = spec.pbr
        if not (0.0 <= pbr.metallic <= 1.0):
            issues.append(f"HARD FAIL CONDITION: INVALID_PBR_RANGE: metallic={pbr.metallic} outside [0.0, 1.0].")
            pbr_score = 0.0
        if not (0.0 <= pbr.roughness <= 1.0):
            issues.append(f"HARD FAIL CONDITION: INVALID_PBR_RANGE: roughness={pbr.roughness} outside [0.0, 1.0].")
            pbr_score = 0.0
        if not (0.0 <= pbr.ao <= 1.0):
            issues.append(f"HARD FAIL CONDITION: INVALID_PBR_RANGE: ao={pbr.ao} outside [0.0, 1.0].")
            pbr_score = 0.0
        if pbr.emission < 0.0:
            issues.append(f"HARD FAIL CONDITION: INVALID_PBR_RANGE: emission={pbr.emission} cannot be negative.")
            pbr_score = 0.0
        if not all(0.0 <= c <= 1.0 for c in pbr.base_color_rgb):
            issues.append(f"HARD FAIL CONDITION: INVALID_PBR_RANGE: base_color_rgb={pbr.base_color_rgb} channels must be in [0.0, 1.0].")
            pbr_score = 0.0

        # 2. Resolution validation (Section 107, 112)
        res_score = 1.0
        if not _is_power_of_two(pbr.resolution) or pbr.resolution < 256:
            issues.append(f"HARD FAIL CONDITION: INVALID_RESOLUTION: resolution={pbr.resolution} must be power-of-two >= 256.")
            res_score = 0.0

        # 3. Core maps presence (Section 6, 112, 123)
        maps_score = 1.0
        if not spec.has_normal:
            issues.append("HARD FAIL CONDITION: MISSING_CORE_MAPS: Normal map is missing.")
            maps_score = 0.0
        if not spec.has_displacement:
            issues.append("HARD FAIL CONDITION: MISSING_CORE_MAPS: Displacement/Height map is missing.")
            maps_score = 0.0

        # 4. Path purity check (Section 124)
        unreal_score = 1.0
        for p in [master_material_path, material_instance_path, texture_set_path]:
            if ":\\" in p or ":/" in p:
                issues.append(f"HARD FAIL CONDITION: Absolute machine-dependent path detected: '{p}'.")
                unreal_score = 0.0

        q_score = LookdevSurfaceQualityScore(
            pbr_range_score=pbr_score,
            normal_displacement_score=maps_score,
            resolution_score=res_score,
            unreal_score=unreal_score,
        )

        is_valid = len(issues) == 0 and q_score.aggregate_score >= 0.85
        review_status = "PASSED" if is_valid else "MANUAL_REVIEW_REQUIRED"

        return LookdevSurfaceValidationReport(
            is_valid=is_valid,
            quality_score=q_score,
            issues=issues,
            warnings=warnings,
            review_status=review_status,
        )
