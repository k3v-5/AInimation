"""
Tests for World Spatial Grid, Specification, and Modular Kit Connectors.
UAF-81.6 Sections 4, 5, 6, 7, 8, 10, 11.
"""

from uaf.world.spatial.world_grid import WorldGrid
from uaf.world.spatial.world_specification import WorldSpecification
from uaf.world.modular.connector import ConnectorType, ConnectorDefinition
from uaf.world.modular.module_definition import ModuleCategory, ModuleDefinition
from uaf.world.modular.modular_kit import ModularKitDefinition


def test_world_grid_snapping():
    grid = WorldGrid(snap_increment_meters=0.5, height_increment_meters=3.0, rotation_increment_degrees=90.0)
    snapped_pos = grid.snap_position([2.34, -4.71, 5.89])
    assert snapped_pos == [2.5, -4.5, 6.0]

    snapped_rot = grid.snap_rotation(87.4)
    assert snapped_rot == 90.0


def test_world_specification_hash_and_properties():
    spec = WorldSpecification(
        world_id="level_facility_01",
        seed=12345,
        dimensions=[150.0, 150.0, 40.0],
        theme="INDUSTRIAL",
        biome="SUBTERRANEAN_BUNKER",
    )
    assert len(spec.world_hash) == 64
    data = spec.to_dict()
    assert data["world_id"] == "level_facility_01"
    assert data["theme"] == "INDUSTRIAL"


def test_connector_compatibility():
    conn_a = ConnectorDefinition("c1", ConnectorType.WALL, size=[2.0, 3.0], compatibility_tags=["scifi", "interior"])
    conn_b = ConnectorDefinition("c2", ConnectorType.WALL, size=[2.0, 3.0], compatibility_tags=["interior"])
    conn_c = ConnectorDefinition("c3", ConnectorType.FLOOR, size=[2.0, 3.0])
    conn_d = ConnectorDefinition("c4", ConnectorType.WALL, size=[2.0, 3.0], compatibility_tags=["exterior"])

    assert conn_a.is_compatible_with(conn_b) is True
    assert conn_a.is_compatible_with(conn_c) is False  # Type mismatch
    assert conn_a.is_compatible_with(conn_d) is False  # Tag mismatch


def test_modular_kit_preloaded_scifi():
    kit = ModularKitDefinition.create_standard_scifi_kit("Kit_SciFi_Test")
    assert kit.kit_id == "Kit_SciFi_Test"
    assert "Mod_Floor_2x2" in kit.modules
    assert "Mod_Wall_2x3" in kit.modules
    assert "Mod_Door_2x3" in kit.modules
    assert "Mod_Stair_2x3" in kit.modules

    stairs = kit.find_by_category(ModuleCategory.STAIR)
    assert len(stairs) == 1
    assert stairs[0].dimensions == [2.0, 2.0, 3.0]
