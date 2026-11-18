"""
BuildingAssemblyFabricationPlatform manufactures canonical Golden Worlds matching Section 133.
UAF-81.35 Sections 133, 136.
"""

from typing import Tuple, List, Dict, Any
from ..models.definition import (
    BuildingAssemblySpecification,
    WorldType35,
    GridMode35,
    RoomType35,
    RoomDefinition35,
)


class BuildingAssemblyFabricationPlatform:
    """
    Synthesizes complete, production-grade modular environments, buildings, blockouts, and world assemblies.
    """

    @classmethod
    def build_golden_room(cls, world_id: str = "World_Gold_Room") -> Tuple[BuildingAssemblySpecification, str]:
        """1. GOLDEN_ROOM (Section 133: single modular room, validated walls, floor, ceiling, spawn)."""
        room = RoomDefinition35("Room_Main", RoomType35.OFFICE, [500.0, 500.0, 300.0], [0.0, 0.0, 0.0])
        spec = BuildingAssemblySpecification(world_id, WorldType35.INTERIOR, GridMode35.RECTANGULAR, cell_size_cm=100.0, rooms=[room], spawn_points_count=1)
        return spec, f"/Game/Environments/Levels/{world_id}"

    @classmethod
    def build_golden_corridor(cls, world_id: str = "World_Gold_Corridor") -> Tuple[BuildingAssemblySpecification, str]:
        """2. GOLDEN_CORRIDOR (Section 133: linear modular connector, double ended, lighting slots)."""
        c1 = RoomDefinition35("Corr_01", RoomType35.CORRIDOR, [300.0, 1000.0, 300.0], [0.0, 0.0, 0.0], connected_room_ids=["Corr_02"])
        c2 = RoomDefinition35("Corr_02", RoomType35.CORRIDOR, [300.0, 1000.0, 300.0], [0.0, 1000.0, 0.0], connected_room_ids=["Corr_01"])
        spec = BuildingAssemblySpecification(world_id, WorldType35.INTERIOR, GridMode35.RECTANGULAR, cell_size_cm=100.0, rooms=[c1, c2], spawn_points_count=2)
        return spec, f"/Game/Environments/Levels/{world_id}"

    @classmethod
    def build_golden_building(cls, world_id: str = "World_Gold_Building") -> Tuple[BuildingAssemblySpecification, str]:
        """3. GOLDEN_BUILDING (Section 133: multi-room connected office/facility structure, staircase)."""
        r1 = RoomDefinition35("Lobby", RoomType35.HALL, [800.0, 800.0, 400.0], [0.0, 0.0, 0.0], connected_room_ids=["Office_A", "Office_B"])
        r2 = RoomDefinition35("Office_A", RoomType35.OFFICE, [400.0, 400.0, 300.0], [800.0, 0.0, 0.0], connected_room_ids=["Lobby"])
        r3 = RoomDefinition35("Office_B", RoomType35.OFFICE, [400.0, 400.0, 300.0], [0.0, 800.0, 0.0], connected_room_ids=["Lobby"])
        spec = BuildingAssemblySpecification(world_id, WorldType35.URBAN, GridMode35.RECTANGULAR, cell_size_cm=100.0, rooms=[r1, r2, r3], spawn_points_count=2)
        return spec, f"/Game/Environments/Levels/{world_id}"

    @classmethod
    def build_golden_facility(cls, world_id: str = "World_Gold_Facility") -> Tuple[BuildingAssemblySpecification, str]:
        """4. GOLDEN_FACILITY (Section 133: industrial/military complex with labs, storage, and command center)."""
        cmd = RoomDefinition35("Cmd_Center", RoomType35.COMMAND_CENTER, [1200.0, 1200.0, 500.0], [0.0, 0.0, 0.0], connected_room_ids=["Lab_Main", "Storage_Bay"])
        lab = RoomDefinition35("Lab_Main", RoomType35.LAB, [600.0, 800.0, 350.0], [1200.0, 0.0, 0.0], connected_room_ids=["Cmd_Center"])
        stg = RoomDefinition35("Storage_Bay", RoomType35.STORAGE, [800.0, 800.0, 400.0], [0.0, 1200.0, 0.0], connected_room_ids=["Cmd_Center"])
        spec = BuildingAssemblySpecification(world_id, WorldType35.FACILITY, GridMode35.RECTANGULAR, cell_size_cm=100.0, rooms=[cmd, lab, stg], spawn_points_count=4)
        return spec, f"/Game/Environments/Levels/{world_id}"

    @classmethod
    def build_golden_combat_area(cls, world_id: str = "World_Gold_CombatArea") -> Tuple[BuildingAssemblySpecification, str]:
        """5. GOLDEN_COMBAT_AREA (Section 133: combat space with cover, line of sight, dynamic obstacles)."""
        arena = RoomDefinition35("Arena_Main", RoomType35.COMBAT_ARENA, [2000.0, 2000.0, 600.0], [0.0, 0.0, 0.0], connected_room_ids=["Flank_Left", "Flank_Right"])
        flank_l = RoomDefinition35("Flank_Left", RoomType35.CORRIDOR, [400.0, 1200.0, 300.0], [-400.0, 400.0, 0.0], connected_room_ids=["Arena_Main"])
        flank_r = RoomDefinition35("Flank_Right", RoomType35.CORRIDOR, [400.0, 1200.0, 300.0], [2000.0, 400.0, 0.0], connected_room_ids=["Arena_Main"])
        spec = BuildingAssemblySpecification(world_id, WorldType35.MILITARY, GridMode35.RECTANGULAR, cell_size_cm=100.0, rooms=[arena, flank_l, flank_r], spawn_points_count=6)
        return spec, f"/Game/Environments/Levels/{world_id}"

    @classmethod
    def build_golden_city_block(cls, world_id: str = "World_Gold_CityBlock") -> Tuple[BuildingAssemblySpecification, str]:
        """6. GOLDEN_CITY_BLOCK (Section 133: urban grid assembly, street intersections, exterior blockouts)."""
        plaza = RoomDefinition35("Plaza_Central", RoomType35.HALL, [2500.0, 2500.0, 1000.0], [0.0, 0.0, 0.0], connected_room_ids=["Street_North", "Street_South"])
        str_n = RoomDefinition35("Street_North", RoomType35.CORRIDOR, [800.0, 2000.0, 800.0], [850.0, 2500.0, 0.0], connected_room_ids=["Plaza_Central"])
        str_s = RoomDefinition35("Street_South", RoomType35.CORRIDOR, [800.0, 2000.0, 800.0], [850.0, -2000.0, 0.0], connected_room_ids=["Plaza_Central"])
        spec = BuildingAssemblySpecification(world_id, WorldType35.CITY, GridMode35.RECTANGULAR, cell_size_cm=100.0, rooms=[plaza, str_n, str_s], spawn_points_count=8)
        return spec, f"/Game/Environments/Levels/{world_id}"
