"""
Tests for Modular Architecture Fabricator, Validator, and Package.
UAF-81.31 Sections 129, 144, 145, 146.
"""

from uaf.modular_architecture.engine.architecture_fabricator import ModularArchitectureFabricationPlatform
from uaf.modular_architecture.validation.architecture_validator import ModularArchitectureValidator
from uaf.modular_architecture.package.architecture_package import ModularArchitecturePackage


def test_modular_architecture_fabrication_all_four_kits():
    builders = [
        ModularArchitectureFabricationPlatform.build_scifi_corridor_kit,
        ModularArchitectureFabricationPlatform.build_industrial_room_kit,
        ModularArchitectureFabricationPlatform.build_urban_building_kit,
        ModularArchitectureFabricationPlatform.build_bunker_kit,
    ]

    for builder in builders:
        kit_def, mesh_refs, mat_ref = builder()
        assert kit_def.is_valid_grid is True
        assert len(kit_def.pieces) == 4
        assert len(mesh_refs) == 4
        assert mat_ref.startswith("M_Master_")


def test_modular_architecture_package_validation_and_serialization():
    kit_def, mesh_refs, mat_ref = ModularArchitectureFabricationPlatform.build_scifi_corridor_kit("Kit_PkgSciFi")

    report = ModularArchitectureValidator.validate_architecture_kit(kit_def, mesh_refs, mat_ref)
    assert report.is_valid is True
    assert report.review_status == "PASSED"
    assert report.quality_score.aggregate_score >= 0.85

    pkg = ModularArchitecturePackage(
        asset_id="Kit_PkgSciFi",
        kit_def=kit_def,
        static_mesh_refs=mesh_refs,
        master_material_ref=mat_ref,
        validation_report=report,
    )

    assert len(pkg.package_hash) == 64
    data = pkg.to_dict()
    assert data["asset_id"] == "Kit_PkgSciFi"
    assert len(data["kit_def"]["pieces"]) == 4
    assert data["validation_report"]["review_status"] == "PASSED"
