"""
Tests for Modular Assembly System Fabricator, Validator, and Package.
UAF-81.50 Sections 149, 153, 156.
"""

from uaf.modular_assembly_system.engine.modular_assembly_fabricator import ModularAssemblyFabricationPlatform
from uaf.modular_assembly_system.validation.modular_assembly_validator import ModularAssemblyValidator
from uaf.modular_assembly_system.package.modular_assembly_package import ModularAssemblyPackage


def test_modular_assembly_system_fabrication_all_five_golden_environments():
    builders = [
        ModularAssemblyFabricationPlatform.build_golden_interior,
        ModularAssemblyFabricationPlatform.build_golden_facility,
        ModularAssemblyFabricationPlatform.build_golden_urban_block,
        ModularAssemblyFabricationPlatform.build_golden_industrial,
        ModularAssemblyFabricationPlatform.build_golden_dungeon,
    ]

    for builder in builders:
        spec, lvl_path, part_path, nav_path = builder()
        assert spec.is_valid_assembly is True
        assert lvl_path.startswith("/Game/Environments/Assembly/Levels/")
        assert part_path.startswith("/Game/Environments/Assembly/Levels/")
        assert nav_path.startswith("/Game/Environments/Assembly/Levels/")


def test_modular_assembly_package_validation_and_serialization():
    spec, lvl_path, part_path, nav_path = ModularAssemblyFabricationPlatform.build_golden_interior("Env_PkgInterior50")

    report = ModularAssemblyValidator.validate_modular_assembly(spec, lvl_path, part_path, nav_path)
    assert report.is_valid is True
    assert report.review_status == "PASSED"
    assert report.quality_score.aggregate_score >= 0.85

    pkg = ModularAssemblyPackage(
        environment_id="Env_PkgInterior50",
        spec=spec,
        level_asset_path=lvl_path,
        world_partition_path=part_path,
        navmesh_path=nav_path,
        validation_report=report,
    )

    assert len(pkg.package_hash) == 64
    data = pkg.to_dict()
    assert data["environment_id"] == "Env_PkgInterior50"
    assert data["spec"]["environment_type"] == "INTERIOR"
    assert data["validation_report"]["review_status"] == "PASSED"
