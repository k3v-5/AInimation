"""
Tests for Surface Material Models and PBR Ranges.
UAF-81.30 Sections 4, 5, 6, 7, 8, 10, 11, 13, 14.
"""

from uaf.surface_material.models.definition import (
    SurfaceType30,
    MaterialModel30,
    ColorSpace30,
    SurfaceMapItem,
    ProductionSurfaceDefinition,
)


def test_surface_map_item_power_of_two():
    map_ok = SurfaceMapItem("T_Metal_BC", "BASE_COLOR", 2048, ColorSpace30.SRGB)
    assert map_ok.is_power_of_two is True

    map_bad = SurfaceMapItem("T_Metal_Bad", "BASE_COLOR", 720, ColorSpace30.SRGB)
    assert map_bad.is_power_of_two is False

    map_tiny = SurfaceMapItem("T_Metal_Tiny", "BASE_COLOR", 128, ColorSpace30.SRGB)
    assert map_tiny.is_power_of_two is False


def test_production_surface_definition_and_hashing():
    maps = [
        SurfaceMapItem("T_Base_BC", "BASE_COLOR", 2048, ColorSpace30.SRGB),
        SurfaceMapItem("T_Base_N", "NORMAL", 2048, ColorSpace30.NORMAL_MAP),
        SurfaceMapItem("T_Base_ORM", "ORM", 2048, ColorSpace30.LINEAR),
    ]
    s_def = ProductionSurfaceDefinition(
        surface_id="Surf_Carbon_Spec",
        surface_type=SurfaceType30.CARBON,
        material_model=MaterialModel30.PBR_METALLIC_ROUGHNESS,
        maps=maps,
        roughness_base=0.35,
        metallic_base=0.0,
        seed=654321,
    )

    assert s_def.is_valid_pbr is True
    assert len(s_def.definition_hash) == 64
    data = s_def.to_dict()
    assert data["material_model"] == "PBR_METALLIC_ROUGHNESS"
    assert data["roughness_base"] == 0.35

    bad_pbr = ProductionSurfaceDefinition(
        surface_id="Surf_Bad_PBR",
        surface_type=SurfaceType30.CARBON,
        material_model=MaterialModel30.PBR_METALLIC_ROUGHNESS,
        roughness_base=1.5,
    )
    assert bad_pbr.is_valid_pbr is False
