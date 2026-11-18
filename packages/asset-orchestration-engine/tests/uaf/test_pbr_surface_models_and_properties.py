"""
Tests for PBR Surface Models, Properties, and Resolution.
UAF-81.43 Sections 6, 11, 15, 24, 149.
"""

from uaf.pbr_surface.models.definition import (
    MaterialCategory43,
    UVStrategy43,
    TexelDensityProfile43,
    PBRProperties43,
    PBRSurfaceSpecification,
)


def test_pbr_properties_and_validity():
    props_ok = PBRProperties43(base_color_rgb=(0.5, 0.5, 0.5), metallic=0.5, roughness=0.5, emissive_intensity=1.0, resolution=2048)
    assert props_ok.is_valid is True

    props_bad_met = PBRProperties43(metallic=1.5)  # > 1.0
    assert props_bad_met.is_valid is False

    props_bad_rough = PBRProperties43(roughness=-0.1)  # < 0.0
    assert props_bad_rough.is_valid is False

    props_bad_res = PBRProperties43(resolution=1000)  # Not POT
    assert props_bad_res.is_valid is False

    props_low_res = PBRProperties43(resolution=128)  # < 256
    assert props_low_res.is_valid is False


def test_pbr_surface_specification_and_hashing():
    spec = PBRSurfaceSpecification(
        material_id="Mat_Test_Gold",
        category=MaterialCategory43.METAL,
        uv_strategy=UVStrategy43.SMART_PROJECT,
        texel_density=TexelDensityProfile43.HIGH,
        pbr=PBRProperties43(base_color_rgb=(1.0, 0.85, 0.5), metallic=1.0, roughness=0.15, emissive_intensity=0.0, resolution=2048),
        has_normal_map=True,
        has_ao_map=True,
        has_material_instance=True,
        seed=998877,
    )

    assert spec.is_valid_surface is True
    assert len(spec.definition_hash) == 64
    data = spec.to_dict()
    assert data["category"] == "METAL"
    assert data["pbr"]["metallic"] == 1.0

    bad_spec_map = PBRSurfaceSpecification(
        material_id="Mat_NoNormal",
        category=MaterialCategory43.METAL,
        has_normal_map=False,  # strictly required
    )
    assert bad_spec_map.is_valid_surface is False
