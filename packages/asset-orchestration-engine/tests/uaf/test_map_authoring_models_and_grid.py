"""
Tests for Map Authoring Models, Dimensions, and Grid.
UAF-81.44 Sections 4, 9, 10, 13, 15, 134, 135.
"""

from uaf.map_authoring.models.definition import (
    GridMode44,
    ModularCategory44,
    ConnectorType44,
    WorldTheme44,
    MapDimensions44,
    MapAuthoringSpecification,
)


def test_map_dimensions_and_validity():
    dims_ok = MapDimensions44(width_m=2000.0, length_m=2000.0, height_m=150.0)
    assert dims_ok.is_valid is True

    dims_neg = MapDimensions44(width_m=-100.0, length_m=1000.0, height_m=50.0)
    assert dims_neg.is_valid is False

    dims_low_height = MapDimensions44(width_m=1000.0, length_m=1000.0, height_m=5.0)  # < 10.0m
    assert dims_low_height.is_valid is False


def test_map_authoring_specification_and_hashing():
    spec = MapAuthoringSpecification(
        map_id="Map_Test_Base",
        theme=WorldTheme44.BUNKER,
        grid_mode=GridMode44.MODULAR,
        dimensions=MapDimensions44(width_m=1500.0, length_m=1500.0, height_m=80.0),
        cell_size_cm=100.0,
        modular_piece_count=20,
        has_collision=True,
        has_navigation=True,
        has_lighting=True,
        has_streaming_partition=True,
        seed=123789,
    )

    assert spec.is_valid_map is True
    assert len(spec.definition_hash) == 64
    data = spec.to_dict()
    assert data["theme"] == "BUNKER"
    assert data["modular_piece_count"] == 20

    bad_spec_pieces = MapAuthoringSpecification(
        map_id="Map_NoPieces",
        theme=WorldTheme44.BUNKER,
        modular_piece_count=0,  # < 1 piece
    )
    assert bad_spec_pieces.is_valid_map is False
