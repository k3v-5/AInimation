"""
Tests for Navigation System (UAF-81.56 Section 195).
"""

import pytest
from uaf.universal_world import (
    NavigationDefinition,
    NavigationSource,
    NavigationFlag,
    WorldQuery,
    WorldQueryType,
    UniversalWorldFabricator,
    UniversalWorldValidator,
)


def test_navigation_definition():
    nav = NavigationDefinition("NAV_TEST")
    assert nav.nav_id == "NAV_TEST"
    assert NavigationSource.TERRAIN in nav.sources
    assert NavigationFlag.WALKABLE in nav.flags


def test_navigation_source():
    nav = NavigationDefinition("NAV_SRC", sources=[NavigationSource.TERRAIN, NavigationSource.ROAD, NavigationSource.BUILDING])
    assert len(nav.sources) == 3


def test_navigation_region():
    nav = NavigationDefinition("NAV_REG", regions=["REGION_01", "REGION_02"])
    assert len(nav.regions) == 2


def test_navigation_connectivity():
    nav = NavigationDefinition("NAV_CONN", connectivity=True)
    assert nav.connectivity is True


def test_navigation_query():
    world = UniversalWorldFabricator.create_base_world("W_NAV_Q", "Nav Query")
    q = WorldQuery(WorldQueryType.NAVIGATION_AT, position=(0.0, 0.0, 500.0))
    res = UniversalWorldFabricator.solve_query(world, q)
    assert "walkable" in res
    assert res["walkable"] is True


def test_navigation_validation():
    world = UniversalWorldFabricator.create_base_world("W_NAV_VAL", "Nav Val")
    world.navigation.connectivity = False
    report = UniversalWorldValidator.validate_world(world)
    assert any("disconnected" in w.lower() for w in report.warnings)
