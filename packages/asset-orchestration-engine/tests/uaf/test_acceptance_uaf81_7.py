"""
UAF-81.7 Acceptance Tests (Sections 98, 109, 110, 111).
Verifies:
- Section 98: Golden Material Library Acceptance Test (End-to-end PBR surface synthesis for
  Painted Metal, Human Skin, and Emissive Tech, validated and packaged into SurfacePackage).
- Section 111: Non-Negotiable Principle Test (ColorSpace violation or forbidden UV overlap
  strictly triggers MANUAL_REVIEW_REQUIRED).
"""

from uaf.surface.models.channels import PBRChannel, ColorSpace, PhysicalClass, ShaderModel
from uaf.surface.models.surface_definition import SurfaceDefinition, SemanticSurfaceRole
from uaf.surface.models.material_definition import MaterialDefinition
from uaf.surface.models.texture_definition import TextureDefinition
from uaf.surface.models.texture_set import TextureSet
from uaf.surface.models.surface_package import SurfacePackage
from uaf.surface.uv.uv_definition import UVDefinition, UVStrategy, UVOverlapPolicy
from uaf.surface.uv.trim_sheet import TrimSheetDefinition, TrimRegion
from uaf.surface.synthesis.procedural_synthesizer import ProceduralTextureSynthesizer
from uaf.surface.validation.surface_quality import (
    ComprehensiveSurfaceValidator,
    QualityTier,
)


def test_golden_material_library_acceptance_section_98():
    """
    Acceptance Test Section 98:
    Golden Material Library synthesis:
    - Synthesizes PBR maps (BaseColor, Normal, ORM) for Painted Metal, Human Skin, Emissive Tech
    - Validates color spaces and UV packing
    - Quality score >= 0.85 (High Quality or Cinematic Tier)
    - Complete packaging into SurfacePackage
    """
    # 1. Surface & Material Definitions
    surf_def = SurfaceDefinition(
        surface_id="surf_golden_painted_metal",
        semantic_role=SemanticSurfaceRole.PAINTED_METAL,
        material_family="PAINTED_METAL",
        shader_model=ShaderModel.DEFAULT_LIT,
    )
    mat_def = MaterialDefinition(
        material_id="M_Master_PaintedMetal",
        material_name="Master_PaintedMetal",
        family_id="PAINTED_METAL",
        shader_model=ShaderModel.DEFAULT_LIT,
    )


    # 2. Procedural PBR Texture Set Synthesis
    tex_set = ProceduralTextureSynthesizer.synthesize_pbr_set(
        set_id="Golden_PaintedMetal",
        material_family="PAINTED_METAL",
        resolution=2048,
        seed=1001,
    )

    # 3. UV Definition
    uv_def = UVDefinition(
        strategy=UVStrategy.SMART_PROJECT,
        resolution=2048,
        padding_px=8,
        overlap_policy=UVOverlapPolicy.FORBIDDEN,
        has_overlapping_islands=False,
    )

    # 4. Validation Gate
    quality_report = ComprehensiveSurfaceValidator.validate_surface_suite(tex_set, uv_def)
    assert quality_report.is_valid is True
    assert quality_report.review_status == "PASSED"
    assert quality_report.quality_tier in [QualityTier.HIGH_QUALITY, QualityTier.CINEMATIC]
    assert quality_report.quality_score.aggregate_score >= 0.85

    # 5. Export Packaging into SurfacePackage
    package = SurfacePackage(
        package_id="Pkg_Surf_PaintedMetal_01",
        surface_definition=surf_def,
        material_definition=mat_def,
        texture_set=tex_set,
        uv_definition=uv_def,
        quality_report=quality_report,
    )

    assert len(package.package_hash) == 64
    pkg_data = package.to_dict()
    assert pkg_data["package_id"] == "Pkg_Surf_PaintedMetal_01"
    assert pkg_data["quality_report"]["review_status"] == "PASSED"
    assert "texture_set" in pkg_data


def test_non_negotiable_principle_section_111():
    """
    Acceptance Test Section 111:
    Non-negotiable principle:
    Invalid color space (e.g. Normal map marked as sRGB) or overlapping UVs
    when forbidden strictly triggers review_status = MANUAL_REVIEW_REQUIRED.
    """
    # Create invalid texture set with Normal map in sRGB
    tex_set = TextureSet(set_id="Flawed_Set")
    normal_flawed = TextureDefinition(
        texture_id="T_Normal_Flawed",
        resolution=2048,
        color_space=ColorSpace.SRGB,  # VIOLATION: Normal must be NormalMap!
        channel=PBRChannel.NORMAL.value,
    )
    base_color = TextureDefinition(
        texture_id="T_BaseColor_Valid",
        resolution=2048,
        color_space=ColorSpace.SRGB,
        channel=PBRChannel.BASE_COLOR.value,
    )
    tex_set.add_texture(PBRChannel.NORMAL.value, normal_flawed)
    tex_set.add_texture(PBRChannel.BASE_COLOR.value, base_color)


    # Overlapping UV violation
    uv_flawed = UVDefinition(
        overlap_policy=UVOverlapPolicy.FORBIDDEN,
        has_overlapping_islands=True,  # VIOLATION!
    )

    report = ComprehensiveSurfaceValidator.validate_surface_suite(tex_set, uv_flawed)
    assert report.is_valid is False
    assert report.review_status == "MANUAL_REVIEW_REQUIRED"
    assert report.quality_tier == QualityTier.FAILED
    assert any("Normal map" in iss for iss in report.issues)
    assert any("UV overlap violation" in iss for iss in report.issues)
