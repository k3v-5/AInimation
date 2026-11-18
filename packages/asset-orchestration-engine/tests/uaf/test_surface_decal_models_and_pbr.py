"""
Tests for Surface Decal Models, Presets, and PBR.
UAF-81.34 Sections 4, 5, 6, 7, 23, 24, 28, 29.
"""

from uaf.surface_decal.models.definition import (
    MaterialFamily34,
    WearType34,
    DamageType34,
    SurfaceDecalItem,
    SurfaceAuthoringSpecification,
)


def test_surface_decal_item_and_validity():
    decal_ok = SurfaceDecalItem("Decal_Stripe", "STRIPE", [50.0, 50.0], 0.8)
    assert decal_ok.is_valid is True

    decal_bad_dim = SurfaceDecalItem("Decal_Bad", "STRIPE", [50.0, -10.0], 0.8)
    assert decal_bad_dim.is_valid is False

    decal_bad_op = SurfaceDecalItem("Decal_BadOp", "STRIPE", [50.0, 50.0], 1.5)
    assert decal_bad_op.is_valid is False


def test_surface_authoring_specification_and_hashing():
    spec = SurfaceAuthoringSpecification(
        surface_id="Surf_Spec_Ceramic",
        material_family=MaterialFamily34.CERAMIC,
        roughness_base=0.15,
        metallic_base=0.0,
        wear_types=[WearType34.SURFACE_WEAR],
        damage_types=[DamageType34.CRACK],
        seed=445566,
    )

    assert spec.is_valid_pbr is True
    assert len(spec.definition_hash) == 64
    data = spec.to_dict()
    assert data["material_family"] == "CERAMIC"
    assert data["roughness_base"] == 0.15

    bad_pbr = SurfaceAuthoringSpecification(
        surface_id="Surf_Bad_PBR",
        material_family=MaterialFamily34.CERAMIC,
        roughness_base=1.5,
    )
    assert bad_pbr.is_valid_pbr is False
