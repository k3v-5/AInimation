"""
Tests for Environment Grid, Snap System, Modular Pieces, and Grammar.
UAF-81.12 Sections 6, 7, 8, 9, 11, 12, 16.
"""

from uaf.environment.spatial.grid import GridProfile, SnapCategory, SnapPoint
from uaf.environment.spatial.piece import ModularPiece
from uaf.environment.grammar.grammar import ModularGrammar, ModularGrammarRule


def test_grid_profile_and_snap_coordinate():
    grid = GridProfile(unit_size_cm=100.0, rotation_increment_deg=90.0)
    assert grid.snap_coordinate(1.89) == 2.0
    assert grid.snap_coordinate(0.24) == 0.0
    data = grid.to_dict()
    assert data["unit_size_cm"] == 100.0


def test_snap_point_compatibility():
    snap_wall_a = SnapPoint("S_Wall_01", [0.0, 0.0, 0.0], category=SnapCategory.WALL, compatibility_tags=["scifi_interior"])
    snap_wall_b = SnapPoint("S_Wall_02", [2.0, 0.0, 0.0], category=SnapCategory.WALL, compatibility_tags=["scifi_interior"])
    snap_floor = SnapPoint("S_Floor_01", [0.0, 0.0, 0.0], category=SnapCategory.FLOOR)

    assert snap_wall_a.is_compatible_with(snap_wall_b) is True
    assert snap_wall_a.is_compatible_with(snap_floor) is False


def test_modular_piece_presets_and_hashing():
    wall = ModularPiece.create_standard_wall("SM_Wall_01")
    floor = ModularPiece.create_standard_floor("SM_Floor_01")

    assert wall.module_type == "WALL"
    assert len(wall.snap_points) == 2
    assert len(wall.piece_hash) == 64

    assert floor.module_type == "FLOOR"
    assert len(floor.snap_points) == 4
    assert len(floor.piece_hash) == 64


def test_modular_grammar_rules():
    grammar = ModularGrammar.create_standard_corridor_grammar("Grammar_Scifi")
    assert len(grammar.rules) == 3
    # Top priority rule is floor
    assert grammar.rules[0].rule_id == "R_Floor"
    assert grammar.rules[0].priority == 100
