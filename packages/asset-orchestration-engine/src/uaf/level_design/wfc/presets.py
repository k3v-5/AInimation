"""
UAF-81.90: Modular Tile Presets and Catalog Factories.
Provides out-of-the-box modular tile sets for sci-fi interiors, dungeons, and multi-level structures.
"""

from typing import List

from uaf.level_design.core.contracts import (
    Direction2D,
    Direction3D,
    SocketType,
    RoomType,
    ModularTileDefinition,
)


def create_scifi_interior_catalog_2d() -> List[ModularTileDefinition]:
    """
    Standard 2D modular sci-fi interior tile set.
    Includes straight corridors, bends, junctions, rooms, entrance, exit, and solid wall fill.
    """
    tiles: List[ModularTileDefinition] = [
        # Solid Void / Wall
        ModularTileDefinition(
            tile_id="solid_wall",
            name="Solid Wall",
            room_type=RoomType.ROOM,
            sockets_2d={
                Direction2D.NORTH: SocketType.WALL,
                Direction2D.SOUTH: SocketType.WALL,
                Direction2D.EAST: SocketType.WALL,
                Direction2D.WEST: SocketType.WALL,
            },
            weight=3.0,
            mesh_path="/Game/ModularSciFi/Meshes/SM_Wall_Solid.SM_Wall_Solid",
        ),
        # Corridors Straight
        ModularTileDefinition(
            tile_id="corridor_ns",
            name="Corridor North-South",
            room_type=RoomType.CORRIDOR,
            sockets_2d={
                Direction2D.NORTH: SocketType.CORRIDOR,
                Direction2D.SOUTH: SocketType.CORRIDOR,
                Direction2D.EAST: SocketType.WALL,
                Direction2D.WEST: SocketType.WALL,
            },
            weight=2.0,
            mesh_path="/Game/ModularSciFi/Meshes/SM_Corridor_Straight_NS.SM_Corridor_Straight_NS",
        ),
        ModularTileDefinition(
            tile_id="corridor_ew",
            name="Corridor East-West",
            room_type=RoomType.CORRIDOR,
            sockets_2d={
                Direction2D.NORTH: SocketType.WALL,
                Direction2D.SOUTH: SocketType.WALL,
                Direction2D.EAST: SocketType.CORRIDOR,
                Direction2D.WEST: SocketType.CORRIDOR,
            },
            weight=2.0,
            mesh_path="/Game/ModularSciFi/Meshes/SM_Corridor_Straight_EW.SM_Corridor_Straight_EW",
        ),
        # Corridor Corners
        ModularTileDefinition(
            tile_id="corridor_corner_ne",
            name="Corridor Corner NE",
            room_type=RoomType.CORRIDOR,
            sockets_2d={
                Direction2D.NORTH: SocketType.CORRIDOR,
                Direction2D.SOUTH: SocketType.WALL,
                Direction2D.EAST: SocketType.CORRIDOR,
                Direction2D.WEST: SocketType.WALL,
            },
            weight=1.5,
            mesh_path="/Game/ModularSciFi/Meshes/SM_Corridor_Corner_NE.SM_Corridor_Corner_NE",
        ),
        ModularTileDefinition(
            tile_id="corridor_corner_nw",
            name="Corridor Corner NW",
            room_type=RoomType.CORRIDOR,
            sockets_2d={
                Direction2D.NORTH: SocketType.CORRIDOR,
                Direction2D.SOUTH: SocketType.WALL,
                Direction2D.EAST: SocketType.WALL,
                Direction2D.WEST: SocketType.CORRIDOR,
            },
            weight=1.5,
            mesh_path="/Game/ModularSciFi/Meshes/SM_Corridor_Corner_NW.SM_Corridor_Corner_NW",
        ),
        ModularTileDefinition(
            tile_id="corridor_corner_se",
            name="Corridor Corner SE",
            room_type=RoomType.CORRIDOR,
            sockets_2d={
                Direction2D.NORTH: SocketType.WALL,
                Direction2D.SOUTH: SocketType.CORRIDOR,
                Direction2D.EAST: SocketType.CORRIDOR,
                Direction2D.WEST: SocketType.WALL,
            },
            weight=1.5,
            mesh_path="/Game/ModularSciFi/Meshes/SM_Corridor_Corner_SE.SM_Corridor_Corner_SE",
        ),
        ModularTileDefinition(
            tile_id="corridor_corner_sw",
            name="Corridor Corner SW",
            room_type=RoomType.CORRIDOR,
            sockets_2d={
                Direction2D.NORTH: SocketType.WALL,
                Direction2D.SOUTH: SocketType.CORRIDOR,
                Direction2D.EAST: SocketType.WALL,
                Direction2D.WEST: SocketType.CORRIDOR,
            },
            weight=1.5,
            mesh_path="/Game/ModularSciFi/Meshes/SM_Corridor_Corner_SW.SM_Corridor_Corner_SW",
        ),
        # Corridor Junctions
        ModularTileDefinition(
            tile_id="corridor_t_north",
            name="Corridor T-Junction North (E, W, N)",
            room_type=RoomType.CORRIDOR,
            sockets_2d={
                Direction2D.NORTH: SocketType.CORRIDOR,
                Direction2D.SOUTH: SocketType.WALL,
                Direction2D.EAST: SocketType.CORRIDOR,
                Direction2D.WEST: SocketType.CORRIDOR,
            },
            weight=1.0,
            mesh_path="/Game/ModularSciFi/Meshes/SM_Corridor_T_North.SM_Corridor_T_North",
        ),
        ModularTileDefinition(
            tile_id="corridor_t_south",
            name="Corridor T-Junction South (E, W, S)",
            room_type=RoomType.CORRIDOR,
            sockets_2d={
                Direction2D.NORTH: SocketType.WALL,
                Direction2D.SOUTH: SocketType.CORRIDOR,
                Direction2D.EAST: SocketType.CORRIDOR,
                Direction2D.WEST: SocketType.CORRIDOR,
            },
            weight=1.0,
            mesh_path="/Game/ModularSciFi/Meshes/SM_Corridor_T_South.SM_Corridor_T_South",
        ),
        ModularTileDefinition(
            tile_id="corridor_cross_4way",
            name="Corridor 4-Way Cross",
            room_type=RoomType.CORRIDOR,
            sockets_2d={
                Direction2D.NORTH: SocketType.CORRIDOR,
                Direction2D.SOUTH: SocketType.CORRIDOR,
                Direction2D.EAST: SocketType.CORRIDOR,
                Direction2D.WEST: SocketType.CORRIDOR,
            },
            weight=0.8,
            mesh_path="/Game/ModularSciFi/Meshes/SM_Corridor_Cross_4Way.SM_Corridor_Cross_4Way",
        ),
        # Dead Ends
        ModularTileDefinition(
            tile_id="dead_end_north",
            name="Dead End Facing North",
            room_type=RoomType.DEAD_END,
            sockets_2d={
                Direction2D.NORTH: SocketType.CORRIDOR,
                Direction2D.SOUTH: SocketType.WALL,
                Direction2D.EAST: SocketType.WALL,
                Direction2D.WEST: SocketType.WALL,
            },
            weight=0.6,
            mesh_path="/Game/ModularSciFi/Meshes/SM_DeadEnd_North.SM_DeadEnd_North",
        ),
        ModularTileDefinition(
            tile_id="dead_end_south",
            name="Dead End Facing South",
            room_type=RoomType.DEAD_END,
            sockets_2d={
                Direction2D.NORTH: SocketType.WALL,
                Direction2D.SOUTH: SocketType.CORRIDOR,
                Direction2D.EAST: SocketType.WALL,
                Direction2D.WEST: SocketType.WALL,
            },
            weight=0.6,
            mesh_path="/Game/ModularSciFi/Meshes/SM_DeadEnd_South.SM_DeadEnd_South",
        ),
        ModularTileDefinition(
            tile_id="dead_end_east",
            name="Dead End Facing East",
            room_type=RoomType.DEAD_END,
            sockets_2d={
                Direction2D.NORTH: SocketType.WALL,
                Direction2D.SOUTH: SocketType.WALL,
                Direction2D.EAST: SocketType.CORRIDOR,
                Direction2D.WEST: SocketType.WALL,
            },
            weight=0.6,
            mesh_path="/Game/ModularSciFi/Meshes/SM_DeadEnd_East.SM_DeadEnd_East",
        ),
        ModularTileDefinition(
            tile_id="dead_end_west",
            name="Dead End Facing West",
            room_type=RoomType.DEAD_END,
            sockets_2d={
                Direction2D.NORTH: SocketType.WALL,
                Direction2D.SOUTH: SocketType.WALL,
                Direction2D.EAST: SocketType.WALL,
                Direction2D.WEST: SocketType.CORRIDOR,
            },
            weight=0.6,
            mesh_path="/Game/ModularSciFi/Meshes/SM_DeadEnd_West.SM_DeadEnd_West",
        ),
        # Hub & Rooms
        ModularTileDefinition(
            tile_id="room_hub",
            name="Central Hub Room",
            room_type=RoomType.HUB,
            sockets_2d={
                Direction2D.NORTH: SocketType.CORRIDOR,
                Direction2D.SOUTH: SocketType.CORRIDOR,
                Direction2D.EAST: SocketType.CORRIDOR,
                Direction2D.WEST: SocketType.CORRIDOR,
            },
            weight=0.5,
            mesh_path="/Game/ModularSciFi/Meshes/SM_Room_Hub.SM_Room_Hub",
        ),
        ModularTileDefinition(
            tile_id="room_arena",
            name="Combat Arena",
            room_type=RoomType.ARENA,
            sockets_2d={
                Direction2D.NORTH: SocketType.CORRIDOR,
                Direction2D.SOUTH: SocketType.CORRIDOR,
                Direction2D.EAST: SocketType.WALL,
                Direction2D.WEST: SocketType.WALL,
            },
            weight=0.7,
            mesh_path="/Game/ModularSciFi/Meshes/SM_Room_Arena.SM_Room_Arena",
        ),
        ModularTileDefinition(
            tile_id="entrance_chamber",
            name="Level Entrance Chamber",
            room_type=RoomType.ENTRANCE,
            sockets_2d={
                Direction2D.NORTH: SocketType.CORRIDOR,
                Direction2D.SOUTH: SocketType.WALL,
                Direction2D.EAST: SocketType.WALL,
                Direction2D.WEST: SocketType.WALL,
            },
            weight=0.3,
            mesh_path="/Game/ModularSciFi/Meshes/SM_Room_Entrance.SM_Room_Entrance",
        ),
        ModularTileDefinition(
            tile_id="exit_chamber",
            name="Level Extraction Chamber",
            room_type=RoomType.EXIT,
            sockets_2d={
                Direction2D.NORTH: SocketType.WALL,
                Direction2D.SOUTH: SocketType.CORRIDOR,
                Direction2D.EAST: SocketType.WALL,
                Direction2D.WEST: SocketType.WALL,
            },
            weight=0.3,
            mesh_path="/Game/ModularSciFi/Meshes/SM_Room_Exit.SM_Room_Exit",
        ),
    ]
    return tiles


