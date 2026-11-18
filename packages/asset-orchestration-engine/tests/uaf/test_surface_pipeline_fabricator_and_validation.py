"""
Tests for Surface Pipeline Fabricator, Validator, and Package.
UAF-81.27 Sections 130, 131, 132, 133, 127, 128.
"""

from uaf.surface_pipeline.engine.pipeline_fabricator import SurfacePipelineFabricationPlatform
from uaf.surface_pipeline.validation.pipeline_validator import SurfacePipelineValidator
from uaf.surface_pipeline.package.pipeline_package import SurfacePipelinePackage


def test_surface_pipeline_fabrication_all_four_scenarios():
    builders = [
        SurfacePipelineFabricationPlatform.build_character_surface,
        SurfacePipelineFabricationPlatform.build_weapon_surface,
        SurfacePipelineFabricationPlatform.build_environment_surface,
        SurfacePipelineFabricationPlatform.build_modular_kit_surface,
    ]

    for builder in builders:
        s_def, master_ref, inst_ref = builder()
        assert len(s_def.textures) >= 3
        assert master_ref.startswith("M_Master_")
        assert inst_ref.startswith("MI_")


def test_surface_pipeline_package_validation_and_serialization():
    s_def, master_ref, inst_ref = SurfacePipelineFabricationPlatform.build_weapon_surface("Wpn_PkgRifle")

    report = SurfacePipelineValidator.validate_surface(s_def, master_ref, inst_ref)
    assert report.is_valid is True
    assert report.review_status == "PASSED"
    assert report.quality_score.aggregate_score >= 0.85

    pkg = SurfacePipelinePackage(
        asset_id="Wpn_PkgRifle",
        surface_def=s_def,
        master_material_ref=master_ref,
        instance_material_ref=inst_ref,
        validation_report=report,
    )

    assert len(pkg.package_hash) == 64
    data = pkg.to_dict()
    assert data["asset_id"] == "Wpn_PkgRifle"
    assert len(data["surface_def"]["textures"]) >= 4
    assert data["validation_report"]["review_status"] == "PASSED"
