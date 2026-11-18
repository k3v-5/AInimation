"""
Tests for Failure Modes & Hard Fail Conditions (UAF-81.56 Section 207).
"""

import pytest
from uaf.universal_world import (
    WorldDefinition,
    WorldBounds,
    WorldCell,
    SceneNode,
    WorldSceneGraph,
    BuildingDefinition,
    RiverDefinition,
    UniversalWorldFabricator,
    UniversalWorldValidator,
)


@pytest.fixture
def valid_world():
    return UniversalWorldFabricator.create_base_world("W_FAIL_TEST", "Fail Test World")


def test_invalid_world(valid_world):
    # Inverted world bounds
    valid_world.bounds = WorldBounds(100.0, -100.0, 100.0, -100.0, 10.0, -10.0)
    report = UniversalWorldValidator.validate_world(valid_world)
    assert report.is_valid is False
    assert any("bounds" in f.lower() for f in report.failed_checks)


def test_invalid_region(valid_world):
    valid_world.regions = []
    sg = UniversalWorldFabricator.build_scene_graph(valid_world)
    assert sg is not None


def test_invalid_cell(valid_world):
    valid_world.cells = []
    report = UniversalWorldValidator.validate_world(valid_world)
    assert report.is_valid is False
    assert any("0 cells" in f.lower() for f in report.failed_checks)


def test_invalid_biome(valid_world):
    valid_world.biomes = []
    report = UniversalWorldValidator.validate_world(valid_world)
    assert any("no biomes" in w.lower() for w in report.warnings)


def test_invalid_terrain(valid_world):
    valid_world.terrain.samples = []
    report = UniversalWorldValidator.validate_world(valid_world)
    assert any("empty samples" in w.lower() for w in report.warnings)


def test_invalid_noise():
    # Frequency zero edge case
    from uaf.universal_world import NoiseDefinition
    noise = NoiseDefinition(frequency=0.0)
    assert noise.sample_2d(10.0, 10.0) == 0.0


def test_invalid_water(valid_world):
    # Nullify water body material reference to invalid windows path
    valid_world.water.water_bodies[0].material_reference = r"C:\Engine\M_Water.uasset"
    report = UniversalWorldValidator.validate_world(valid_world)
    assert report.is_valid is False
    assert any("machine-dependent" in f.lower() for f in report.failed_checks)


def test_invalid_river(valid_world):
    # Negative width
    valid_world.water.rivers[0].width = -100.0
    report = UniversalWorldValidator.validate_world(valid_world)
    assert report.is_valid is False
    assert any("non-positive width" in f.lower() for f in report.failed_checks)


def test_invalid_scatter(valid_world):
    # Scatter outside bounds
    b = WorldBounds(0.0, 10.0, 0.0, 10.0, 0.0, 10.0)
    assert b.contains_point(100.0, 100.0, 0.0) is False


def test_invalid_asset(valid_world):
    # Asset with local D:\ drive path
    valid_world.props[0].asset_variants = [r"D:\Assets\Crate.uasset"]
    report = UniversalWorldValidator.validate_world(valid_world)
    assert report.is_valid is False
    assert any("machine-dependent" in f.lower() for f in report.failed_checks)


def test_invalid_building(valid_world):
    # Non-positive height
    valid_world.structures[0].height = -50.0
    report = UniversalWorldValidator.validate_world(valid_world)
    assert report.is_valid is False
    assert any("height" in f.lower() for f in report.failed_checks)


def test_invalid_road(valid_world):
    valid_world.roads[0].surface_profile = r"E:\Game\Road.uasset"
    report = UniversalWorldValidator.validate_world(valid_world)
    assert report.is_valid is False
    assert any("machine-dependent" in f.lower() for f in report.failed_checks)


def test_invalid_navigation(valid_world):
    valid_world.navigation.connectivity = False
    report = UniversalWorldValidator.validate_world(valid_world)
    assert any("disconnected" in w.lower() for w in report.warnings)


def test_invalid_collision(valid_world):
    valid_world.collision.layers = []
    assert len(valid_world.collision.layers) == 0


def test_invalid_streaming(valid_world):
    valid_world.partition.cells = []
    assert len(valid_world.partition.cells) == 0


def test_invalid_hlod(valid_world):
    valid_world.hlod.levels = []
    assert len(valid_world.hlod.levels) == 0


def test_invalid_environment(valid_world):
    valid_world.environment.ambient_soundtrack = r"C:\Audio\Track.uasset"
    report = UniversalWorldValidator.validate_world(valid_world)
    assert report.is_valid is False
    assert any("machine-dependent" in f.lower() for f in report.failed_checks)


def test_invalid_spawn(valid_world):
    valid_world.spawn.height_range = (1000.0, 500.0)  # Inverted range
    assert valid_world.spawn.height_range[0] > valid_world.spawn.height_range[1]


def test_invalid_landmark(valid_world):
    # Scene graph cycle
    sg = WorldSceneGraph(root_id="N1")
    n1 = SceneNode("N1", parent_id="N2")
    n2 = SceneNode("N2", parent_id="N1")
    sg.add_node(n1)
    sg.add_node(n2)
    report = UniversalWorldValidator.validate_world(valid_world, scene_graph=sg)
    assert report.is_valid is False
    assert any("cyclic" in f.lower() for f in report.failed_checks)
