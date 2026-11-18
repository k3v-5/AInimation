"""
WorldArchitectureFabricationPlatform manufactures all 9 canonical reference worlds from Section 149.
UAF-81.24 Sections 149, 150, 151, 152, 153, 154.
"""

from typing import Tuple, List, Dict, Any
from ..models.definition import WorldDefinition24, WorldBoundaryBounds, WorldGridCell, BiomeType24
from ..models.graph import ArchitecturalWorldGraph, ArchitecturalRoomNode, ArchitecturalZoneType


class WorldArchitectureFabricationPlatform:
    """
    Synthesizes complete, production-ready world architectures matching Section 149.
    """

    @classmethod
    def _create_grid_cells(cls, count_x: int, count_y: int, cell_size: float = 10000.0) -> List[WorldGridCell]:
        cells = []
        for gx in range(count_x):
            for gy in range(count_y):
                cells.append(WorldGridCell(
                    f"Cell_{gx}_{gy}",
                    gx, gy,
                    [gx * cell_size, gy * cell_size, 0.0]
                ))
        return cells

    @classmethod
    def build_small_interior_world(cls, world_id: str = "World_SmallInterior") -> Tuple[WorldDefinition24, ArchitecturalWorldGraph, List[WorldGridCell], List[str]]:
        """1. SMALL_INTERIOR (Section 150: rooms, doors, walls, ceiling)."""
        w_def = WorldDefinition24(world_id, WorldBoundaryBounds(-5000, 5000, -5000, 5000, 0, 800), BiomeType24.URBAN)
        graph = ArchitecturalWorldGraph()
        graph.add_room(ArchitecturalRoomNode("Room_Entry", ArchitecturalZoneType.CRITICAL_PATH, [800.0, 800.0, 350.0]))
        graph.add_room(ArchitecturalRoomNode("Room_Living", ArchitecturalZoneType.CRITICAL_PATH, [1200.0, 1000.0, 350.0]))
        graph.add_room(ArchitecturalRoomNode("Room_Office", ArchitecturalZoneType.OPTIONAL_ZONE, [600.0, 600.0, 350.0]))
        graph.add_connection("Room_Entry", "Room_Living", "DOORWAY")
        graph.add_connection("Room_Living", "Room_Office", "DOORWAY")
        return w_def, graph, cls._create_grid_cells(1, 1), ["LM_Interior_Foyer"]

    @classmethod
    def build_modular_building_world(cls, world_id: str = "World_ModularBuilding") -> Tuple[WorldDefinition24, ArchitecturalWorldGraph, List[WorldGridCell], List[str]]:
        """2. MODULAR_BUILDING (Section 151: module connectivity, grid alignment)."""
        w_def = WorldDefinition24(world_id, WorldBoundaryBounds(-10000, 10000, -10000, 10000, 0, 3000), BiomeType24.URBAN)
        graph = ArchitecturalWorldGraph()
        graph.add_room(ArchitecturalRoomNode("Floor0_Lobby", ArchitecturalZoneType.CRITICAL_PATH, [1600.0, 1600.0, 400.0], 0))
        graph.add_room(ArchitecturalRoomNode("Floor0_Corridor", ArchitecturalZoneType.CORRIDOR, [400.0, 2000.0, 400.0], 0))
        graph.add_room(ArchitecturalRoomNode("Floor1_Offices", ArchitecturalZoneType.CRITICAL_PATH, [1600.0, 1600.0, 400.0], 1))
        graph.add_connection("Floor0_Lobby", "Floor0_Corridor", "CORRIDOR")
        graph.add_connection("Floor0_Corridor", "Floor1_Offices", "STAIR")
        return w_def, graph, cls._create_grid_cells(2, 2), ["LM_Skyscraper_Atrium"]

    @classmethod
    def build_industrial_complex_world(cls, world_id: str = "World_IndustrialComplex") -> Tuple[WorldDefinition24, ArchitecturalWorldGraph, List[WorldGridCell], List[str]]:
        """3. INDUSTRIAL_COMPLEX (Refinery, pipes, warehouses)."""
        w_def = WorldDefinition24(world_id, WorldBoundaryBounds(-25000, 25000, -25000, 25000, 0, 5000), BiomeType24.INDUSTRIAL)
        graph = ArchitecturalWorldGraph()
        graph.add_room(ArchitecturalRoomNode("Ind_Depot", ArchitecturalZoneType.CRITICAL_PATH, [2400.0, 2400.0, 600.0]))
        graph.add_room(ArchitecturalRoomNode("Ind_Reactor", ArchitecturalZoneType.CRITICAL_PATH, [3000.0, 3000.0, 1200.0]))
        graph.add_connection("Ind_Depot", "Ind_Reactor", "CORRIDOR")
        return w_def, graph, cls._create_grid_cells(3, 3), ["LM_Cooling_Tower", "LM_Storage_Silo"]

    @classmethod
    def build_outdoor_area_world(cls, world_id: str = "World_OutdoorArea") -> Tuple[WorldDefinition24, ArchitecturalWorldGraph, List[WorldGridCell], List[str]]:
        """4. OUTDOOR_AREA (Section 152: terrain, vegetation, rocks, paths)."""
        w_def = WorldDefinition24(world_id, WorldBoundaryBounds(-50000, 50000, -50000, 50000, -2000, 10000), BiomeType24.FOREST)
        graph = ArchitecturalWorldGraph()
        graph.add_room(ArchitecturalRoomNode("Out_CanyonPath", ArchitecturalZoneType.CRITICAL_PATH, [5000.0, 1500.0, 1000.0]))
        graph.add_room(ArchitecturalRoomNode("Out_Clearing", ArchitecturalZoneType.CRITICAL_PATH, [4000.0, 4000.0, 2000.0]))
        graph.add_connection("Out_CanyonPath", "Out_Clearing", "ROAD")
        return w_def, graph, cls._create_grid_cells(4, 4), ["LM_Ancient_Monolith", "LM_Waterfall"]

    @classmethod
    def build_forest_world(cls, world_id: str = "World_DeepForest") -> Tuple[WorldDefinition24, ArchitecturalWorldGraph, List[WorldGridCell], List[str]]:
        """5. FOREST (Dense canopy, groves, ranger post)."""
        w_def = WorldDefinition24(world_id, WorldBoundaryBounds(-40000, 40000, -40000, 40000, 0, 8000), BiomeType24.FOREST)
        graph = ArchitecturalWorldGraph()
        graph.add_room(ArchitecturalRoomNode("Forest_Grove", ArchitecturalZoneType.CRITICAL_PATH, [3500.0, 3500.0, 1500.0]))
        graph.add_room(ArchitecturalRoomNode("Forest_Cabin", ArchitecturalZoneType.INTERIOR, [1000.0, 800.0, 350.0]))
        graph.add_connection("Forest_Grove", "Forest_Cabin", "TRAIL")
        return w_def, graph, cls._create_grid_cells(4, 4), ["LM_Elder_Oak"]

    @classmethod
    def build_desert_world(cls, world_id: str = "World_DuneDesert") -> Tuple[WorldDefinition24, ArchitecturalWorldGraph, List[WorldGridCell], List[str]]:
        """6. DESERT (Dunes, oasis, ancient ruin)."""
        w_def = WorldDefinition24(world_id, WorldBoundaryBounds(-60000, 60000, -60000, 60000, 0, 6000), BiomeType24.DESERT)
        graph = ArchitecturalWorldGraph()
        graph.add_room(ArchitecturalRoomNode("Desert_Oasis", ArchitecturalZoneType.CRITICAL_PATH, [4000.0, 4000.0, 1000.0]))
        graph.add_room(ArchitecturalRoomNode("Desert_Temple", ArchitecturalZoneType.CRITICAL_PATH, [2500.0, 2500.0, 1200.0]))
        graph.add_connection("Desert_Oasis", "Desert_Temple", "DUNEPATH")
        return w_def, graph, cls._create_grid_cells(5, 5), ["LM_Pyramid_Ruin"]

    @classmethod
    def build_urban_block_world(cls, world_id: str = "World_CityBlock") -> Tuple[WorldDefinition24, ArchitecturalWorldGraph, List[WorldGridCell], List[str]]:
        """7. URBAN_BLOCK (Streets, intersections, plazas)."""
        w_def = WorldDefinition24(world_id, WorldBoundaryBounds(-30000, 30000, -30000, 30000, 0, 8000), BiomeType24.URBAN)
        graph = ArchitecturalWorldGraph()
        graph.add_room(ArchitecturalRoomNode("City_MainAvenue", ArchitecturalZoneType.CRITICAL_PATH, [6000.0, 1200.0, 500.0]))
        graph.add_room(ArchitecturalRoomNode("City_CentralPlaza", ArchitecturalZoneType.PLAZA, [3000.0, 3000.0, 500.0]))
        graph.add_connection("City_MainAvenue", "City_CentralPlaza", "ROAD")
        return w_def, graph, cls._create_grid_cells(3, 3), ["LM_Civic_Clocktower"]

    @classmethod
    def build_multi_level_world(cls, world_id: str = "World_MultiLevelFacility") -> Tuple[WorldDefinition24, ArchitecturalWorldGraph, List[WorldGridCell], List[str]]:
        """8. MULTI_LEVEL (Section 154: stairs, ramps, vertical connectivity)."""
        w_def = WorldDefinition24(world_id, WorldBoundaryBounds(-15000, 15000, -15000, 15000, -3000, 9000), BiomeType24.SCI_FI)
        graph = ArchitecturalWorldGraph()
        graph.add_room(ArchitecturalRoomNode("Level_Subterranean", ArchitecturalZoneType.CRITICAL_PATH, [1800.0, 1800.0, 400.0], -1))
        graph.add_room(ArchitecturalRoomNode("Level_Ground", ArchitecturalZoneType.CRITICAL_PATH, [2000.0, 2000.0, 400.0], 0))
        graph.add_room(ArchitecturalRoomNode("Level_Mezzanine", ArchitecturalZoneType.VERTICAL_TRANSITION, [1500.0, 1500.0, 400.0], 1))
        graph.add_room(ArchitecturalRoomNode("Level_Helipad", ArchitecturalZoneType.CRITICAL_PATH, [2500.0, 2500.0, 400.0], 2))
        graph.add_connection("Level_Subterranean", "Level_Ground", "ELEVATOR")
        graph.add_connection("Level_Ground", "Level_Mezzanine", "STAIR")
        graph.add_connection("Level_Mezzanine", "Level_Helipad", "RAMP")
        return w_def, graph, cls._create_grid_cells(2, 2), ["LM_Helipad_Tower"]

    @classmethod
    def build_combat_arena_world(cls, world_id: str = "World_CombatColosseum") -> Tuple[WorldDefinition24, ArchitecturalWorldGraph, List[WorldGridCell], List[str]]:
        """9. COMBAT_ARENA (Section 153: player access, cover, combat space)."""
        w_def = WorldDefinition24(world_id, WorldBoundaryBounds(-20000, 20000, -20000, 20000, 0, 4000), BiomeType24.URBAN)
        graph = ArchitecturalWorldGraph()
        graph.add_room(ArchitecturalRoomNode("Arena_Foyer", ArchitecturalZoneType.CRITICAL_PATH, [1200.0, 1200.0, 400.0]))
        graph.add_room(ArchitecturalRoomNode("Arena_MainPit", ArchitecturalZoneType.ARENA, [4000.0, 4000.0, 1000.0]))
        graph.add_connection("Arena_Foyer", "Arena_MainPit", "GATE")
        return w_def, graph, cls._create_grid_cells(2, 2), ["LM_Colosseum_Arch"]
