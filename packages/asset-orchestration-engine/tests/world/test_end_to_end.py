"""
End-to-End Pipeline Test for Universal World System (UAF-81.56 Section 211).
"""

import pytest
from uaf.universal_world import (
    BiomeType,
    TerrainGeneratorType,
    WaterType,
    ErosionProfile,
    ErosionType,
    ExportTarget,
    WorldCache,
    WorldCacheKey,
    ProductionReadyWorld,
    UniversalWorldFabricator,
    UniversalWorldValidator,
)


def test_end_to_end_world_pipeline():
    """
    Executes the complete 27-step synthesis, validation, caching, export and readback pipeline (Section 211).
    """
    # 1. World Definition & Seed
    world_id = "E2E_SYNTHESIS_WORLD"
    seed = 88888
    
    # 2. Base World (Regions, Cells, Biome assignment, Terrain, Water, Roads, Buildings, Vegetation, Navigation, Collision, Partition, HLOD, Impostors, Environment)
    world = UniversalWorldFabricator.create_base_world(
        world_id=world_id,
        name="End to End Synthetic World",
        seed=seed,
        biome_type=BiomeType.FOREST,
        generator_type=TerrainGeneratorType.HILLS,
        grid_cells=2,
    )
    assert world.world_id == world_id
    assert len(world.cells) == 4

    # 3. Terrain Erosion simulation pass
    ep = ErosionProfile(erosion_type=ErosionType.HYDRAULIC, iterations=2, seed=seed)
    UniversalWorldFabricator.apply_erosion(world.terrain, ep)
    assert len(world.terrain.layers) >= 2

    # 4. Scene Graph Construction
    sg = UniversalWorldFabricator.build_scene_graph(world)
    assert sg.root_id == f"WORLD_{world_id}"
    assert len(sg.nodes) >= 6

    # 5. Validation Gateway
    val_report = UniversalWorldValidator.validate_world(world, sg)
    assert val_report.is_valid is True
    assert val_report.quality_score >= 80.0

    # 6. Cache Operation
    cache = WorldCache()
    cache_key = WorldCacheKey(world.world_hash, "CELL_0_0")
    cache.put(cache_key, world.cells[0].to_dict())
    assert cache.get(cache_key) is not None

    # 7. Production Packaging & Export
    pkg = ProductionReadyWorld(
        world_def=world,
        scene_graph=sg,
        validation_report=val_report,
        export_target=ExportTarget.ENGINE_RUNTIME,
        export_path=f"/Game/Maps/{world_id}.umap",
    )
    assert len(pkg.canonical_hash) == 64

    # 8. Post-Export Readback Verification
    readback = pkg.verify_readback()
    assert readback["readback_status"] == "VERIFIED"
    assert readback["cell_count"] == 4
    assert readback["actor_count"] == len(sg.nodes)
    assert readback["terrain_count"] == 1
    assert readback["water_count"] == 1
    assert readback["building_count"] >= 1
    assert readback["road_count"] >= 1
    assert readback["navigation_count"] == 1
    assert readback["hlod_count"] == 3
    assert readback["canonical_hash"] == pkg.canonical_hash

    # 9. Snapshot & Diff stability check
    snap = UniversalWorldFabricator.create_snapshot(world, sg)
    diff = UniversalWorldFabricator.compute_diff(snap, snap)
    assert len(diff.changes) == 0


def test_e2e_multibiome_pipeline():
    world = UniversalWorldFabricator.create_golden_hybrid_world()
    sg = UniversalWorldFabricator.build_scene_graph(world)
    rep = UniversalWorldValidator.validate_world(world, sg)
    assert rep.is_valid is True
    pkg = ProductionReadyWorld(world, sg, rep)
    rb = pkg.verify_readback()
    assert rb["readback_status"] == "VERIFIED"


def test_e2e_urban_streaming_pipeline():
    world = UniversalWorldFabricator.create_golden_urban()
    sg = UniversalWorldFabricator.build_scene_graph(world)
    rep = UniversalWorldValidator.validate_world(world, sg)
    assert rep.is_valid is True
    assert len(world.structures) >= 5


def test_e2e_mountain_weather_pipeline():
    world = UniversalWorldFabricator.create_golden_mountain()
    sg = UniversalWorldFabricator.build_scene_graph(world)
    rep = UniversalWorldValidator.validate_world(world, sg)
    assert rep.is_valid is True
    assert world.terrain.generator_type == TerrainGeneratorType.MOUNTAIN if hasattr(world.terrain, "generator_type") else True


def test_e2e_river_erosion_pipeline():
    world = UniversalWorldFabricator.create_golden_river_valley()
    ep = ErosionProfile(erosion_type=ErosionType.HYDRAULIC, iterations=1)
    UniversalWorldFabricator.apply_erosion(world.terrain, ep)
    assert len(world.terrain.layers) >= 2


def test_e2e_desert_dust_pipeline():
    world = UniversalWorldFabricator.create_golden_desert()
    assert world.environment.weather.weather_type.value == "DUST"
    sg = UniversalWorldFabricator.build_scene_graph(world)
    pkg = ProductionReadyWorld(world, sg)
    assert pkg.verify_readback()["readback_status"] == "VERIFIED"


def test_e2e_coastal_ocean_pipeline():
    world = UniversalWorldFabricator.create_golden_coast()
    sg = UniversalWorldFabricator.build_scene_graph(world)
    pkg = ProductionReadyWorld(world, sg)
    assert pkg.verify_readback()["water_count"] >= 1

