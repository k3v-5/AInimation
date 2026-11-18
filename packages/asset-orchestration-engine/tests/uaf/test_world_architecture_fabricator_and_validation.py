"""
Tests for World Architecture Fabricator, Validator, and Package.
UAF-81.24 Sections 149, 150, 151, 152, 153, 154, 156.
"""

from uaf.world_architecture.engine.architecture_fabricator import WorldArchitectureFabricationPlatform
from uaf.world_architecture.validation.architecture_validator import WorldArchitectureValidator
from uaf.world_architecture.package.architecture_package import WorldArchitecturePackage


def test_world_architecture_fabrication_all_nine_reference_worlds():
    builders = [
        WorldArchitectureFabricationPlatform.build_small_interior_world,
        WorldArchitectureFabricationPlatform.build_modular_building_world,
        WorldArchitectureFabricationPlatform.build_industrial_complex_world,
        WorldArchitectureFabricationPlatform.build_outdoor_area_world,
        WorldArchitectureFabricationPlatform.build_forest_world,
        WorldArchitectureFabricationPlatform.build_desert_world,
        WorldArchitectureFabricationPlatform.build_urban_block_world,
        WorldArchitectureFabricationPlatform.build_multi_level_world,
        WorldArchitectureFabricationPlatform.build_combat_arena_world,
    ]

    for builder in builders:
        w_def, graph, grid_cells, landmarks = builder()
        assert w_def.bounds.is_valid is True
        assert graph.is_fully_connected() is True
        assert graph.is_critical_path_valid() is True
        assert len(grid_cells) >= 1
        assert len(landmarks) >= 1


def test_world_architecture_package_validation_and_serialization():
    w_def, graph, grid_cells, landmarks = WorldArchitectureFabricationPlatform.build_modular_building_world("World_PkgBuilding")

    report = WorldArchitectureValidator.validate_world(w_def, graph, landmarks)
    assert report.is_valid is True
    assert report.review_status == "PASSED"
    assert report.quality_score.aggregate_score >= 0.85

    pkg = WorldArchitecturePackage(
        asset_id="World_PkgBuilding",
        world_def=w_def,
        graph=graph,
        grid_cells=grid_cells,
        landmarks=landmarks,
        validation_report=report,
    )

    assert len(pkg.package_hash) == 64
    data = pkg.to_dict()
    assert data["asset_id"] == "World_PkgBuilding"
    assert len(data["grid_cells"]) >= 4
    assert data["validation_report"]["review_status"] == "PASSED"
