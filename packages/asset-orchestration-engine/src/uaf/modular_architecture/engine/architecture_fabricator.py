"""
ModularArchitectureFabricationPlatform manufactures canonical modular kits matching Section 144.
UAF-81.31 Sections 129, 144.
"""

from typing import Tuple, List, Dict, Any
from ..models.definition import (
    ModularArchitectureKitDefinition,
    ArchitecturalKitType31,
    ModuleType31,
    SocketType31,
    ArchitecturalModulePiece,
)


class ModularArchitectureFabricationPlatform:
    """
    Synthesizes complete, production-grade modular architectural kits with validated sockets and grid alignment.
    """

    @classmethod
    def build_scifi_corridor_kit(cls, kit_id: str = "Kit_SciFiCorridor") -> Tuple[ModularArchitectureKitDefinition, List[str], str]:
        """1. SCI_FI_CORRIDOR_KIT (Section 144: Sci-fi corridor walls, airlock doors, floors, ceiling panels)."""
        pieces = [
            ArchitecturalModulePiece(f"{kit_id}_Wall_Panel", ModuleType31.WALL, [400.0, 30.0, 300.0], [SocketType31.WALL_START, SocketType31.WALL_END]),
            ArchitecturalModulePiece(f"{kit_id}_Floor_Deck", ModuleType31.FLOOR, [400.0, 400.0, 20.0], [SocketType31.FLOOR_TOP, SocketType31.FLOOR_BOTTOM]),
            ArchitecturalModulePiece(f"{kit_id}_Airlock_Door", ModuleType31.DOOR, [400.0, 40.0, 300.0], [SocketType31.DOOR]),
            ArchitecturalModulePiece(f"{kit_id}_Ceiling_Grid", ModuleType31.CEILING, [400.0, 400.0, 25.0], [SocketType31.CEILING]),
        ]
        kit_def = ModularArchitectureKitDefinition(kit_id, ArchitecturalKitType31.SCI_FI_CORRIDOR_KIT, grid_unit_cm=400.0, pieces=pieces)
        mesh_refs = [f"SM_{p.piece_id}" for p in pieces]
        return kit_def, mesh_refs, "M_Master_SciFiModularPBR"

    @classmethod
    def build_industrial_room_kit(cls, kit_id: str = "Kit_IndustrialWarehouse") -> Tuple[ModularArchitectureKitDefinition, List[str], str]:
        """2. INDUSTRIAL_ROOM_KIT (Section 144: Concrete walls, steel beams, platforms, pipe modules)."""
        pieces = [
            ArchitecturalModulePiece(f"{kit_id}_Ind_Wall", ModuleType31.WALL, [400.0, 40.0, 400.0], [SocketType31.WALL_START, SocketType31.WALL_END]),
            ArchitecturalModulePiece(f"{kit_id}_Steel_Beam", ModuleType31.BEAM, [400.0, 50.0, 50.0], [SocketType31.STRUCTURAL]),
            ArchitecturalModulePiece(f"{kit_id}_Catwalk_Plat", ModuleType31.PLATFORM, [400.0, 200.0, 30.0], [SocketType31.FLOOR_TOP]),
            ArchitecturalModulePiece(f"{kit_id}_Conduit_Pipe", ModuleType31.PIPE, [400.0, 30.0, 30.0], [SocketType31.PIPE]),
        ]
        kit_def = ModularArchitectureKitDefinition(kit_id, ArchitecturalKitType31.INDUSTRIAL_ROOM_KIT, grid_unit_cm=400.0, pieces=pieces)
        mesh_refs = [f"SM_{p.piece_id}" for p in pieces]
        return kit_def, mesh_refs, "M_Master_IndustrialModularPBR"

    @classmethod
    def build_urban_building_kit(cls, kit_id: str = "Kit_UrbanArchitecture") -> Tuple[ModularArchitectureKitDefinition, List[str], str]:
        """3. URBAN_BUILDING_KIT (Section 144: Brick walls, street doors, glass windows, facade corners)."""
        pieces = [
            ArchitecturalModulePiece(f"{kit_id}_Brick_Wall", ModuleType31.WALL, [400.0, 35.0, 350.0], [SocketType31.WALL_START, SocketType31.WALL_END]),
            ArchitecturalModulePiece(f"{kit_id}_Store_Door", ModuleType31.DOOR, [400.0, 35.0, 350.0], [SocketType31.DOOR]),
            ArchitecturalModulePiece(f"{kit_id}_Bay_Window", ModuleType31.WINDOW, [400.0, 35.0, 350.0], [SocketType31.WINDOW]),
            ArchitecturalModulePiece(f"{kit_id}_Outer_Corner", ModuleType31.CORNER, [100.0, 100.0, 350.0], [SocketType31.CORNER]),
        ]
        kit_def = ModularArchitectureKitDefinition(kit_id, ArchitecturalKitType31.URBAN_BUILDING_KIT, grid_unit_cm=400.0, pieces=pieces)
        mesh_refs = [f"SM_{p.piece_id}" for p in pieces]
        return kit_def, mesh_refs, "M_Master_UrbanModularPBR"

    @classmethod
    def build_bunker_kit(cls, kit_id: str = "Kit_MilitaryBunker") -> Tuple[ModularArchitectureKitDefinition, List[str], str]:
        """4. BUNKER_KIT (Section 144: Heavy reinforced concrete walls, blast doors, support pillars)."""
        pieces = [
            ArchitecturalModulePiece(f"{kit_id}_Blast_Wall", ModuleType31.WALL, [400.0, 60.0, 300.0], [SocketType31.WALL_START, SocketType31.WALL_END]),
            ArchitecturalModulePiece(f"{kit_id}_Blast_Door", ModuleType31.DOOR, [400.0, 60.0, 300.0], [SocketType31.DOOR]),
            ArchitecturalModulePiece(f"{kit_id}_Heavy_Pillar", ModuleType31.PILLAR, [80.0, 80.0, 300.0], [SocketType31.STRUCTURAL]),
            ArchitecturalModulePiece(f"{kit_id}_Bunker_Stair", ModuleType31.STAIR, [400.0, 400.0, 300.0], [SocketType31.STAIR]),
        ]
        kit_def = ModularArchitectureKitDefinition(kit_id, ArchitecturalKitType31.BUNKER_KIT, grid_unit_cm=400.0, pieces=pieces)
        mesh_refs = [f"SM_{p.piece_id}" for p in pieces]
        return kit_def, mesh_refs, "M_Master_BunkerReinforcedPBR"
