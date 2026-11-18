"""
Tests for World Architecture Models and Graph.
UAF-81.24 Sections 3, 4, 8, 14, 70, 71, 171, 172.
"""

from uaf.world_architecture.models.definition import (
    BiomeType24,
    WorldBoundaryBounds,
    WorldGridCell,
    WorldDefinition24,
)
from uaf.world_architecture.models.graph import (
    ArchitecturalZoneType,
    ArchitecturalRoomNode,
    ArchitecturalWorldGraph,
)


def test_world_definition_bounds_and_hashing():
    bounds = WorldBoundaryBounds(-20000, 20000, -20000, 20000, 0, 5000)
    assert bounds.is_valid is True

    w_def = WorldDefinition24("World_NeoTokyo", bounds, BiomeType24.URBAN, seed=778899)
    assert w_def.primary_biome == "URBAN"
    assert len(w_def.definition_hash) == 64
    data = w_def.to_dict()
    assert data["primary_biome"] == "URBAN"


def test_architectural_graph_connectivity_and_critical_path():
    graph = ArchitecturalWorldGraph()
    r1 = ArchitecturalRoomNode("Room_A", ArchitecturalZoneType.CRITICAL_PATH)
    r2 = ArchitecturalRoomNode("Room_B", ArchitecturalZoneType.CRITICAL_PATH)
    r3 = ArchitecturalRoomNode("Room_C", ArchitecturalZoneType.OPTIONAL_ZONE)

    graph.add_room(r1)
    graph.add_room(r2)
    graph.add_room(r3)

    # Initially completely disconnected
    assert graph.is_fully_connected() is False
    assert graph.is_critical_path_valid() is False

    # Connect critical path rooms
    graph.add_connection("Room_A", "Room_B", "DOORWAY")
    assert graph.is_critical_path_valid() is True
    assert graph.is_fully_connected() is False

    # Connect optional room
    graph.add_connection("Room_B", "Room_C", "DOORWAY")
    assert graph.is_fully_connected() is True
