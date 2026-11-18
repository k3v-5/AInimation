"""
Tests for World Building Fabricator, Validator, and Package.
UAF-81.28 Sections 60 to 77, 118, 122.
"""

from uaf.world_building.engine.building_fabricator import WorldBuildingFabricationPlatform
from uaf.world_building.validation.building_validator import WorldBuildingValidator
from uaf.world_building.package.building_package import WorldBuildingPackage


def test_world_building_fabrication_all_five_scenarios():
    builders = [
        WorldBuildingFabricationPlatform.build_interior_facility_world,
        WorldBuildingFabricationPlatform.build_urban_block_world,
        WorldBuildingFabricationPlatform.build_industrial_complex_world,
        WorldBuildingFabricationPlatform.build_combat_arena_world,
        WorldBuildingFabricationPlatform.build_dungeon_complex_world,
    ]

    for builder in builders:
        w_def, graph, lvl_ref = builder()
        assert w_def.is_valid_grid is True
        assert len(w_def.module_blocks) >= 4
        assert graph.is_fully_connected() is True
        assert graph.is_critical_path_connected() is True
        assert lvl_ref.startswith("LV_")


def test_world_building_package_validation_and_serialization():
    w_def, graph, lvl_ref = WorldBuildingFabricationPlatform.build_interior_facility_world("World_PkgFacility")

    report = WorldBuildingValidator.validate_world_build(w_def, graph, lvl_ref)
    assert report.is_valid is True
    assert report.review_status == "PASSED"
    assert report.quality_score.aggregate_score >= 0.85

    pkg = WorldBuildingPackage(
        asset_id="World_PkgFacility",
        world_def=w_def,
        graph=graph,
        level_ref=lvl_ref,
        validation_report=report,
    )

    assert len(pkg.package_hash) == 64
    data = pkg.to_dict()
    assert data["asset_id"] == "World_PkgFacility"
    assert len(data["world_def"]["module_blocks"]) >= 5
    assert data["validation_report"]["review_status"] == "PASSED"
