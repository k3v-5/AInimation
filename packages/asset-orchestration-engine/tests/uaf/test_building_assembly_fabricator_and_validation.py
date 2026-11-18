"""
Tests for Building Assembly Fabricator, Validator, and Package.
UAF-81.35 Sections 133, 136, 137, 138.
"""

from uaf.building_assembly.engine.building_assembly_fabricator import BuildingAssemblyFabricationPlatform
from uaf.building_assembly.validation.building_assembly_validator import BuildingAssemblyValidator
from uaf.building_assembly.package.building_assembly_package import BuildingAssemblyPackage


def test_building_assembly_fabrication_all_six_golden_worlds():
    builders = [
        BuildingAssemblyFabricationPlatform.build_golden_room,
        BuildingAssemblyFabricationPlatform.build_golden_corridor,
        BuildingAssemblyFabricationPlatform.build_golden_building,
        BuildingAssemblyFabricationPlatform.build_golden_facility,
        BuildingAssemblyFabricationPlatform.build_golden_combat_area,
        BuildingAssemblyFabricationPlatform.build_golden_city_block,
    ]

    for builder in builders:
        spec, level_path = builder()
        assert spec.is_valid_grid is True
        assert len(spec.rooms) >= 1
        assert level_path.startswith("/Game/Environments/Levels/")


def test_building_assembly_package_validation_and_serialization():
    spec, level_path = BuildingAssemblyFabricationPlatform.build_golden_facility("World_PkgFacility")

    report = BuildingAssemblyValidator.validate_building_assembly(spec, level_path)
    assert report.is_valid is True
    assert report.review_status == "PASSED"
    assert report.quality_score.aggregate_score >= 0.85

    pkg = BuildingAssemblyPackage(
        world_id="World_PkgFacility",
        spec=spec,
        level_asset_path=level_path,
        validation_report=report,
    )

    assert len(pkg.package_hash) == 64
    data = pkg.to_dict()
    assert data["world_id"] == "World_PkgFacility"
    assert data["spec"]["world_type"] == "FACILITY"
    assert data["validation_report"]["review_status"] == "PASSED"
