"""
Tests for Vegetation System (UAF-81.56 Section 190).
"""

import pytest
from uaf.universal_world import (
    VegetationDefinition,
    VegetationSpecies,
    VegetationCategory,
    VegetationScatterProfile,
    ScatterDistributionType,
    FoliageDefinition,
    FoliageLayer,
    FoliageLODType,
    WorldBounds,
    UniversalWorldFabricator,
)


def test_vegetation_definition():
    v = VegetationDefinition()
    assert len(v.species) == 0
    assert len(v.scatter_profiles) == 0


def test_species():
    sp = VegetationSpecies(
        "SP_PINE",
        category=VegetationCategory.TREE,
        asset_variants=["/Game/Foliage/SM_Pine.uasset"],
        scale_range=(0.8, 1.5),
    )
    assert sp.category == VegetationCategory.TREE
    assert len(sp.asset_variants) == 1


def test_scatter():
    b = WorldBounds(-5000.0, 5000.0, -5000.0, 5000.0, 0.0, 1000.0)
    prof = VegetationScatterProfile(seed=101, distribution_type=ScatterDistributionType.POISSON)
    instances = UniversalWorldFabricator.scatter_assets(b, prof, "SM_Tree", max_count=15)
    assert len(instances) == 15
    assert all(b.contains_point(inst.position[0], inst.position[1], inst.position[2]) for inst in instances)


def test_poisson_scatter():
    b = WorldBounds(-2000.0, 2000.0, -2000.0, 2000.0, 0.0, 500.0)
    prof = VegetationScatterProfile(distribution_type=ScatterDistributionType.POISSON, min_distance=300.0)
    insts = UniversalWorldFabricator.scatter_assets(b, prof, "SM_Bush", max_count=10)
    assert len(insts) == 10


def test_grid_scatter():
    b = WorldBounds(-1000.0, 1000.0, -1000.0, 1000.0, 0.0, 100.0)
    prof = VegetationScatterProfile(distribution_type=ScatterDistributionType.GRID, min_distance=200.0)
    insts = UniversalWorldFabricator.scatter_assets(b, prof, "SM_Crop", max_count=25)
    assert len(insts) == 25


def test_cluster_scatter():
    b = WorldBounds(-3000.0, 3000.0, -3000.0, 3000.0, 0.0, 100.0)
    prof = VegetationScatterProfile(distribution_type=ScatterDistributionType.CLUSTER)
    insts = UniversalWorldFabricator.scatter_assets(b, prof, "SM_Fern", max_count=12)
    assert len(insts) == 12


def test_vegetation_mask():
    sp = VegetationSpecies("SP_BUSH", slope_rules=(0.0, 20.0), height_rules=(0.0, 800.0))
    assert sp.slope_rules[1] == 20.0
    assert sp.height_rules[1] == 800.0


def test_tree_variation():
    b = WorldBounds(-1000.0, 1000.0, -1000.0, 1000.0, 0.0, 100.0)
    prof = VegetationScatterProfile(scale_min=0.5, scale_max=2.0)
    insts = UniversalWorldFabricator.scatter_assets(b, prof, "SM_Tree", max_count=10)
    scales = [inst.scale[0] for inst in insts]
    assert min(scales) >= 0.5
    assert max(scales) <= 2.0


def test_foliage():
    fol = FoliageDefinition("F_FERN", layer=FoliageLayer.GROUND_COVER, density=0.4)
    assert fol.layer == FoliageLayer.GROUND_COVER
    assert fol.density == 0.4


def test_foliage_lod():
    fol = FoliageDefinition("F_GRASS", lod_type=FoliageLODType.BILLBOARD, cull_distance=10000.0)
    assert fol.lod_type == FoliageLODType.BILLBOARD
    assert fol.cull_distance == 10000.0


def test_vegetation_determinism():
    b = WorldBounds(-1000.0, 1000.0, -1000.0, 1000.0, 0.0, 100.0)
    prof1 = VegetationScatterProfile(seed=999)
    prof2 = VegetationScatterProfile(seed=999)
    insts1 = UniversalWorldFabricator.scatter_assets(b, prof1, "SM_Flower", max_count=8)
    insts2 = UniversalWorldFabricator.scatter_assets(b, prof2, "SM_Flower", max_count=8)
    assert [i.to_dict() for i in insts1] == [i.to_dict() for i in insts2]
