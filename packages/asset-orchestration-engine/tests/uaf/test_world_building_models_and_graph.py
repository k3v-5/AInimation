"""
Tests for World Building Models and Blockout Graph.
UAF-81.28 Sections 3, 4, 5, 7, 8, 9, 10, 25, 26, 40, 124.
"""

from uaf.world_building.models.definition import (
    WorldType28,
    ModularCategory,
    SocketType28,
    ModularBlockDefinition,
    PlayableWorldDefinition,
)
from uaf.world_building.models.graph import (
    BlockoutZoneNode,
    BlockoutWorldGraph,
)


def test_playable_world_definition_grid_and_hashing():
    block = ModularBlockDefinition("Wall_Std", ModularCategory.WALL, [400.0, 20.0, 300.0], [SocketType28.WALL_CONNECTOR])
    w_def = PlayableWorldDefinition("World_Test_Grid", WorldType28.FACILITY, grid_size_cm=400.0, module_blocks=[block], seed=12345)

    assert w_def.is_valid_grid is True
    assert len(w_def.definition_hash) == 64
    data = w_def.to_dict()
    assert data["grid_size_cm"] == 400.0

    bad_wdef = PlayableWorldDefinition("World_Bad_Grid", WorldType28.FACILITY, grid_size_cm=50.0)
    assert bad_wdef.is_valid_grid is False


def test_blockout_world_graph_connectivity_and_critical_path():
    graph = BlockoutWorldGraph()
    z1 = BlockoutZoneNode("Zone_A", "Entryway", [800.0, 800.0, 300.0], is_critical_path=True)
    z2 = BlockoutZoneNode("Zone_B", "Boss Chamber", [1600.0, 1600.0, 600.0], is_critical_path=True)
    z3 = BlockoutZoneNode("Zone_C", "Secret Alcove", [400.0, 400.0, 300.0], is_critical_path=False)

    graph.add_zone(z1)
    graph.add_zone(z2)
    graph.add_zone(z3)

    assert graph.is_fully_connected() is False
    assert graph.is_critical_path_connected() is False

    # Connect critical path
    graph.add_connection("Zone_A", "Zone_B", "CORRIDOR")
    assert graph.is_critical_path_connected() is True
    assert graph.is_fully_connected() is False

    # Connect secret alcove
    graph.add_connection("Zone_B", "Zone_C", "CRACKED_WALL")
    assert graph.is_fully_connected() is True
