"""
Tests for Character Assembly Fabricator, Validator, and Package.
UAF-81.42 Sections 144, 147, 148, 163.
"""

from uaf.character_assembly.engine.character_assembly_fabricator import CharacterAssemblyFabricationPlatform
from uaf.character_assembly.validation.character_assembly_validator import CharacterAssemblyValidator
from uaf.character_assembly.package.character_assembly_package import CharacterAssemblyPackage


def test_character_assembly_fabrication_all_six_golden_characters():
    builders = [
        CharacterAssemblyFabricationPlatform.build_golden_humanoid,
        CharacterAssemblyFabricationPlatform.build_golden_robot,
        CharacterAssemblyFabricationPlatform.build_golden_creature,
        CharacterAssemblyFabricationPlatform.build_golden_quadruped,
        CharacterAssemblyFabricationPlatform.build_golden_mechanical,
        CharacterAssemblyFabricationPlatform.build_golden_hybrid,
    ]

    for builder in builders:
        spec, sk_path, abp_path, phys_path = builder()
        assert spec.is_valid_assembly is True
        assert sk_path.startswith("/Game/Characters/Meshes/")
        assert abp_path.startswith("/Game/Characters/Animations/")
        assert phys_path.startswith("/Game/Characters/Physics/")


def test_character_assembly_package_validation_and_serialization():
    spec, sk_path, abp_path, phys_path = CharacterAssemblyFabricationPlatform.build_golden_humanoid("Char_PkgHumanoid")

    report = CharacterAssemblyValidator.validate_character_assembly(spec, sk_path, abp_path, phys_path)
    assert report.is_valid is True
    assert report.review_status == "PASSED"
    assert report.quality_score.aggregate_score >= 0.85

    pkg = CharacterAssemblyPackage(
        character_id="Char_PkgHumanoid",
        spec=spec,
        skeletal_mesh_path=sk_path,
        anim_blueprint_path=abp_path,
        physics_asset_path=phys_path,
        validation_report=report,
    )

    assert len(pkg.package_hash) == 64
    data = pkg.to_dict()
    assert data["character_id"] == "Char_PkgHumanoid"
    assert data["spec"]["classification"] == "HUMANOID"
    assert data["validation_report"]["review_status"] == "PASSED"
