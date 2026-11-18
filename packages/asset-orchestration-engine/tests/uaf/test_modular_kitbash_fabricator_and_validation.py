"""
Tests for Modular Kitbash Fabricator, Validator, and Package.
UAF-81.39 Sections 136, 140, 146.
"""

from uaf.modular_kitbash.engine.modular_kitbash_fabricator import ModularKitbashFabricationPlatform
from uaf.modular_kitbash.validation.modular_kitbash_validator import ModularKitbashValidator
from uaf.modular_kitbash.package.modular_kitbash_package import ModularKitbashPackage


def test_modular_kitbash_fabrication_all_six_golden_assemblies():
    builders = [
        ModularKitbashFabricationPlatform.build_golden_corridor,
        ModularKitbashFabricationPlatform.build_golden_room,
        ModularKitbashFabricationPlatform.build_golden_building,
        ModularKitbashFabricationPlatform.build_golden_industrial_facility,
        ModularKitbashFabricationPlatform.build_golden_sci_fi_facility,
        ModularKitbashFabricationPlatform.build_golden_modular_kit,
    ]

    for builder in builders:
        spec, sm_path, bp_path = builder()
        assert spec.is_valid_structure is True
        assert sm_path.startswith("/Game/ModularKits/Meshes/")
        assert bp_path.startswith("/Game/ModularKits/Blueprints/")


def test_modular_kitbash_package_validation_and_serialization():
    spec, sm_path, bp_path = ModularKitbashFabricationPlatform.build_golden_room("Kitbash_PkgRoom")

    report = ModularKitbashValidator.validate_modular_kitbash(spec, sm_path, bp_path)
    assert report.is_valid is True
    assert report.review_status == "PASSED"
    assert report.quality_score.aggregate_score >= 0.85

    pkg = ModularKitbashPackage(
        kitbash_id="Kitbash_PkgRoom",
        spec=spec,
        static_mesh_path=sm_path,
        blueprint_path=bp_path,
        validation_report=report,
    )

    assert len(pkg.package_hash) == 64
    data = pkg.to_dict()
    assert data["kitbash_id"] == "Kitbash_PkgRoom"
    assert data["spec"]["kit_style"] == "LAB_KIT"
    assert data["validation_report"]["review_status"] == "PASSED"
