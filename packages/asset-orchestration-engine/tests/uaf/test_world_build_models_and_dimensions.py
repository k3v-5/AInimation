"""
Tests for World Build Models, Dimensions, and Scales.
UAF-81.40 Sections 4, 5, 6, 16, 33, 153.
"""

from uaf.world_build.models.definition import (
    WorldScaleProfile40,
    RegionType40,
    TerrainSlopeClass40,
    WorldDimensions40,
    WorldBuildSpecification,
)


def test_world_dimensions_and_validity():
    dims_ok = WorldDimensions40(width_m=2000.0, length_m=2000.0, height_m=300.0)
    assert dims_ok.is_valid is True

    dims_neg = WorldDimensions40(width_m=-100.0, length_m=1000.0, height_m=100.0)
    assert dims_neg.is_valid is False

    dims_low_height = WorldDimensions40(width_m=1000.0, length_m=1000.0, height_m=5.0)  # < 10.0m
    assert dims_low_height.is_valid is False


def test_world_build_specification_and_hashing():
    spec = WorldBuildSpecification(
        world_id="World_Test_Forest",
        scale_profile=WorldScaleProfile40.MEDIUM,
        primary_region=RegionType40.FOREST,
        dimensions=WorldDimensions40(width_m=2000.0, length_m=2000.0, height_m=250.0),
        cell_count=4,
        has_world_partition=True,
        has_hydrology=True,
        road_count=2,
        seed=778899,
    )

    assert spec.is_valid_scale is True
    assert len(spec.definition_hash) == 64
    data = spec.to_dict()
    assert data["scale_profile"] == "MEDIUM"
    assert data["cell_count"] == 4

    # Large world without partition should be invalid
    bad_large_spec = WorldBuildSpecification(
        world_id="World_BadPartition",
        scale_profile=WorldScaleProfile40.LARGE,
        primary_region=RegionType40.DESERT,
        dimensions=WorldDimensions40(width_m=4000.0, length_m=4000.0, height_m=300.0),
        has_world_partition=False,  # >= 2000m requires world partition
    )
    assert bad_large_spec.is_valid_scale is False
