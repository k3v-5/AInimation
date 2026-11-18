"""
Tests for Pathfinding & Navigation System (UAF-81.57 Sections 72-78, 226).
"""

import math
import pytest
from uaf.universal_ai import (
    PathfindingAlgorithm,
    PathStatus,
    PathResult,
    DynamicObstacle,
    UniversalAIFabricator,
)


def test_pathfinding_algorithm_enum():
    algos = {a.value for a in PathfindingAlgorithm}
    expected = {"A_STAR", "DIJKSTRA", "FLOW_FIELD", "NAVMESH_QUERY", "GRID", "CUSTOM"}
    assert algos == expected


def test_path_status_enum():
    statuses = {s.value for s in PathStatus}
    expected = {"SUCCESS", "PARTIAL", "FAILED", "INVALID"}
    assert statuses == expected


def test_pathfinding_direct_unobstructed():
    start = (0.0, 0.0, 0.0)
    dest = (400.0, 0.0, 0.0)
    res = UniversalAIFabricator.compute_path(start, dest)

    assert res.status == PathStatus.SUCCESS
    assert len(res.waypoints) == 2
    assert res.waypoints[0] == start
    assert res.waypoints[1] == dest
    assert res.distance == 400.0


def test_pathfinding_distance_calculation():
    start = (0.0, 0.0, 0.0)
    dest = (300.0, 400.0, 0.0)
    res = UniversalAIFabricator.compute_path(start, dest)
    assert res.distance == 500.0


def test_pathfinding_estimated_time():
    start = (0.0, 0.0, 0.0)
    dest = (800.0, 0.0, 0.0)
    res = UniversalAIFabricator.compute_path(start, dest)
    # speed is 400.0 -> 800 / 400 = 2.0 sec
    assert res.estimated_time == 2.0


def test_pathfinding_dynamic_obstacle_avoidance():
    start = (0.0, 0.0, 0.0)
    dest = (1000.0, 0.0, 0.0)
    # Midpoint is (500, 0, 0)
    obs = DynamicObstacle(
        obstacle_id="FALLEN_TREE",
        position=(500.0, 0.0, 0.0),
        radius=100.0,
        is_active=True,
    )
    res = UniversalAIFabricator.compute_path(start, dest, obstacles=[obs])

    assert res.status == PathStatus.SUCCESS
    assert len(res.waypoints) == 3  # Detour included
    assert res.distance == 1000.0 * 1.3
    # Check that detour waypoint is displaced
    assert res.waypoints[1] == (650.0, 150.0, 0.0)


def test_pathfinding_inactive_obstacle_ignored():
    start = (0.0, 0.0, 0.0)
    dest = (1000.0, 0.0, 0.0)
    obs = DynamicObstacle(
        obstacle_id="GHOST_ROCK",
        position=(500.0, 0.0, 0.0),
        radius=100.0,
        is_active=False,
    )
    res = UniversalAIFabricator.compute_path(start, dest, obstacles=[obs])

    assert len(res.waypoints) == 2
    assert res.distance == 1000.0


def test_pathfinding_distant_obstacle_ignored():
    start = (0.0, 0.0, 0.0)
    dest = (1000.0, 0.0, 0.0)
    obs = DynamicObstacle(
        obstacle_id="DISTANT_ROCK",
        position=(500.0, 2000.0, 0.0),  # Far away
        radius=100.0,
        is_active=True,
    )
    res = UniversalAIFabricator.compute_path(start, dest, obstacles=[obs])

    assert len(res.waypoints) == 2
    assert res.distance == 1000.0


def test_pathfinding_cost_calculation():
    start = (0.0, 0.0, 0.0)
    dest = (600.0, 0.0, 0.0)
    res = UniversalAIFabricator.compute_path(start, dest)
    assert res.cost == 600.0 * 0.01


def test_path_result_to_dict():
    res = PathResult(
        status=PathStatus.SUCCESS,
        waypoints=[(0.0, 0.0, 0.0), (100.0, 0.0, 0.0)],
        distance=100.0,
        estimated_time=0.25,
    )
    d = res.to_dict()
    assert d["status"] == "SUCCESS"
    assert d["waypoint_count"] == 2
    assert d["distance"] == 100.0
    assert d["estimated_time"] == 0.25
