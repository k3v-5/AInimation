"""
Tests for Surface Authoring Models, Regions, Compositions, and Region Graph.
UAF-81.11 Sections 4, 5, 6, 7, 163, 164.
"""

from uaf.surface_authoring.models.regions import (
    MaterialFamilyType,
    MaterialLayerBlendMode,
    SurfaceRegion,
    MaterialCompositionLayer,
    MaterialRegionGraph,
)


def test_surface_region_and_composition_layer():
    reg = SurfaceRegion(
        region_id="reg_tactical_vest",
        material_family=MaterialFamilyType.FABRIC,
        roughness_range=[0.7, 0.9],
        metallic=0.0,
    )
    assert reg.material_family == MaterialFamilyType.FABRIC
    assert reg.roughness_range == [0.7, 0.9]

    layer = MaterialCompositionLayer(
        layer_id="layer_dirt",
        material_family=MaterialFamilyType.ORGANIC,
        mask_id="mask_crevice_dirt",
        blend_mode=MaterialLayerBlendMode.MASK_BLEND,
        opacity=0.8,
    )
    assert layer.blend_mode == MaterialLayerBlendMode.MASK_BLEND
    assert layer.opacity == 0.8


def test_material_region_graph_serialization_and_hash():
    graph = MaterialRegionGraph(asset_id="Asset_SciFi_Rifle")
    graph.add_region(
        SurfaceRegion("reg_barrel", MaterialFamilyType.METAL, metallic=1.0)
    )
    graph.add_region(
        SurfaceRegion("reg_stock", MaterialFamilyType.PLASTIC, metallic=0.0)
    )
    graph.add_composition_layer(
        "reg_barrel",
        MaterialCompositionLayer("comp_heat_stain", MaterialFamilyType.ENERGY, "mask_muzzle_heat"),
    )

    assert len(graph.regions) == 2
    assert "reg_barrel" in graph.compositions
    assert len(graph.graph_hash) == 64

    data = graph.to_dict()
    assert data["asset_id"] == "Asset_SciFi_Rifle"
    assert "reg_barrel" in data["regions"]
    assert len(data["compositions"]["reg_barrel"]) == 1
