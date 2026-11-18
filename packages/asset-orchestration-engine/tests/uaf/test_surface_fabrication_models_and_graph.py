"""
Tests for Surface Fabrication Models, Profiles, and Material Graphs.
UAF-81.15 Sections 4, 5, 6, 7, 9, 10, 33.
"""

from uaf.surface_fabrication.models.profile import (
    MaterialClassification,
    MaterialDomain,
    SurfaceWearType,
    SurfaceProfile,
)
from uaf.surface_fabrication.models.graph import (
    MaterialParameterType,
    MaterialGraphContract,
)


def test_surface_profile_and_hashing():
    prof = SurfaceProfile(
        surface_id="Surf_Carbon_Fiber",
        surface_type="COMPOSITE",
        material_classification=MaterialClassification.OPAQUE,
        roughness_range=[0.2, 0.5],
        metallic_range=[0.0, 0.0],
        base_color_hex="#1A1A1A",
        wears=[SurfaceWearType.SCRATCH],
        seed=102030,
    )
    assert prof.surface_type == "COMPOSITE"
    assert len(prof.wears) == 1
    assert len(prof.profile_hash) == 64
    data = prof.to_dict()
    assert data["material_classification"] == "OPAQUE"


def test_material_graph_contract():
    graph = MaterialGraphContract(
        graph_id="Graph_ProceduralTile",
        master_material_id="M_Master_TiledPBR",
        parameters={"TilingU": 8.0, "TilingV": 8.0},
        material_functions=["Triplanar", "NormalBlend"],
        has_triplanar=True,
    )
    assert graph.has_triplanar is True
    assert len(graph.contract_hash) == 64
    data = graph.to_dict()
    assert data["master_material_id"] == "M_Master_TiledPBR"
