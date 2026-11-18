"""
SurfaceDetailValidator enforces physical PBR ranges, power-of-two texture dimensions, and strict color spaces.
UAF-81.22 Sections 148, 151, 154, 156, 165.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from ..models.definition import SurfaceDetailDefinition
from ..models.textures import SurfaceDetailChannel


@dataclass
class SurfaceDetailQualityScore:
    pbr_score: float          # 0.0 to 1.0 (Physical metallic/roughness bounds)
    resolution_score: float   # 0.0 to 1.0 (Power-of-two >= 256)
    layer_score: float        # 0.0 to 1.0 (Valid layer stack)
    efficiency_score: float   # 0.0 to 1.0 (Texture channel packing ORM)

    @property
    def aggregate_score(self) -> float:
        return round(
            0.30 * self.pbr_score +
            0.30 * self.resolution_score +
            0.20 * self.layer_score +
            0.20 * self.efficiency_score,
            3
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "pbr_score": self.pbr_score,
            "resolution_score": self.resolution_score,
            "layer_score": self.layer_score,
            "efficiency_score": self.efficiency_score,
            "aggregate_score": self.aggregate_score,
        }


@dataclass
class SurfaceDetailValidationReport:
    is_valid: bool
    quality_score: SurfaceDetailQualityScore
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


class SurfaceDetailValidator:
    """
    Enforces NON-NEGOTIABLE REQUIREMENTS (Sections 148, 151, 154, 156).
    """

    @classmethod
    def validate_surface(
        cls,
        surface_def: SurfaceDetailDefinition,
        textures: List[SurfaceDetailChannel],
        master_material_id: str,
        material_instance_id: str,
    ) -> SurfaceDetailValidationReport:
        issues = []
        warnings = []

        # 1. PBR Parameter range checks
        pbr_score = 1.0
        if not (0.0 <= surface_def.metallic <= 1.0):
            issues.append(f"NON-NEGOTIABLE VIOLATION: Metallic value {surface_def.metallic} is out of physical bounds [0.0, 1.0].")
            pbr_score = 0.0
        if not (0.0 <= surface_def.roughness <= 1.0):
            issues.append(f"NON-NEGOTIABLE VIOLATION: Roughness value {surface_def.roughness} is out of physical bounds [0.0, 1.0].")
            pbr_score = 0.0

        # 2. Texture resolution and color space rules (Section 148)
        res_score = 1.0
        if not textures:
            issues.append("NON-NEGOTIABLE VIOLATION: Zero textures declared for surface detail.")
            res_score = 0.0

        for tex in textures:
            if not tex.is_power_of_two:
                issues.append(f"NON-NEGOTIABLE VIOLATION: Texture '{tex.texture_id}' resolution {tex.resolution} is not a power of two.")
                res_score = 0.0
            if tex.resolution < 256:
                issues.append(f"NON-NEGOTIABLE VIOLATION: Texture '{tex.texture_id}' resolution {tex.resolution} is below minimum 256.")
                res_score = 0.0

            # Color space validation (Section 148)
            if tex.channel_name in ["NORMAL", "ORM", "ROUGHNESS", "METALLIC", "AO", "MASK"]:
                if tex.color_space != "LINEAR":
                    issues.append(f"NON-NEGOTIABLE VIOLATION: Data map '{tex.texture_id}' ({tex.channel_name}) must be LINEAR, got {tex.color_space}.")
                    res_score = 0.0
            elif tex.channel_name in ["ALBEDO", "BASE_COLOR", "EMISSIVE"]:
                if tex.color_space != "sRGB":
                    issues.append(f"NON-NEGOTIABLE VIOLATION: Color map '{tex.texture_id}' ({tex.channel_name}) must be sRGB, got {tex.color_space}.")
                    res_score = 0.0

        # 3. Layer and Efficiency checks
        layer_score = 1.0 if len(surface_def.layers) > 0 else 0.5
        efficiency_score = 1.0 if any(t.channel_name == "ORM" for t in textures) else 0.8

        # 4. Path purity check (Section 151)
        for identifier in [master_material_id, material_instance_id]:
            if ":\\" in identifier or ":/" in identifier or identifier.startswith("/"):
                issues.append(f"NON-NEGOTIABLE VIOLATION: Absolute machine-dependent path detected: '{identifier}'.")
                pbr_score = 0.0

        q_score = SurfaceDetailQualityScore(
            pbr_score=pbr_score,
            resolution_score=res_score,
            layer_score=layer_score,
            efficiency_score=efficiency_score,
        )

        is_valid = len(issues) == 0 and q_score.aggregate_score >= 0.85
        review_status = "PASSED" if is_valid else "MANUAL_REVIEW_REQUIRED"

        return SurfaceDetailValidationReport(
            is_valid=is_valid,
            quality_score=q_score,
            issues=issues,
            warnings=warnings,
            review_status=review_status,
        )
