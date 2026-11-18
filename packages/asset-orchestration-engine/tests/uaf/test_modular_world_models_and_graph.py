"""
Tests for Modular World Models and Spatial Layout Graph.
UAF-81.19 Sections 3, 4, 8, 22, 23, 24, 25, 26, 32.
"""

from uaf.modular_world.models.definition import (
    EnvironmentType,
    ModularKitProfile,
    EnvironmentDefinition,
)
from uaf.modular_world.models.spatial_graph import (
    RoomPurpose,
    EnvironmentRoom,
    SpatialConnection,
    SpatialLayoutGraph,
)


def test_environment_definition_and_hashing():
    kit = ModularKitProfile("Kit_Industrial_Bunker", [100.0, 100.0, 300.0])
    env = EnvironmentDefinition("Env_Industrial_Complex", EnvironmentType.INDUSTRIAL, kit, seed=12345)

    assert env.environment_type == "INDUSTRIAL"
    assert env.kit_profile.grid_size_xyz == [100.0, 100.0, 300.0]
    assert len(env.definition_hash) == 64
    data = env.to_dict()
    assert data["environment_type"] == "INDUSTRIAL"


def test_spatial_layout_graph_connectivity():
    graph = SpatialLayoutGraph()
    r1 = EnvironmentRoom("Room_A", RoomPurpose.SPAWN, [600.0, 600.0, 300.0])
    r2 = EnvironmentRoom("Room_B", RoomPurpose.COMBAT, [800.0, 800.0, 300.0])
    r3 = EnvironmentRoom("Room_C", RoomPurpose.OBJECTIVE, [600.0, 600.0, 300.0])

    graph.add_room(r1)
    graph.add_room(r2)
    graph.add_room(r3)

    # Initially disconnected: Room_C has no path
    graph.add_connection("Room_A", "Room_B", "DOORWAY")
    assert graph.is_fully_connected() is False

    # Connect Room_B to Room_C -> now fully connected
    graph.add_connection("Room_B", "Room_C", "CORRIDOR")
    assert graph.is_fully_connected() is True
