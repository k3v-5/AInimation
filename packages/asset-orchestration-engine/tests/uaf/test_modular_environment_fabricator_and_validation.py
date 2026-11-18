"""
Tests for Modular Environment Fabricator, Validator, and Package.
UAF-81.47 Sections 131, 151, 167.
"""

from uaf.modular_environment.engine.modular_environment_fabricator import ModularEnvironmentFabricationPlatform
from uaf.modular_environment.validation.modular_environment_validator import ModularEnvironmentValidator
from uaf.modular_environment.package.modular_environment_package import ModularEnvironmentPackage


def test_modular_environment_fabrication_all_six_golden_environments():
    builders = [
        ModularEnvironmentFabricationPlatform.build_golden_room,
        ModularEnvironmentFabricationPlatform.build_golden_corridor,
        ModularEnvironmentFabricationPlatform.build_golden_building,
        ModularEnvironmentFabricationPlatform.build_golden_facility,
        ModularEnvironmentFabricationPlatform.build_golden_indoor_map,
        ModularEnvironmentFabricationPlatform.build_golden_outdoor_map,
    ]

    for builder in builders:
        spec, level_path, nav_path, col_path = builder()
        assert spec.is_valid_environment is True
        assert level_path.startswith("/Game/Environments/Modular/Levels/")
        assert nav_path.startswith("/Game/Environments/Modular/Nav/")
        assert col_path.startswith("/Game/Environments/Modular/Collision/")


def test_modular_environment_package_validation_and_serialization():
    spec, level_path, nav_path, col_path = ModularEnvironmentFabricationPlatform.build_golden_room("Env_PkgRoom")

    report = ModularEnvironmentValidator.validate_modular_environment(spec, level_path, nav_path, col_path)
    assert report.is_valid is True
    assert report.review_status == "PASSED"
    assert report.quality_score.aggregate_score >= 0.85

    pkg = ModularEnvironmentPackage(
        environment_id="Env_PkgRoom",
        spec=spec,
        level_asset_path=level_path,
        navmesh_path=nav_path,
        collision_asset_path=col_path,
        validation_report=report,
    )

    assert len(pkg.package_hash) == 64
    data = pkg.to_dict()
    assert data["environment_id"] == "Env_PkgRoom"
    assert data["spec"]["style"] == "SCI_FI"
    assert data["validation_report"]["review_status"] == "PASSED"
