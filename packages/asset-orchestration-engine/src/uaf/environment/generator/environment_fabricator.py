"""
ProceduralEnvironmentFabricator generates all 6 canonical environments.
UAF-81.12 Sections 201, 202.
"""

from typing import List, Dict, Any, Tuple
from ..spatial.grid import GridProfile
from ..spatial.piece import ModularPiece
from ..topology.facility_graph import RoomType, RoomNode, BuildingFacilityGraph


class ProceduralEnvironmentFabricator:
    """
    Synthesizes complete environments matching all 6 canonical configurations from Section 202.
    """

    @classmethod
    def build_modular_room(cls, env_id: str = "Env_ModularRoom") -> Tuple[BuildingFacilityGraph, List[ModularPiece]]:
        """1. Modular Room (single room with modular boundary)."""
        graph = BuildingFacilityGraph(facility_id=env_id, floors_count=1)
        graph.add_room(RoomNode("room_01", RoomType.LAB, [8.0, 8.0, 3.0], 0, [], spawns_count=1))
        pieces = [ModularPiece.create_standard_floor(f"{env_id}_F0"), ModularPiece.create_standard_wall(f"{env_id}_W0")]
        return graph, pieces

    @classmethod
    def build_multi_room_building(cls, env_id: str = "Env_MultiRoom") -> Tuple[BuildingFacilityGraph, List[ModularPiece]]:
        """2. Multi-Room Building (office, corridor, server room)."""
        graph = BuildingFacilityGraph(facility_id=env_id, floors_count=1)
        graph.add_room(RoomNode("corridor_01", RoomType.CORRIDOR, [4.0, 16.0, 3.0], 0))
        graph.add_room(RoomNode("office_01", RoomType.OFFICE, [8.0, 8.0, 3.0], 0))
        graph.add_room(RoomNode("server_01", RoomType.SERVER_ROOM, [8.0, 8.0, 3.0], 0, has_objective=True))

        graph.connect_rooms("corridor_01", "office_01")
        graph.connect_rooms("corridor_01", "server_01")

        pieces = [ModularPiece.create_standard_floor(f"{env_id}_F"), ModularPiece.create_standard_wall(f"{env_id}_W")]
        return graph, pieces

    @classmethod
    def build_multi_floor_facility(cls, env_id: str = "Env_Facility_3F") -> Tuple[BuildingFacilityGraph, List[ModularPiece]]:
        """3. Multi-Floor Facility (3 floors with vertical stairs)."""
        graph = BuildingFacilityGraph(facility_id=env_id, floors_count=3)
        graph.add_room(RoomNode("F0_Lobby", RoomType.HALL, [12.0, 12.0, 4.0], 0))
        graph.add_room(RoomNode("F1_Labs", RoomType.LAB, [12.0, 12.0, 3.0], 1))
        graph.add_room(RoomNode("F2_Command", RoomType.CONTROL_ROOM, [12.0, 12.0, 3.0], 2, has_objective=True))

        graph.connect_rooms("F0_Lobby", "F1_Labs")
        graph.connect_rooms("F1_Labs", "F2_Command")
        graph.vertical_connections.extend(["Stairs_F0_F1", "Elevator_F1_F2"])

        pieces = [ModularPiece.create_standard_floor(f"{env_id}_F"), ModularPiece.create_standard_wall(f"{env_id}_W")]
        return graph, pieces

    @classmethod
    def build_combat_arena(cls, env_id: str = "Env_CombatArena") -> Tuple[BuildingFacilityGraph, List[ModularPiece]]:
        """4. Combat Arena (symmetric arena with boss encounter)."""
        graph = BuildingFacilityGraph(facility_id=env_id, floors_count=1)
        graph.add_room(RoomNode("arena_center", RoomType.ARENA, [30.0, 30.0, 8.0], 0, spawns_count=4, has_objective=True))
        pieces = [ModularPiece.create_standard_floor(f"{env_id}_F"), ModularPiece.create_standard_wall(f"{env_id}_W")]
        return graph, pieces

    @classmethod
    def build_outdoor_environment(cls, env_id: str = "Env_OutdoorValley") -> Tuple[BuildingFacilityGraph, List[ModularPiece]]:
        """5. Outdoor Environment (natural terrain & rock formations)."""
        graph = BuildingFacilityGraph(facility_id=env_id, floors_count=1)
        graph.add_room(RoomNode("valley_open", RoomType.OUTDOOR, [100.0, 100.0, 20.0], 0, spawns_count=2, has_objective=True))
        pieces = [ModularPiece(piece_id=f"{env_id}_TerrainTile", module_type="TERRAIN", dimensions=[20.0, 20.0, 2.0])]
        return graph, pieces

    @classmethod
    def build_hybrid_environment(cls, env_id: str = "Env_HybridBunker") -> Tuple[BuildingFacilityGraph, List[ModularPiece]]:
        """6. Hybrid Interior/Exterior Environment (underground bunker + outdoor landing pad)."""
        graph = BuildingFacilityGraph(facility_id=env_id, floors_count=2)
        graph.add_room(RoomNode("bunker_interior", RoomType.STORAGE, [16.0, 16.0, 4.0], 0))
        graph.add_room(RoomNode("landing_pad_exterior", RoomType.OUTDOOR, [32.0, 32.0, 10.0], 1, has_objective=True))

        graph.connect_rooms("bunker_interior", "landing_pad_exterior")
        graph.vertical_connections.append("Hangar_Ramp")

        pieces = [ModularPiece.create_standard_floor(f"{env_id}_F"), ModularPiece.create_standard_wall(f"{env_id}_W")]
        return graph, pieces
