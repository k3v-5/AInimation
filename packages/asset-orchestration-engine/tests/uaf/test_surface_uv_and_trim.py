"""
Tests for UV Definitions, Texel Density, Trim Sheets, and Texture Atlases.
UAF-81.7 Sections 16, 17, 18, 19, 23, 24, 25.
"""

from uaf.surface.uv.uv_definition import UVChannel, UVStrategy, UVOverlapPolicy, UVDefinition
from uaf.surface.uv.trim_sheet import TrimRegion, TrimSheetDefinition
from uaf.surface.uv.texture_atlas import TextureAtlasDefinition, UDIMDefinition
from uaf.surface.models.texel_density import TexelDensityProfile


def test_uv_definition_properties():
    uv = UVDefinition(
        uv_channel=UVChannel.UV0,
        strategy=UVStrategy.SMART_PROJECT,
        resolution=2048,
        padding_px=8,
        overlap_policy=UVOverlapPolicy.FORBIDDEN,
    )
    assert uv.uv_channel == UVChannel.UV0
    assert uv.padding_px == 8
    data = uv.to_dict()
    assert data["strategy"] == "SMART_PROJECT"
    assert data["overlap_policy"] == "FORBIDDEN"


def test_texel_density_validation():
    profile = TexelDensityProfile(target_px_per_meter=512.0, min_px_per_meter=256.0, max_px_per_meter=1024.0)

    # Valid
    is_valid, msg = profile.validate_density(500.0)
    assert is_valid is True

    # Under-density
    is_valid, msg = profile.validate_density(128.0)
    assert is_valid is False
    assert "Under-density" in msg

    # Over-density
    is_valid, msg = profile.validate_density(2048.0)
    assert is_valid is False
    assert "Over-density" in msg


def test_trim_sheet_definition():
    sheet = TrimSheetDefinition(
        sheet_id="Trim_SciFi_Panels",
        resolution=2048,
        trim_regions=[
            TrimRegion("trim_01", 0.0, 0.0, 1.0, 0.25, material_family="PAINTED_METAL", label="TopBorder"),
            TrimRegion("trim_02", 0.0, 0.25, 1.0, 0.50, material_family="EMISSIVE_TECH", label="LightStrip"),
        ],
    )
    assert len(sheet.trim_regions) == 2
    r1 = sheet.get_region("trim_01")
    assert r1 is not None
    assert r1.height == 0.25
    assert r1.material_family == "PAINTED_METAL"


def test_texture_atlas_and_udim():
    atlas = TextureAtlasDefinition("Atlas_Props_01", resolution=4096)
    atlas.add_sub_texture("prop_crate", [0.0, 0.0, 0.5, 0.5])
    atlas.add_sub_texture("prop_barrel", [0.5, 0.0, 1.0, 0.5])

    assert len(atlas.sub_textures) == 2
    assert atlas.get_uv_rect("prop_crate") == [0.0, 0.0, 0.5, 0.5]

    udim = UDIMDefinition()
    udim.add_tile(1002, resolution=4096)
    assert 1001 in udim.tile_ids
    assert 1002 in udim.tile_ids
