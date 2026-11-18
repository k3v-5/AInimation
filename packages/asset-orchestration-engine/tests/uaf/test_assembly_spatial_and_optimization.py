"""
Tests for Spatial Pivot, Sockets, LOD Chain, and Nanite Policies.
UAF-81.8 Sections 10, 11, 13, 17, 18, 20, 21, 28, 29.
"""

from uaf.assembly.spatial.pivot import PivotType, OriginPolicy, PivotDefinition
from uaf.assembly.spatial.socket import SocketType, RuntimeSocketDefinition
from uaf.assembly.optimization.lod_policy import NanitePolicy, LODLevel, LODChain


def test_pivot_definition_and_origin_policy():
    pivot = PivotDefinition(
        pivot_type=PivotType.BOTTOM,
        position=[0.0, 0.0, 0.0],
        origin_policy=OriginPolicy.FEET_ROOT,
    )
    assert pivot.pivot_type == PivotType.BOTTOM
    assert pivot.origin_policy == OriginPolicy.FEET_ROOT
    data = pivot.to_dict()
    assert data["pivot_type"] == "BOTTOM"
    assert data["origin_policy"] == "FEET_ROOT"


def test_runtime_socket_definition():
    socket = RuntimeSocketDefinition(
        socket_id="Socket_Weapon_R",
        parent_attachment="hand_R",
        position=[0.05, 0.02, 0.0],
        rotation=[0.0, 90.0, 0.0],
        socket_type=SocketType.WEAPON,
    )
    assert socket.socket_id == "Socket_Weapon_R"
    assert socket.parent_attachment == "hand_R"
    assert socket.socket_type == SocketType.WEAPON
    data = socket.to_dict()
    assert data["socket_type"] == "WEAPON"


def test_lod_chain_exponential_reduction():
    chain = LODChain.create_standard_chain(base_triangles=10000, lod_count=4)
    assert len(chain.lods) == 4
    # LOD0 = 10000, LOD1 = 5000, LOD2 = 2500, LOD3 = 1200
    assert chain.lods[0].triangle_count == 10000
    assert chain.lods[1].triangle_count == 5000
    assert chain.lods[2].triangle_count == 2500
    assert chain.lods[3].triangle_count == 1200
    assert chain.lods[1].screen_size == 0.5


def test_nanite_eligibility_rules():
    # Dense static mesh -> Eligible
    assert NanitePolicy.evaluate_nanite_eligibility(is_static=True, triangle_count=5000, has_skinning=False) is True

    # Low-poly static mesh -> Not eligible
    assert NanitePolicy.evaluate_nanite_eligibility(is_static=True, triangle_count=200, has_skinning=False) is False

    # Skeletal / deformed mesh -> Not eligible
    assert NanitePolicy.evaluate_nanite_eligibility(is_static=False, triangle_count=10000, has_skinning=True) is False
