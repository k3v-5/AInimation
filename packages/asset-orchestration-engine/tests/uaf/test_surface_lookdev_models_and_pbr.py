"""
Tests for Surface Lookdev Models, PBR Channels, and Resolutions.
UAF-81.38 Sections 3, 4, 5, 7, 9, 11, 12, 147.
"""

from uaf.surface_lookdev.models.definition import (
    MaterialType38,
    ColorSpace38,
    NormalProfile38,
    PBRSurfaceProperties38,
    SurfaceLookdevSpecification,
)


def test_pbr_surface_properties_and_bounds():
    props_ok = PBRSurfaceProperties38(roughness=0.5, metallic=0.0, specular=0.5, emissive_intensity=0.0)
    assert props_ok.is_valid is True

    props_bad_rough = PBRSurfaceProperties38(roughness=1.2)  # > 1.0
    assert props_bad_rough.is_valid is False

    props_bad_metal = PBRSurfaceProperties38(metallic=-0.1)  # < 0.0
    assert props_bad_metal.is_valid is False

    props_bad_emissive = PBRSurfaceProperties38(emissive_intensity=-1.0)
    assert props_bad_emissive.is_valid is False


def test_surface_lookdev_specification_and_hashing():
    spec = SurfaceLookdevSpecification(
        surface_id="Surf_Test_Lookdev",
        material_type=MaterialType38.CERAMIC,
        properties=PBRSurfaceProperties38(roughness=0.2, metallic=0.0, specular=0.6),
        normal_profile=NormalProfile38.DIRECTX,
        color_space=ColorSpace38.SRGB,
        resolution_width=2048,
        resolution_height=2048,
        seed=445566,
    )

    assert spec.is_valid_resolution is True
    assert len(spec.definition_hash) == 64
    data = spec.to_dict()
    assert data["material_type"] == "CERAMIC"
    assert data["resolution_width"] == 2048

    bad_res_npot = SurfaceLookdevSpecification(
        surface_id="Surf_NPOT",
        material_type=MaterialType38.CERAMIC,
        resolution_width=1500,  # NPOT
        resolution_height=2048,
    )
    assert bad_res_npot.is_valid_resolution is False

    bad_res_small = SurfaceLookdevSpecification(
        surface_id="Surf_Small",
        material_type=MaterialType38.CERAMIC,
        resolution_width=128,  # < 256
        resolution_height=128,
    )
    assert bad_res_small.is_valid_resolution is False
