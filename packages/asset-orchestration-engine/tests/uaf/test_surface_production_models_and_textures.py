"""
Tests for Surface Production Models, PBR Profiles, and Texture Channels.
UAF-81.18 Sections 3, 4, 7, 21, 26, 27, 29.
"""

from uaf.surface_production.models.definition import (
    SurfaceWeatheringState,
    MaterialPBRProfile,
    SurfaceDefinition,
)
from uaf.surface_production.models.textures import (
    TexturePackingType,
    TextureChannelDefinition,
)


def test_surface_definition_and_pbr_profile():
    s_def = SurfaceDefinition(
        surface_id="Surf_Carbon_Chassis",
        surface_type="ARMOR",
        material_family="COMPOSITE",
        resolution=2048,
        weathering_state=SurfaceWeatheringState.WORN,
        seed=998877,
    )
    assert s_def.surface_type == "ARMOR"
    assert s_def.weathering_state == "WORN"
    assert len(s_def.definition_hash) == 64

    mat = MaterialPBRProfile(
        base_color_hex="#222222",
        metallic=0.1,
        roughness=0.4,
        normal_strength=1.2,
    )
    assert mat.metallic == 0.1
    data = mat.to_dict()
    assert data["roughness"] == 0.4


def test_texture_channel_definition_power_of_two():
    tex_ok = TextureChannelDefinition("T_Albedo", "ALBEDO", "sRGB", 2048)
    assert tex_ok.is_power_of_two is True

    tex_bad = TextureChannelDefinition("T_Bad", "ALBEDO", "sRGB", 1500)
    assert tex_bad.is_power_of_two is False
