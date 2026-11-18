"""
Tests for Surface Pipeline Models and Texture Definitions.
UAF-81.27 Sections 3, 4, 15, 16, 17, 19, 22.
"""

from uaf.surface_pipeline.models.definition import (
    SurfaceClass27,
    UVStrategyType,
    ColorSpace27,
    TextureMapDefinition,
    SurfaceDefinition27,
)


def test_texture_map_definition_power_of_two():
    tex_ok = TextureMapDefinition("T_Wall_BC", "BASE_COLOR", 2048, ColorSpace27.SRGB)
    assert tex_ok.is_power_of_two is True

    tex_npot = TextureMapDefinition("T_Wall_Bad", "BASE_COLOR", 1080, ColorSpace27.SRGB)
    assert tex_npot.is_power_of_two is False

    tex_too_small = TextureMapDefinition("T_Wall_Small", "BASE_COLOR", 128, ColorSpace27.SRGB)
    assert tex_too_small.is_power_of_two is False


def test_surface_definition_and_hashing():
    textures = [
        TextureMapDefinition("T_Albedo", "BASE_COLOR", 2048, ColorSpace27.SRGB),
        TextureMapDefinition("T_Normal", "NORMAL", 2048, ColorSpace27.NORMAL_MAP),
        TextureMapDefinition("T_ORM", "ORM", 2048, ColorSpace27.LINEAR),
    ]
    s_def = SurfaceDefinition27(
        "Surf_Composite_Metal",
        "Asset_Prop_Box",
        SurfaceClass27.METAL,
        UVStrategyType.SEAM_BASED,
        texel_density=10.24,
        textures=textures,
        seed=13579,
    )

    assert s_def.surface_class == "METAL"
    assert len(s_def.definition_hash) == 64
    data = s_def.to_dict()
    assert data["uv_strategy"] == "SEAM_BASED"
    assert len(data["textures"]) == 3
