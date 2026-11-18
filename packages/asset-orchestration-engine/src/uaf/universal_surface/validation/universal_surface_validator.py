"""
UniversalSurfaceValidator enforces PBR physical limits, POT texture dimensions, core channel presence, and path purity.
UAF-81.52 Sections 141, 144, 151, 152.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from ..models.definition import UniversalSurfaceSpecification


@dataclass
class UniversalSurfaceQualityScore:
    pbr_resolution_score: float     # 0.0 to 1.0 (PBR in [0, 1], POT resolution >= 128)
    channel_coherence_score: float  # 0.0 to 1.0 (normal, roughness, metallic, AO present)
    instance_score: float           # 0.0 to 1.0 (material instance enabled)
    unreal_score: float             # 0.0 to 1.0 (valid master material, instance, and texture paths)

    @property
    def aggregate_score(self) -> float:
        return round(
            0.30 * self.pbr_resolution_score +
            0.25 * self.channel_coherence_score +
            0.25 * self.instance_score +
            0.20 * self.unreal_score,
            3
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "pbr_resolution_score": self.pbr_resolution_score,
            "channel_coherence_score": self.channel_coherence_score,
            "instance_score": self.instance_score,
            "unreal_score": self.unreal_score,
            "aggregate_score": self.aggregate_score,
        }


@dataclass
class UniversalSurfaceValidationReport:
    is_valid: bool
    quality_score: UniversalSurfaceQualityScore
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


class UniversalSurfaceValidator:
    """
    Enforces NON-NEGOTIABLE HARD FAIL CONDITIONS (Sections 141, 144, 151, 152).
    """

    @classmethod
    def validate_universal_surface(
        cls,
        spec: UniversalSurfaceSpecification,
        master_material_path: str,
        material_instance_path: str,
        texture_set_path: str,
    ) -> UniversalSurfaceValidationReport:
        issues = []
        warnings = []

        # 1. PBR parameters and resolution (Section 55, 125, 141)
        pbr_res_score = 1.0
        if not spec.properties.is_valid:
            issues.append("HARD FAIL CONDITION: INVALID_PBR_RANGE: PBR parameters must be strictly in [0.0, 1.0].")
            pbr_res_score = 0.0
        if not spec.resolution.is_power_of_two:
            issues.append(
                f"HARD FAIL CONDITION: INVALID_RESOLUTION: width={spec.resolution.width_px}, "
                f"height={spec.resolution.height_px} must be power of two >= 128."
            )
            pbr_res_score = 0.0

        # 2. Core maps & channels (Section 125, 126, 141)
        channel_score = 1.0
        if not (spec.has_normal and spec.has_roughness and spec.has_metallic and spec.has_ambient_occlusion):
            issues.append("HARD FAIL CONDITION: MISSING_CORE_MAPS: Normal, roughness, metallic, and AO are mandatory.")
            channel_score = 0.0

        # 3. Material instance (Section 129, 147)
        inst_score = 1.0
        if not spec.has_material_instance:
            issues.append("HARD FAIL CONDITION: MISSING_CORE_SUBSYSTEMS: Material instance generation is disabled.")
            inst_score = 0.0

        # 4. Path purity check (Section 147)
        unreal_score = 1.0
        for p in [master_material_path, material_instance_path, texture_set_path]:
            if ":\\" in p or ":/" in p:
                issues.append(f"HARD FAIL CONDITION: Absolute machine-dependent path detected: '{p}'.")
                unreal_score = 0.0

        q_score = UniversalSurfaceQualityScore(
            pbr_resolution_score=pbr_res_score,
            channel_coherence_score=channel_score,
            instance_score=inst_score,
            unreal_score=unreal_score,
        )

        is_valid = len(issues) == 0 and q_score.aggregate_score >= 0.85
        review_status = "PASSED" if is_valid else "MANUAL_REVIEW_REQUIRED"

        return UniversalSurfaceValidationReport(
            is_valid=is_valid,
            quality_score=q_score,
            issues=issues,
            warnings=warnings,
            review_status=review_status,
        )
