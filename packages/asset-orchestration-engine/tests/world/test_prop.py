"""
Tests for Prop System & Exclusion Volumes (UAF-81.56 Section 192).
"""

import pytest
from uaf.universal_world import (
    PropDefinition,
    PropCategory,
    PropPlacementMode,
    ExclusionVolume,
    ExclusionVolumeType,
    WorldBounds,
    VegetationScatterProfile,
    UniversalWorldFabricator,
)


def test_prop_definition():
    p = PropDefinition("P_FENCE_01", PropCategory.FENCE, ["/Game/Props/SM_Fence.uasset"])
    assert p.category == PropCategory.FENCE
    assert len(p.asset_variants) == 1


def test_prop_placement():
    p = PropDefinition("P_SIGN", PropCategory.SIGN, placement_mode=PropPlacementMode.ROAD)
    assert p.placement_mode == PropPlacementMode.ROAD


def test_exclusion_volume():
    ex = ExclusionVolume("EX_01", ExclusionVolumeType.CIRCLE, center=(0.0, 0.0, 0.0), radius=500.0)
    assert ex.contains(100.0, 100.0, 0.0) is True
    assert ex.contains(1000.0, 1000.0, 0.0) is False


def test_prop_constraints():
    b = WorldBounds(-2000.0, 2000.0, -2000.0, 2000.0, 0.0, 100.0)
    ex = ExclusionVolume("EX_CENTER", ExclusionVolumeType.CIRCLE, center=(0.0, 0.0, 0.0), radius=500.0)
    prof = VegetationScatterProfile(seed=12)
    insts = UniversalWorldFabricator.scatter_assets(b, prof, "SM_Lamp", exclusion_volumes=[ex], max_count=20)
    # Ensure no instance was placed within exclusion zone
    for inst in insts:
        assert not ex.contains(inst.position[0], inst.position[1], inst.position[2])


def test_prop_determinism():
    p1 = PropDefinition("P_DET", PropCategory.BENCH)
    p2 = PropDefinition("P_DET", PropCategory.BENCH)
    assert p1.to_dict() == p2.to_dict()
