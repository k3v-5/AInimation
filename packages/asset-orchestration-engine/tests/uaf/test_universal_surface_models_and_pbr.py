"""
Tests for Universal Surface Models, PBR ranges, and Texture Resolution.
UAF-81.52 Sections 4, 5, 55, 143, 145.
"""

from uaf.universal_surface.models.definition import (
    SurfaceType52,
    PBRChannelType52,
    TextureResolution52,
    PBRSurfaceProperties52,
    UniversalSurfaceSpecification,
)


def test_pbr_properties_and_resolution_validity():
    props_ok = PBRSurfaceProperties52(base_color_rgb=(0.8, 0.8, 0.8), metallic=0.9, roughness=0.2, specular=0.5, opacity=1.0)
    assert props_ok.is_valid is True

    props_neg = PBRSurfaceProperties52(metallic=-0.1)
    assert props_neg.is_valid is False

    props_high = PBRSurfaceProperties52(roughness=1.2)
    assert props_high.is_valid is False

    res_ok = TextureResolution52(width_px=2048, height_px=2048)
    assert res_ok.is_power_of_two is True

    res_non_pot = TextureResolution52(width_px=1920, height_px=1080)
    assert res_non_pot.is_power_of_two is False

    res_too_small = TextureResolution52(width_px=64, height_px=64)  # < 128
    assert res_too_small.is_power_of_two is False


def test_universal_surface_specification_and_hashing():
    spec = UniversalSurfaceSpecification(
        surface_id="Surf_Test_Ceramic",
        surface_type=SurfaceType52.CERAMIC,
        properties=PBRSurfaceProperties52(base_color_rgb=(0.9, 0.9, 0.92), metallic=0.0, roughness=0.15, specular=0.5, opacity=1.0),
        resolution=TextureResolution52(width_px=1024, height_px=1024),
        has_normal=True,
        has_roughness=True,
        has_metallic=True,
        has_ambient_occlusion=True,
        has_material_instance=True,
        seed=24680,
    )

    assert spec.is_valid_surface is True
    assert len(spec.definition_hash) == 64
    data = spec.to_dict()
    assert data["surface_type"] == "CERAMIC"
    assert data["resolution"]["width_px"] == 1024

    bad_spec_normal = UniversalSurfaceSpecification(
        surface_id="Surf_NoNormal",
        surface_type=SurfaceType52.CERAMIC,
        has_normal=False,
    )
    assert bad_spec_normal.is_valid_surface is False
