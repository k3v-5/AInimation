"""
Tests for Procedural Texture Synthesis, TextureSet Aggregation, and Surface Quality Assessment.
UAF-81.7 Sections 10, 26, 27, 28, 78, 105, 106.
"""

from uaf.surface.synthesis.procedural_synthesizer import ProceduralPatternType, ProceduralTextureSynthesizer
from uaf.surface.models.texture_set import TextureSet
from uaf.surface.models.channels import PBRChannel, ColorSpace, PhysicalClass
from uaf.surface.uv.uv_definition import UVDefinition, UVOverlapPolicy
from uaf.surface.validation.surface_quality import (
    ComprehensiveSurfaceValidator,
    QualityTier,
    SurfaceQualityScore,
)


def test_procedural_texture_synthesizer_patterns():
    tex = ProceduralTextureSynthesizer.generate_pattern_texture(
        texture_id="T_Proc_Noise_01",
        pattern_type=ProceduralPatternType.NOISE,
        resolution=1024,
        seed=101,
        color_space=ColorSpace.LINEAR,
    )
    assert tex.resolution == 1024
    assert tex.color_space == ColorSpace.LINEAR
    assert len(tex.texture_hash) == 64



def test_synthesize_pbr_set_and_memory():
    tex_set = ProceduralTextureSynthesizer.synthesize_pbr_set(
        set_id="PaintedMetal_01",
        material_family="PAINTED_METAL",
        resolution=2048,
        seed=42,
    )
    assert tex_set.resolution == 2048
    assert tex_set.is_orm_packed is True
    assert tex_set.get_texture("BASE_COLOR") is not None
    assert tex_set.get_texture("NORMAL") is not None
    assert tex_set.get_texture("ORM") is not None
    assert tex_set.total_memory_bytes > 0
    assert len(tex_set.set_hash) == 64


def test_comprehensive_surface_validator_passing():
    tex_set = ProceduralTextureSynthesizer.synthesize_pbr_set("ArmorSteel_01", "PAINTED_METAL", 2048)
    uv = UVDefinition(overlap_policy=UVOverlapPolicy.FORBIDDEN, has_overlapping_islands=False)

    report = ComprehensiveSurfaceValidator.validate_surface_suite(tex_set, uv)
    assert report.is_valid is True
    assert report.review_status == "PASSED"
    assert report.quality_tier in [QualityTier.HIGH_QUALITY, QualityTier.CINEMATIC]
    assert report.quality_score.aggregate_score >= 0.85
