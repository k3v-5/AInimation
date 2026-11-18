"""
Tests for Landmark System (UAF-81.56 Section 202).
"""

import pytest
from uaf.universal_world import (
    LandmarkDefinition,
    LandmarkType,
    WorldBounds,
    UniversalWorldFabricator,
)


def test_landmark_definition():
    lm = LandmarkDefinition("LM_TOWER", "Wizard Tower", LandmarkType.TOWER, position=(500.0, 500.0, 200.0))
    assert lm.landmark_id == "LM_TOWER"
    assert lm.name == "Wizard Tower"
    assert lm.landmark_type == LandmarkType.TOWER


def test_landmark_visibility():
    lm = LandmarkDefinition("LM_VIS", "Citadel", visible_distance=80000.0)
    assert lm.visible_distance == 80000.0


def test_landmark_collision():
    lm = LandmarkDefinition("LM_COLL", "Rock Pillar", bounds=WorldBounds(-100.0, 100.0, -100.0, 100.0, 0.0, 1000.0))
    assert lm.bounds.size_z == 1000.0


def test_landmark_navigation():
    world = UniversalWorldFabricator.create_base_world("W_LM_NAV", "LM Nav")
    assert len(world.landmarks) >= 1
    assert world.landmarks[0].landmark_type == LandmarkType.MOUNTAIN


def test_landmark_validation():
    lm = LandmarkDefinition("LM_VAL", "Ancient Monolith", LandmarkType.MONUMENT)
    d = lm.to_dict()
    assert d["landmark_type"] == "MONUMENT"