def create_scifi_multilevel_catalog_3d() -> List[ModularTileDefinition]:
    """
    Standard 3D modular sci-fi interior tile set with vertical connectivity.
    """
    tiles: List[ModularTileDefinition] = [
        # Solid 3D Cube
        ModularTileDefinition(
            tile_id="solid_block_3d",
            name="Solid 3D Block",
            room_type=RoomType.ROOM,
            sockets_3d={
                Direction3D.NORTH: SocketType.WALL,
                Direction3D.SOUTH: SocketType.WALL,
                Direction3D.EAST: SocketType.WALL,
                Direction3D.WEST: SocketType.WALL,
                Direction3D.UP: SocketType.WALL,
                Direction3D.DOWN: SocketType.WALL,
            },
            weight=3.0,
            mesh_path="/Game/ModularSciFi/Meshes/SM_Block_Solid.SM_Block_Solid",
        ),
        # Flat Corridor Level 0/1
        ModularTileDefinition(
            tile_id="corridor_3d_ns",
            name="Corridor 3D North-South",
            room_type=RoomType.CORRIDOR,
            sockets_3d={
                Direction3D.NORTH: SocketType.CORRIDOR,
                Direction3D.SOUTH: SocketType.CORRIDOR,
                Direction3D.EAST: SocketType.WALL,
                Direction3D.WEST: SocketType.WALL,
                Direction3D.UP: SocketType.WALL,
                Direction3D.DOWN: SocketType.WALL,
            },
            weight=2.0,
            mesh_path="/Game/ModularSciFi/Meshes/SM_Corridor_3D_NS.SM_Corridor_3D_NS",
        ),
        ModularTileDefinition(
            tile_id="corridor_3d_ew",
            name="Corridor 3D East-West",
            room_type=RoomType.CORRIDOR,
            sockets_3d={
                Direction3D.NORTH: SocketType.WALL,
                Direction3D.SOUTH: SocketType.WALL,
                Direction3D.EAST: SocketType.CORRIDOR,
                Direction3D.WEST: SocketType.CORRIDOR,
                Direction3D.UP: SocketType.WALL,
                Direction3D.DOWN: SocketType.WALL,
            },
            weight=2.0,
            mesh_path="/Game/ModularSciFi/Meshes/SM_Corridor_3D_EW.SM_Corridor_3D_EW",
        ),
        # Stairwell Connecting Down to Up
        ModularTileDefinition(
            tile_id="stairwell_connector",
            name="Stairwell Vertical Connector",
            room_type=RoomType.CORRIDOR,
            sockets_3d={
                Direction3D.NORTH: SocketType.CORRIDOR,
                Direction3D.SOUTH: SocketType.WALL,
                Direction3D.EAST: SocketType.WALL,
                Direction3D.WEST: SocketType.WALL,
                Direction3D.UP: SocketType.OPEN,
                Direction3D.DOWN: SocketType.OPEN,
            },
            weight=1.0,
            mesh_path="/Game/ModularSciFi/Meshes/SM_Stairwell_Connector.SM_Stairwell_Connector",
        ),
        # Elevator Shaft
        ModularTileDefinition(
            tile_id="elevator_shaft",
            name="Elevator Shaft Unit",
            room_type=RoomType.ELEVATOR,
            sockets_3d={
                Direction3D.NORTH: SocketType.WALL,
                Direction3D.SOUTH: SocketType.WALL,
                Direction3D.EAST: SocketType.WALL,
                Direction3D.WEST: SocketType.CORRIDOR,
                Direction3D.UP: SocketType.OPEN,
                Direction3D.DOWN: SocketType.OPEN,
            },
            weight=0.8,
            mesh_path="/Game/ModularSciFi/Meshes/SM_Elevator_Shaft.SM_Elevator_Shaft",
        ),
    ]
    return tiles
