"""
Tests for Natural Ecosystem System Fabricator, Validator, and Package.
UAF-81.51 Sections 135, 139, 142.
"""

from uaf.natural_ecosystem.engine.natural_ecosystem_fabricator import NaturalEcosystemFabricationPlatform
from uaf.natural_ecosystem.validation.natural_ecosystem_validator import NaturalEcosystemValidator
from uaf.natural_ecosystem.package.natural_ecosystem_package import NaturalEcosystemPackage


def test_natural_ecosystem_system_fabrication_all_six_golden_environments():
    builders = [
        NaturalEcosystemFabricationPlatform.build_golden_forest,
        NaturalEcosystemFabricationPlatform.build_golden_desert,
        NaturalEcosystemFabricationPlatform.build_golden_mountain,
        NaturalEcosystemFabricationPlatform.build_golden_swamp,
        NaturalEcosystemFabricationPlatform.build_golden_coastal,
        NaturalEcosystemFabricationPlatform.build_golden_hybrid,
    ]

    for builder in builders:
        spec, land_path, fol_path, water_path, nav_path = builder()
        assert spec.is_valid_ecosystem is True
        assert land_path.startswith("/Game/Environments/Natural/")
        assert fol_path.startswith("/Game/Environments/Natural/")
        assert water_path.startswith("/Game/Environments/Natural/")
        assert nav_path.startswith("/Game/Environments/Natural/")


def test_natural_ecosystem_package_validation_and_serialization():
    spec, land_path, fol_path, water_path, nav_path = NaturalEcosystemFabricationPlatform.build_golden_forest("Eco_PkgForest51")

    report = NaturalEcosystemValidator.validate_natural_ecosystem(spec, land_path, fol_path, water_path, nav_path)
    assert report.is_valid is True
    assert report.review_status == "PASSED"
    assert report.quality_score.aggregate_score >= 0.85

    pkg = NaturalEcosystemPackage(
        ecosystem_id="Eco_PkgForest51",
        spec=spec,
        landscape_asset_path=land_path,
        foliage_asset_path=fol_path,
        water_mesh_path=water_path,
        navmesh_path=nav_path,
        validation_report=report,
    )

    assert len(pkg.package_hash) == 64
    data = pkg.to_dict()
    assert data["ecosystem_id"] == "Eco_PkgForest51"
    assert data["spec"]["biome"] == "FOREST"
    assert data["validation_report"]["review_status"] == "PASSED"
