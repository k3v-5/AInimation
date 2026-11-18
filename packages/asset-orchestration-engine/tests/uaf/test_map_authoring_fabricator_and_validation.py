"""
Tests for Map Authoring Fabricator, Validator, and Package.
UAF-81.44 Sections 130, 134, 146.
"""

from uaf.map_authoring.engine.map_authoring_fabricator import MapAuthoringFabricationPlatform
from uaf.map_authoring.validation.map_authoring_validator import MapAuthoringValidator
from uaf.map_authoring.package.map_authoring_package import MapAuthoringPackage


def test_map_authoring_fabrication_all_six_golden_worlds():
    builders = [
        MapAuthoringFabricationPlatform.build_golden_industrial,
        MapAuthoringFabricationPlatform.build_golden_sci_fi_facility,
        MapAuthoringFabricationPlatform.build_golden_bunker,
        MapAuthoringFabricationPlatform.build_golden_outdoor,
        MapAuthoringFabricationPlatform.build_golden_forest,
        MapAuthoringFabricationPlatform.build_golden_combat_arena,
    ]

    for builder in builders:
        spec, level_path, part_path, nav_path = builder()
        assert spec.is_valid_map is True
        assert level_path.startswith("/Game/Maps/")
        assert part_path.startswith("/Game/Maps/")
        assert nav_path.startswith("/Game/Maps/")


def test_map_authoring_package_validation_and_serialization():
    spec, level_path, part_path, nav_path = MapAuthoringFabricationPlatform.build_golden_industrial("Map_PkgIndustrial")

    report = MapAuthoringValidator.validate_map_authoring(spec, level_path, part_path, nav_path)
    assert report.is_valid is True
    assert report.review_status == "PASSED"
    assert report.quality_score.aggregate_score >= 0.85

    pkg = MapAuthoringPackage(
        map_id="Map_PkgIndustrial",
        spec=spec,
        level_asset_path=level_path,
        world_partition_path=part_path,
        navmesh_path=nav_path,
        validation_report=report,
    )

    assert len(pkg.package_hash) == 64
    data = pkg.to_dict()
    assert data["map_id"] == "Map_PkgIndustrial"
    assert data["spec"]["theme"] == "INDUSTRIAL"
    assert data["validation_report"]["review_status"] == "PASSED"
