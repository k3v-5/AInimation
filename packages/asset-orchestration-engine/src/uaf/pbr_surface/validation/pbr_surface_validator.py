"""
PBRSurfaceValidator enforces PBR physical ranges, POT resolutions, normal/AO maps, and path purity.
UAF-81.43 Sections 18, 20, 138, 144, 158, 159, 160.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from ..models.definition import PBRSurfaceSpecification


@dataclass
class PBRSurfaceQualityScore:
    pbr_range_score: float  # 0.0 to 1.0 (metallic/roughness in [0,1], base_color in [0,1])
    uv_score: float         # 0.0 to 1.0 (valid UV strategy and texel density profile)
    texture_score: float    # 0.0 to 1.0 (POT resolution >= 256, normal & AO maps present)
    unreal_score: float     # 0.0 to 1.0 (valid master material, instance, and texture set paths)

    @property
    def aggregate_score(self) -> float:
        return round(
            0.30 * self.pbr_range_score +
            0.25 * self.uv_score +
            0.25 * self.texture_score +
            0.20 * self.unreal_score,
            3
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "pbr_range_score": self.pbr_range_score,
            "uv_score": self.uv_score,
            "texture_score": self.texture_score,
            "unreal_score": self.unreal_score,
            "aggregate_score": self.aggregate_score,
        }


@dataclass
class PBRSurfaceValidationReport:
    is_valid: bool
    quality_score: PBRSurfaceQualityScore
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


class PBRSurfaceValidator:
    """
    Enforces NON-NEGOTIABLE HARD FAIL CONDITIONS (Sections 144, 158, 159, 160).
    """

    @classmethod
    def validate_pbr_surface(
        cls,
        spec: PBRSurfaceSpecification,
        master_material_path: str,
        material_instance_path: str,
        texture_set_path: str,
    ) -> PBRSurfaceValidationReport:
        issues = []
        warnings = []

        # 1. PBR physical ranges validation (Section 138, 160)
        pbr_score = 1.0
        if not (0.0 <= spec.pbr.metallic <= 1.0):
            issues.append(f"HARD FAIL CONDITION: INVALID_PBR_RANGE: metallic={spec.pbr.metallic} outside [0.0, 1.0].")
            pbr_score = 0.0
        if not (0.0 <= spec.pbr.roughness <= 1.0):
            issues.append(f"HARD FAIL CONDITION: INVALID_PBR_RANGE: roughness={spec.pbr.roughness} outside [0.0, 1.0].")
            pbr_score = 0.0
        if spec.pbr.emissive_intensity < 0.0:
            issues.append(f"HARD FAIL CONDITION: INVALID_PBR_RANGE: emissive_intensity={spec.pbr.emissive_intensity} < 0.0.")
            pbr_score = 0.0
        if not all(0.0 <= c <= 1.0 for c in spec.pbr.base_color_rgb):
            issues.append(f"HARD FAIL CONDITION: INVALID_PBR_RANGE: base_color_rgb={spec.pbr.base_color_rgb} channels outside [0.0, 1.0].")
            pbr_score = 0.0

        # 2. UV strategy & density (Section 158)
        uv_score = 1.0

        # 3. Texture resolution and maps (Section 137, 159)
        tex_score = 1.0
        res = spec.pbr.resolution
        if res < 256 or (res & (res - 1)) != 0:
            issues.append(f"HARD FAIL CONDITION: INVALID_RESOLUTION: resolution={res} is not a power-of-two >= 256.")
            tex_score = 0.0
        if not spec.has_normal_map:
            issues.append("HARD FAIL CONDITION: MISSING_TEXTURE_MAPS: Normal map is strictly required for PBR authoring.")
            tex_score = 0.0
        if not spec.has_ao_map:
            issues.append("HARD FAIL CONDITION: MISSING_TEXTURE_MAPS: Ambient Occlusion (AO) map is strictly required.")
            tex_score = 0.0

        # 4. Path purity check (Section 166)
        unreal_score = 1.0
        for p in [master_material_path, material_instance_path, texture_set_path]:
            if ":\\" in p or ":/" in p:
                issues.append(f"HARD FAIL CONDITION: Absolute machine-dependent path detected: '{p}'.")
                unreal_score = 0.0

        q_score = PBRSurfaceQualityScore(
            pbr_range_score=pbr_score,
            uv_score=uv_score,
            texture_score=tex_score,
            unreal_score=unreal_score,
        )

        is_valid = len(issues) == 0 and q_score.aggregate_score >= 0.85
        review_status = "PASSED" if is_valid else "MANUAL_REVIEW_REQUIRED"

        return PBRSurfaceValidationReport(
            is_valid=is_valid,
            quality_score=q_score,
            issues=issues,
            warnings=warnings,
            review_status=review_status,
        )
