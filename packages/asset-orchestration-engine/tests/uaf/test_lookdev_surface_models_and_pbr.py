"""
Tests for Lookdev Surface Models, PBR Properties, and Resolution.
UAF-81.46 Sections 4, 5, 6, 8, 114.
"""

from uaf.lookdev_surface.models.definition import (
    MaterialFamily46,
    LookdevQualityTier46,
    SurfacePBRProperties46,
    LookdevSurfaceSpecification,
)


def test_surface_pbr_properties_and_validity():
    pbr_ok = SurfacePBRProperties46(base_color_rgb=(0.8, 0.8, 0.8), metallic=0.0, roughness=0.5, ao=1.0, emission=0.0, resolution=2048)
    assert pbr_ok.is_valid is True

    pbr_bad_metallic = SurfacePBRProperties46(metallic=1.5)  # > 1.0
    assert pbr_bad_metallic.is_valid is False

    pbr_bad_roughness = SurfacePBRProperties46(roughness=-0.1)  # < 0.0
    assert pbr_bad_roughness.is_valid is False

    pbr_bad_emission = SurfacePBRProperties46(emission=-1.0)  # < 0.0
    assert pbr_bad_emission.is_valid is False

    pbr_non_pot = SurfacePBRProperties46(resolution=1000)  # not power of two
    assert pbr_non_pot.is_valid is False

    pbr_small = SurfacePBRProperties46(resolution=128)  # < 256
    assert pbr_small.is_valid is False


def test_lookdev_surface_specification_and_hashing():
    pbr = SurfacePBRProperties46(base_color_rgb=(0.95, 0.95, 0.95), metallic=1.0, roughness=0.2, ao=1.0, emission=0.0, resolution=2048)
    spec = LookdevSurfaceSpecification(
        surface_id="Surf_Test_Steel",
        material_family=MaterialFamily46.METAL,
        quality_tier=LookdevQualityTier46.HIGH,
        pbr=pbr,
        has_normal=True,
        has_displacement=True,
        has_material_instance=True,
        seed=778899,
    )

    assert spec.is_valid_surface is True
    assert len(spec.definition_hash) == 64
    data = spec.to_dict()
    assert data["material_family"] == "METAL"
    assert data["pbr"]["metallic"] == 1.0

    bad_spec_normal = LookdevSurfaceSpecification(
        surface_id="Surf_NoNormal",
        material_family=MaterialFamily46.METAL,
        has_normal=False,
    )
    assert bad_spec_normal.is_valid_surface is False
