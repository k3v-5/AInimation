"""
Tests for Surface Detail Models and Texture Channels.
UAF-81.22 Sections 3, 4, 11, 12, 13, 148.
"""

from uaf.surface_detail.models.definition import (
    PhysicalMaterialClass,
    SurfaceLayerType,
    SurfaceDetailDefinition,
)
from uaf.surface_detail.models.textures import (
    SurfaceDetailChannel,
)


def test_surface_detail_definition_and_hashing():
    s_def = SurfaceDetailDefinition(
        "Surf_Carbon_Chassis",
        PhysicalMaterialClass.PLASTIC,
        shader_model="DEFAULT_LIT",
        base_color_hex="#1E1E1E",
        roughness=0.35,
        metallic=0.1,
        layers=[SurfaceLayerType.BASE, SurfaceLayerType.COATING],
        resolution=2048,
        seed=654321,
    )
    assert s_def.physical_class == "PLASTIC"
    assert len(s_def.definition_hash) == 64
    data = s_def.to_dict()
    assert data["shader_model"] == "DEFAULT_LIT"


def test_surface_detail_channel_power_of_two():
    tex_ok = SurfaceDetailChannel("T_Albedo", "ALBEDO", "sRGB", 2048)
    assert tex_ok.is_power_of_two is True

    tex_bad = SurfaceDetailChannel("T_BadRes", "ALBEDO", "sRGB", 1920)
    assert tex_bad.is_power_of_two is False
