"""
ModularWorldFabricationPlatform manufactures complete 3D environments across all 8 canonical archetypes.
UAF-81.19 Sections 182, 213, 214.
"""

from typing import Tuple, List, Dict, Any
from ..models.definition import EnvironmentDefinition, EnvironmentType, ModularKitProfile
from ..models.spatial_graph import SpatialLayoutGraph, EnvironmentRoom, RoomPurpose, SpatialConnection


class ModularWorldFabricationPlatform:
    """
    Fabricates fully-connected, production-ready modular environments matching Section 213 archetypes.
    """

    @classmethod
    def build_room_environment(cls, env_id: str = "Env_SingleRoom", seed: int = 101) -> Tuple[EnvironmentDefinition, SpatialLayoutGraph, int, int]:
        """1. A Room."""
        env_def = EnvironmentDefinition(env_id, EnvironmentType.INTERIOR, seed=seed)
        graph = SpatialLayoutGraph()
        graph.add_room(EnvironmentRoom("Room_Main", RoomPurpose.SAFE, [600.0, 600.0, 300.0]))
        return env_def, graph, 24, 8

    @classmethod
    def build_building_environment(cls, env_id: str = "Env_Building", seed: int = 202) -> Tuple[EnvironmentDefinition, SpatialLayoutGraph, int, int]:
        """2. A Building (Multi-room, 2-floor)."""
        env_def = EnvironmentDefinition(env_id, EnvironmentType.URBAN, seed=seed)
        graph = SpatialLayoutGraph()
        graph.add_room(EnvironmentRoom("Room_Lobby", RoomPurpose.TRANSITION, [800.0, 800.0, 300.0], floor_level=0))
        graph.add_room(EnvironmentRoom("Room_Office", RoomPurpose.LOOT, [600.0, 600.0, 300.0], floor_level=1))
        graph.add_connection("Room_Lobby", "Room_Office", "STAIR")
        return env_def, graph, 68, 22

    @classmethod
    def build_facility_environment(cls, env_id: str = "Env_Facility", seed: int = 303) -> Tuple[EnvironmentDefinition, SpatialLayoutGraph, int, int]:
        """3. A Facility (Multi-zone research base)."""
        env_def = EnvironmentDefinition(env_id, EnvironmentType.INDUSTRIAL, seed=seed)
        graph = SpatialLayoutGraph()
        graph.add_room(EnvironmentRoom("Room_Airlock", RoomPurpose.SPAWN, [400.0, 400.0, 300.0]))
        graph.add_room(EnvironmentRoom("Room_Lab", RoomPurpose.OBJECTIVE, [1200.0, 800.0, 300.0]))
        graph.add_room(EnvironmentRoom("Room_Storage", RoomPurpose.STORAGE, [600.0, 600.0, 300.0]))
        graph.add_connection("Room_Airlock", "Room_Lab", "DOORWAY")
        graph.add_connection("Room_Lab", "Room_Storage", "CORRIDOR")
        return env_def, graph, 140, 45

    @classmethod
    def build_combat_arena_environment(cls, env_id: str = "Env_CombatArena", seed: int = 404) -> Tuple[EnvironmentDefinition, SpatialLayoutGraph, int, int]:
        """4. A Combat Arena (Large open arena with cover elements)."""
        env_def = EnvironmentDefinition(env_id, EnvironmentType.MILITARY, seed=seed)
        graph = SpatialLayoutGraph()
        graph.add_room(EnvironmentRoom("Room_Staging", RoomPurpose.SPAWN, [600.0, 600.0, 300.0]))
        graph.add_room(EnvironmentRoom("Room_MainArena", RoomPurpose.COMBAT, [2400.0, 2400.0, 600.0]))
        graph.add_connection("Room_Staging", "Room_MainArena", "DOORWAY")
        return env_def, graph, 180, 60

    @classmethod
    def build_dungeon_environment(cls, env_id: str = "Env_Dungeon", seed: int = 505) -> Tuple[EnvironmentDefinition, SpatialLayoutGraph, int, int]:
        """5. A Dungeon (Crypt layout with puzzle and boss room)."""
        env_def = EnvironmentDefinition(env_id, EnvironmentType.DUNGEON, seed=seed)
        graph = SpatialLayoutGraph()
        graph.add_room(EnvironmentRoom("Room_Entrance", RoomPurpose.SPAWN, [600.0, 600.0, 300.0]))
        graph.add_room(EnvironmentRoom("Room_HallOfTrials", RoomPurpose.PUZZLE, [1000.0, 800.0, 400.0]))
        graph.add_room(EnvironmentRoom("Room_Catacomb", RoomPurpose.COMBAT, [800.0, 800.0, 300.0]))
        graph.add_room(EnvironmentRoom("Room_Throne", RoomPurpose.BOSS, [1600.0, 1200.0, 500.0]))
        graph.add_connection("Room_Entrance", "Room_HallOfTrials", "CORRIDOR")
        graph.add_connection("Room_HallOfTrials", "Room_Catacomb", "DOORWAY")
        graph.add_connection("Room_Catacomb", "Room_Throne", "DOORWAY")
        return env_def, graph, 210, 55

    @classmethod
    def build_scifi_complex_environment(cls, env_id: str = "Env_SciFiComplex", seed: int = 606) -> Tuple[EnvironmentDefinition, SpatialLayoutGraph, int, int]:
        """6. A Sci-Fi Complex (High-tech orbital habitat/bunker)."""
        env_def = EnvironmentDefinition(env_id, EnvironmentType.SCI_FI, seed=seed)
        graph = SpatialLayoutGraph()
        graph.add_room(EnvironmentRoom("Room_Hangars", RoomPurpose.TRANSITION, [1500.0, 1500.0, 600.0]))
        graph.add_room(EnvironmentRoom("Room_ReactorCore", RoomPurpose.OBJECTIVE, [1200.0, 1200.0, 800.0]))
        graph.add_connection("Room_Hangars", "Room_ReactorCore", "ELEVATOR")
        return env_def, graph, 195, 70

    @classmethod
    def build_modular_district_environment(cls, env_id: str = "Env_ModularDistrict", seed: int = 707) -> Tuple[EnvironmentDefinition, SpatialLayoutGraph, int, int]:
        """7. A Modular District (Interconnected urban blocks and streets)."""
        env_def = EnvironmentDefinition(env_id, EnvironmentType.URBAN, seed=seed)
        graph = SpatialLayoutGraph()
        graph.add_room(EnvironmentRoom("Block_Plaza", RoomPurpose.TRANSITION, [2000.0, 2000.0, 300.0]))
        graph.add_room(EnvironmentRoom("Block_Market", RoomPurpose.LOOT, [1200.0, 1200.0, 300.0]))
        graph.add_room(EnvironmentRoom("Block_Residential", RoomPurpose.SAFE, [1000.0, 1000.0, 300.0]))
        graph.add_connection("Block_Plaza", "Block_Market", "CORRIDOR")
        graph.add_connection("Block_Plaza", "Block_Residential", "CORRIDOR")
        return env_def, graph, 320, 110

    @classmethod
    def build_world_cell_environment(cls, env_id: str = "Env_WorldCell", seed: int = 808) -> Tuple[EnvironmentDefinition, SpatialLayoutGraph, int, int]:
        """8. A Procedural World Cell (Partitioned landscape tile with modular outpost)."""
        env_def = EnvironmentDefinition(env_id, EnvironmentType.EXTERIOR, seed=seed)
        graph = SpatialLayoutGraph()
        graph.add_room(EnvironmentRoom("Cell_ValleyOutpost", RoomPurpose.OBJECTIVE, [3000.0, 3000.0, 400.0]))
        return env_def, graph, 250, 85
