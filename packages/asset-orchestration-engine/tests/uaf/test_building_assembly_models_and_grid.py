"""
Tests for Building Assembly Models, Scale, and Grid.
UAF-81.35 Sections 4, 5, 6, 7, 8, 12, 13, 23, 29, 30.
"""

from uaf.building_assembly.models.definition import (
    WorldType35,
    GridMode35,
    ModularKitComponent35,
    RoomType35,
    RoomDefinition35,
    BuildingAssemblySpecification,
)


def test_room_definition_and_scale_limits():
    room_ok = RoomDefinition35("R_01", RoomType35.OFFICE, [500.0, 400.0, 280.0])
    assert room_ok.is_valid_scale is True

    room_low_ceiling = RoomDefinition35("R_Low", RoomType35.OFFICE, [500.0, 400.0, 200.0])
    assert room_low_ceiling.is_valid_scale is False

    room_neg_dim = RoomDefinition35("R_Neg", RoomType35.OFFICE, [-500.0, 400.0, 300.0])
    assert room_neg_dim.is_valid_scale is False


def test_building_assembly_specification_and_hashing():
    r1 = RoomDefinition35("R_A", RoomType35.HALL, [600.0, 600.0, 350.0], connected_room_ids=["R_B"])
    r2 = RoomDefinition35("R_B", RoomType35.OFFICE, [400.0, 400.0, 300.0], connected_room_ids=["R_A"])
    spec = BuildingAssemblySpecification(
        world_id="World_Test_Office",
        world_type=WorldType35.URBAN,
        grid_mode=GridMode35.RECTANGULAR,
        cell_size_cm=100.0,
        rooms=[r1, r2],
        spawn_points_count=2,
        seed=12345,
    )

    assert spec.is_valid_grid is True
    assert len(spec.definition_hash) == 64
    data = spec.to_dict()
    assert data["world_type"] == "URBAN"
    assert len(data["rooms"]) == 2

    bad_grid = BuildingAssemblySpecification(
        world_id="World_BadGrid",
        world_type=WorldType35.URBAN,
        cell_size_cm=20.0,  # < 50.0 cm minimum
    )
    assert bad_grid.is_valid_grid is False
