"""
Tests for Character Pipeline Fabricator, Validator, and Package.
UAF-81.37 Sections 136, 153, 155.
"""

from uaf.character_pipeline.engine.character_pipeline_fabricator import CharacterPipelineFabricationPlatform
from uaf.character_pipeline.validation.character_pipeline_validator import CharacterPipelineValidator
from uaf.character_pipeline.package.character_pipeline_package import CharacterPipelinePackage


def test_character_pipeline_fabrication_all_ten_golden_characters():
    builders = [
        CharacterPipelineFabricationPlatform.build_golden_human_male,
        CharacterPipelineFabricationPlatform.build_golden_human_female,
        CharacterPipelineFabricationPlatform.build_golden_heavy_soldier,
        CharacterPipelineFabricationPlatform.build_golden_light_soldier,
        CharacterPipelineFabricationPlatform.build_golden_robot,
        CharacterPipelineFabricationPlatform.build_golden_android,
        CharacterPipelineFabricationPlatform.build_golden_alien,
        CharacterPipelineFabricationPlatform.build_golden_creature,
        CharacterPipelineFabricationPlatform.build_golden_boss,
        CharacterPipelineFabricationPlatform.build_golden_armored_character,
    ]

    for builder in builders:
        spec, sk_path, phys_path = builder()
        assert spec.is_valid_rig_structure is True
        assert sk_path.startswith("/Game/Characters/Meshes/")
        assert phys_path.startswith("/Game/Characters/Physics/")


def test_character_pipeline_package_validation_and_serialization():
    spec, sk_path, phys_path = CharacterPipelineFabricationPlatform.build_golden_heavy_soldier("Char_PkgHeavy")

    report = CharacterPipelineValidator.validate_character_pipeline(spec, sk_path, phys_path)
    assert report.is_valid is True
    assert report.review_status == "PASSED"
    assert report.quality_score.aggregate_score >= 0.85

    pkg = CharacterPipelinePackage(
        character_id="Char_PkgHeavy",
        spec=spec,
        skeletal_mesh_path=sk_path,
        physics_asset_path=phys_path,
        validation_report=report,
    )

    assert len(pkg.package_hash) == 64
    data = pkg.to_dict()
    assert data["character_id"] == "Char_PkgHeavy"
    assert data["spec"]["archetype"] == "HEAVY"
    assert data["validation_report"]["review_status"] == "PASSED"
