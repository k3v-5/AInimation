"""
Tests for Surface Lookdev Fabricator, Validator, and Package.
UAF-81.38 Sections 143, 147, 149.
"""

from uaf.surface_lookdev.engine.surface_lookdev_fabricator import SurfaceLookdevFabricationPlatform
from uaf.surface_lookdev.validation.surface_lookdev_validator import SurfaceLookdevValidator
from uaf.surface_lookdev.package.surface_lookdev_package import SurfaceLookdevPackage


def test_surface_lookdev_fabrication_all_fourteen_golden_surfaces():
    builders = [
        SurfaceLookdevFabricationPlatform.build_golden_skin,
        SurfaceLookdevFabricationPlatform.build_golden_metal,
        SurfaceLookdevFabricationPlatform.build_golden_fabric,
        SurfaceLookdevFabricationPlatform.build_golden_leather,
        SurfaceLookdevFabricationPlatform.build_golden_concrete,
        SurfaceLookdevFabricationPlatform.build_golden_rock,
        SurfaceLookdevFabricationPlatform.build_golden_wood,
        SurfaceLookdevFabricationPlatform.build_golden_glass,
        SurfaceLookdevFabricationPlatform.build_golden_plastic,
        SurfaceLookdevFabricationPlatform.build_golden_energy,
        SurfaceLookdevFabricationPlatform.build_golden_robot_surface,
        SurfaceLookdevFabricationPlatform.build_golden_armor_surface,
        SurfaceLookdevFabricationPlatform.build_golden_weapon_surface,
        SurfaceLookdevFabricationPlatform.build_golden_environment_surface,
    ]

    for builder in builders:
        spec, master_path, inst_path = builder()
        assert spec.properties.is_valid is True
        assert spec.is_valid_resolution is True
        assert master_path.startswith("/Game/Materials/Masters/")
        assert inst_path.startswith("/Game/Materials/Instances/")


def test_surface_lookdev_package_validation_and_serialization():
    spec, master_path, inst_path = SurfaceLookdevFabricationPlatform.build_golden_weapon_surface("Lookdev_PkgWeapon")

    report = SurfaceLookdevValidator.validate_surface_lookdev(spec, master_path, inst_path)
    assert report.is_valid is True
    assert report.review_status == "PASSED"
    assert report.quality_score.aggregate_score >= 0.85

    pkg = SurfaceLookdevPackage(
        surface_id="Lookdev_PkgWeapon",
        spec=spec,
        master_material_path=master_path,
        material_instance_path=inst_path,
        validation_report=report,
    )

    assert len(pkg.package_hash) == 64
    data = pkg.to_dict()
    assert data["surface_id"] == "Lookdev_PkgWeapon"
    assert data["spec"]["material_type"] == "METAL"
    assert data["validation_report"]["review_status"] == "PASSED"
