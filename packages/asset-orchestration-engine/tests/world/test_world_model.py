"""
Tests for World Model & Scene Graph (UAF-81.56 Section 185).
"""

import pytest
from uaf.universal_world import (
    WorldDefinition,
    WorldRegion,
    WorldCell,
    WorldBounds,
    WorldCoordinateSystem,
    WorldTransform,
    SceneNode,
    SceneNodeType,
    WorldSceneGraph,
    UniversalWorldFabricator,
)


def test_world_definition():
    b = WorldBounds(-1000.0, 1000.0, -1000.0, 1000.0, -500.0, 500.0)
    cs = WorldCoordinateSystem()
    w = WorldDefinition("W_TEST", "Test World", seed=42, bounds=b, coordinate_system=cs)
    assert w.world_id == "W_TEST"
    assert w.name == "Test World"
    assert w.seed == 42
    assert w.bounds.size_x == 2000.0
    assert cs.up_axis == "Z"


def test_world_region():
    reg = WorldRegion("REG_01", "Continent Alpha", biomes=["FOREST", "PLAINS"])
    assert reg.region_id == "REG_01"
    assert len(reg.biomes) == 2
    assert "FOREST" in reg.biomes


def test_world_cell():
    cell = WorldCell("CELL_1_2", 1, 2, origin=(1000.0, 2000.0, 0.0), size=1000.0)
    assert cell.cell_x == 1
    assert cell.cell_y == 2
    assert cell.size == 1000.0
    d = cell.to_dict()
    assert d["cell_id"] == "CELL_1_2"


def test_world_hash():
    w1 = UniversalWorldFabricator.create_base_world("W1", "World A", seed=100)
    w2 = UniversalWorldFabricator.create_base_world("W1", "World A", seed=100)
    w3 = UniversalWorldFabricator.create_base_world("W1", "World A", seed=200)
    assert len(w1.world_hash) == 64
    assert w1.world_hash == w2.world_hash
    assert w1.world_hash != w3.world_hash


def test_world_snapshot():
    w = UniversalWorldFabricator.create_base_world("W_SNAP", "Snapshot World", seed=50)
    sg = UniversalWorldFabricator.build_scene_graph(w)
    snap = UniversalWorldFabricator.create_snapshot(w, sg)
    assert snap.world_hash == w.world_hash
    assert len(snap.cells) == len(w.cells)
    assert len(snap.scene_graph_hash) == 64


def test_scene_graph():
    sg = WorldSceneGraph(root_id="ROOT")
    root = SceneNode("ROOT", node_type=SceneNodeType.WORLD)
    child = SceneNode("CHILD_01", parent_id="ROOT", node_type=SceneNodeType.REGION)
    sg.add_node(root)
    sg.add_node(child)
    assert "ROOT" in sg.nodes
    assert "CHILD_01" in sg.nodes
    assert "CHILD_01" in sg.nodes["ROOT"].children


def test_scene_hierarchy():
    sg = WorldSceneGraph(root_id="ROOT")
    sg.add_node(SceneNode("ROOT", node_type=SceneNodeType.WORLD))
    sg.add_node(SceneNode("N1", parent_id="ROOT", node_type=SceneNodeType.CELL))
    sg.add_node(SceneNode("N2", parent_id="N1", node_type=SceneNodeType.STRUCTURE))
    issues = sg.validate_hierarchy()
    assert len(issues) == 0


def test_scene_transform():
    t = WorldTransform(translation=(100.0, 200.0, 300.0), rotation=(0.0, 45.0, 0.0), scale=(1.0, 2.0, 1.0))
    d = t.to_dict()
    assert d["translation"] == [100.0, 200.0, 300.0]
    assert d["rotation"] == [0.0, 45.0, 0.0]
    assert d["scale"] == [1.0, 2.0, 1.0]
