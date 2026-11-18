"""
SurfaceValidator enforces color-space compliance, texture budgets, and channel packing invariants.
UAF-81.4 Sections 18, 19, 31, 71, 72.
"""

import math
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from ..models.channels import ColorSpace, PBRChannel, ChannelPacking
from ..models.texture_definition import TextureDefinition
from ..models.material_definition import MaterialDefinition


@dataclass
class SurfaceValidationReport:
    is_valid: bool
    issues: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    estimated_vram_mb: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "is_valid": self.is_valid,
            "issues": self.issues,
            "warnings": self.warnings,
            "estimated_vram_mb": self.estimated_vram_mb,
        }


class SurfaceValidator:
    """
    Validates physical realism, color spaces, power-of-two resolutions, and VRAM memory budgets.
    """
    VALID_POW2 = {128, 256, 512, 1024, 2048, 4096, 8192}

    @classmethod
    def validate_texture(cls, texture: TextureDefinition) -> List[str]:
        issues = []
        if texture.resolution not in cls.VALID_POW2:
            issues.append(f"Texture resolution {texture.resolution} is not a valid power of 2.")

        # Color-space rules (Section 19)
        channel_upper = texture.channel.upper()
        if channel_upper in ["BASE_COLOR", "ALBEDO", "DIFFUSE"]:
            if texture.color_space != ColorSpace.SRGB:
                issues.append(f"Base Color channel '{texture.channel}' must use sRGB color space, found {texture.color_space.value}.")
        elif channel_upper in ["NORMAL", "NORMAL_MAP"]:
            if texture.color_space != ColorSpace.NORMAL_MAP:
                issues.append(f"Normal channel '{texture.channel}' must use NormalMap color space, found {texture.color_space.value}.")
        elif channel_upper in ["ROUGHNESS", "METALLIC", "AMBIENT_OCCLUSION", "ORM", "DISPLACEMENT", "HEIGHT"]:
            if texture.color_space != ColorSpace.LINEAR:
                issues.append(f"Data channel '{texture.channel}' must use Linear color space, found {texture.color_space.value}.")

        return issues

    @classmethod
    def validate_channel_packing(cls, packing: ChannelPacking) -> List[str]:
        issues = []
        if packing.color_space != ColorSpace.LINEAR:
            issues.append(f"Packed texture '{packing.packed_texture_id}' must use Linear color space.")
        return issues

    @classmethod
    def validate_material_suite(
        cls,
        textures: List[TextureDefinition],
        max_vram_budget_mb: Optional[float] = None,
    ) -> SurfaceValidationReport:
        all_issues = []
        all_warnings = []
        total_vram_bytes = 0

        for tex in textures:
            issues = cls.validate_texture(tex)
            all_issues.extend(issues)

            # Estimate uncompressed VRAM (res * res * 4 bytes RGBA)
            total_vram_bytes += tex.resolution * tex.resolution * 4

        vram_mb = round(total_vram_bytes / (1024 * 1024), 2)
        if max_vram_budget_mb and vram_mb > max_vram_budget_mb:
            all_issues.append(f"Total texture VRAM ({vram_mb} MB) exceeds maximum budget ({max_vram_budget_mb} MB).")

        return SurfaceValidationReport(
            is_valid=len(all_issues) == 0,
            issues=all_issues,
            warnings=all_warnings,
            estimated_vram_mb=vram_mb,
        )
