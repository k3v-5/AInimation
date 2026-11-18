"""
WorldBuildingFabricationPlatform manufactures playable modular worlds matching Sections 60 to 77.
UAF-81.28 Sections 60, 68, 69, 70, 72, 73, 113, 133.
"""

from typing import Tuple, List, Dict, Any
from ..models.definition import (
    PlayableWorldDefinition,
    WorldType28,
    ModularCategory,
    SocketType28,
    ModularBlockDefinition,
)
from ..models.graph import (
    BlockoutWorldGraph,
    BlockoutZoneNode,
)


class WorldBuildingFabricationPlatform:
    """
    Synthesizes complete blockouts, modular kits, spatial graphs, and production world assets.
    """

    @classmethod
    def _create_standard_kit(cls, prefix: str) -> List[ModularBlockDefinition]:
        return [
            ModularBlockDefinition(f"{prefix}_Wall_4x3", ModularCategory.WALL, [400.0, 20.0, 300.0], [SocketType28.WALL_CONNECTOR]),
            ModularBlockDefinition(f"{prefix}_Floor_4x4", ModularCategory.FLOOR, [400.0, 400.0, 20.0], [SocketType28.FLOOR_CONNECTOR]),
            ModularBlockDefinition(f"{prefix}_Ceiling_4x4", ModularCategory.CEILING, [400.0, 400.0, 20.0], [SocketType28.CEILING_CONNECTOR]),
            ModularBlockDefinition(f"{prefix}_Door_4x3", ModularCategory.DOOR, [400.0, 20.0, 300.0], [SocketType28.DOOR_CONNECTOR]),
            ModularBlockDefinition(f"{prefix}_Stair_4x3", ModularCategory.STAIR, [400.0, 400.0, 300.0], [SocketType28.STAIR_CONNECTOR]),
        ]

    @classmethod
    def build_interior_facility_world(cls, world_id: str = "World_SciFiFacility") -> Tuple[PlayableWorldDefinition, BlockoutWorldGraph, str]:
        """1. INTERIOR FACILITY (Section 68: Sci-fi corridors, lab rooms, airlocks)."""
        kit = cls._create_standard_kit("SciFi")
        w_def = PlayableWorldDefinition(world_id, WorldType28.FACILITY, grid_size_cm=400.0, module_blocks=kit)

        graph = BlockoutWorldGraph()
        graph.add_zone(BlockoutZoneNode("Zone_Airlock", "Airlock Entry", [800.0, 800.0, 300.0], is_critical_path=True))
        graph.add_zone(BlockoutZoneNode("Zone_MainHall", "Main Central Hall", [2000.0, 2000.0, 600.0], is_critical_path=True))
        graph.add_zone(BlockoutZoneNode("Zone_BioLab", "Biotech Laboratory", [1200.0, 1200.0, 300.0], is_critical_path=False))
        graph.add_connection("Zone_Airlock", "Zone_MainHall", "SECURITY_DOOR")
        graph.add_connection("Zone_MainHall", "Zone_BioLab", "SLIDING_DOOR")
        return w_def, graph, f"LV_{world_id}"

    @classmethod
    def build_urban_block_world(cls, world_id: str = "World_UrbanCityBlock") -> Tuple[PlayableWorldDefinition, BlockoutWorldGraph, str]:
        """2. URBAN BLOCK (Section 70: city streets, building fronts, intersections)."""
        kit = cls._create_standard_kit("Urban")
        w_def = PlayableWorldDefinition(world_id, WorldType28.URBAN, grid_size_cm=400.0, module_blocks=kit)

        graph = BlockoutWorldGraph()
        graph.add_zone(BlockoutZoneNode("Zone_Boulevard", "North Boulevard", [4000.0, 1200.0, 2000.0], is_critical_path=True))
        graph.add_zone(BlockoutZoneNode("Zone_Plaza", "Metro Station Plaza", [2400.0, 2400.0, 1500.0], is_critical_path=True))
        graph.add_connection("Zone_Boulevard", "Zone_Plaza", "CROSSWALK")
        return w_def, graph, f"LV_{world_id}"

    @classmethod
    def build_industrial_complex_world(cls, world_id: str = "World_IndustrialDepot") -> Tuple[PlayableWorldDefinition, BlockoutWorldGraph, str]:
        """3. INDUSTRIAL COMPLEX (Section 69: warehouses, catwalks, refineries)."""
        kit = cls._create_standard_kit("Ind")
        w_def = PlayableWorldDefinition(world_id, WorldType28.INDUSTRIAL, grid_size_cm=400.0, module_blocks=kit)

        graph = BlockoutWorldGraph()
        graph.add_zone(BlockoutZoneNode("Zone_CargoYard", "Cargo Loading Yard", [3200.0, 3200.0, 800.0], is_critical_path=True))
        graph.add_zone(BlockoutZoneNode("Zone_TurbineHall", "Main Turbine Generator", [2400.0, 1600.0, 1000.0], is_critical_path=True))
        graph.add_connection("Zone_CargoYard", "Zone_TurbineHall", "CATWALK")
        return w_def, graph, f"LV_{world_id}"

    @classmethod
    def build_combat_arena_world(cls, world_id: str = "World_GladiatorArena") -> Tuple[PlayableWorldDefinition, BlockoutWorldGraph, str]:
        """4. COMBAT ARENA (Section 72: player access, cover, lines of sight, spawn zones)."""
        kit = cls._create_standard_kit("Arena")
        w_def = PlayableWorldDefinition(world_id, WorldType28.ARENA, grid_size_cm=400.0, module_blocks=kit)

        graph = BlockoutWorldGraph()
        graph.add_zone(BlockoutZoneNode("Zone_Spawn_Alpha", "Team Alpha Spawn", [1200.0, 800.0, 300.0], is_critical_path=True))
        graph.add_zone(BlockoutZoneNode("Zone_CentralPit", "Central Arena Pit", [3600.0, 3600.0, 800.0], is_critical_path=True))
        graph.add_zone(BlockoutZoneNode("Zone_Spawn_Bravo", "Team Bravo Spawn", [1200.0, 800.0, 300.0], is_critical_path=True))
        graph.add_connection("Zone_Spawn_Alpha", "Zone_CentralPit", "TUNNEL")
        graph.add_connection("Zone_Spawn_Bravo", "Zone_CentralPit", "TUNNEL")
        return w_def, graph, f"LV_{world_id}"

    @classmethod
    def build_dungeon_complex_world(cls, world_id: str = "World_CryptDungeon") -> Tuple[PlayableWorldDefinition, BlockoutWorldGraph, str]:
        """5. DUNGEON COMPLEX (Section 73: catacombs, crypt chambers, stone corridors)."""
        kit = cls._create_standard_kit("Crypt")
        w_def = PlayableWorldDefinition(world_id, WorldType28.DUNGEON, grid_size_cm=400.0, module_blocks=kit)

        graph = BlockoutWorldGraph()
        graph.add_zone(BlockoutZoneNode("Zone_CryptEntrance", "Crypt Entrance Staircase", [1200.0, 800.0, 400.0], is_critical_path=True))
        graph.add_zone(BlockoutZoneNode("Zone_TombChamber", "Ancient Tomb Chamber", [2000.0, 2000.0, 600.0], is_critical_path=True))
        graph.add_zone(BlockoutZoneNode("Zone_TreasureVault", "Sealed Treasure Vault", [800.0, 800.0, 400.0], is_critical_path=False))
        graph.add_connection("Zone_CryptEntrance", "Zone_TombChamber", "STONE_CORRIDOR")
        graph.add_connection("Zone_TombChamber", "Zone_TreasureVault", "IRON_GATE")
        return w_def, graph, f"LV_{world_id}"
