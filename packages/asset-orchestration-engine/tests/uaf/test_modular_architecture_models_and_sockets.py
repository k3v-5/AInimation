"""
Tests for Modular Architecture Models and Sockets.
UAF-81.31 Sections 4, 5, 6, 7, 13, 14, 15.
"""

from uaf.modular_architecture.models.definition import (
    ModuleType31,
    ArchitecturalKitType31,
    SocketType31,
    ArchitecturalModulePiece,
    ModularArchitectureKitDefinition,
)


def test_architectural_module_piece_dimensions_and_validity():
    piece_ok = ArchitecturalModulePiece("Wall_A", ModuleType31.WALL, [400.0, 30.0, 300.0], [SocketType31.WALL_START])
    assert piece_ok.is_valid is True

    piece_bad = ArchitecturalModulePiece("Wall_Bad", ModuleType31.WALL, [400.0, -10.0, 300.0], [SocketType31.WALL_START])
    assert piece_bad.is_valid is False


def test_modular_architecture_kit_definition_and_hashing():
    pieces = [
        ArchitecturalModulePiece("Floor_Deck", ModuleType31.FLOOR, [400.0, 400.0, 20.0], [SocketType31.FLOOR_TOP]),
        ArchitecturalModulePiece("Wall_Solid", ModuleType31.WALL, [400.0, 30.0, 300.0], [SocketType31.WALL_START]),
    ]
    kit_def = ModularArchitectureKitDefinition(
        kit_id="Kit_Spec_Corridor",
        kit_type=ArchitecturalKitType31.SCI_FI_CORRIDOR_KIT,
        grid_unit_cm=400.0,
        pieces=pieces,
        seed=34567,
    )

    assert kit_def.is_valid_grid is True
    assert len(kit_def.definition_hash) == 64
    data = kit_def.to_dict()
    assert data["kit_type"] == "SCI_FI_CORRIDOR_KIT"
    assert len(data["pieces"]) == 2

    bad_kit = ModularArchitectureKitDefinition(
        kit_id="Kit_Bad_Grid",
        kit_type=ArchitecturalKitType31.SCI_FI_CORRIDOR_KIT,
        grid_unit_cm=50.0,
    )
    assert bad_kit.is_valid_grid is False
