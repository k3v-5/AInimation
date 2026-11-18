"""
Tests for Impostor System (UAF-81.56 Section 199).
"""

import pytest
from uaf.universal_world import (
    ImpostorDefinition,
    UniversalWorldFabricator,
)


def test_impostor_definition():
    imp = ImpostorDefinition("IMP_TREE", "SM_Tree_Oak", resolution=512, directions=16)
    assert imp.impostor_id == "IMP_TREE"
    assert imp.source_asset_id == "SM_Tree_Oak"
    assert imp.resolution == 512
    assert imp.directions == 16


def test_impostor_generation():
    world = UniversalWorldFabricator.create_base_world("W_IMP", "Imp World")
    assert len(world.impostors) >= 1
    assert world.impostors[0].billboard_count == 8


def test_impostor_orientation():
    imp = ImpostorDefinition("IMP_DIR", "SM_Rock", directions=32)
    assert imp.directions == 32


def test_impostor_alpha():
    imp = ImpostorDefinition("IMP_ALPHA", "SM_Bush", alpha_threshold=0.5)
    assert imp.alpha_threshold == 0.5


def test_impostor_validation():
    imp = ImpostorDefinition("IMP_VAL", "SM_Foliage", distance=40000.0)
    d = imp.to_dict()
    assert d["distance"] == 40000.0
