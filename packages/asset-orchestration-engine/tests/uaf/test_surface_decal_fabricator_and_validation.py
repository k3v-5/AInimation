"""
Tests for Surface Decal Fabricator, Validator, and Package.
UAF-81.34 Sections 7, 127, 145, 146.
"""

from uaf.surface_decal.engine.surface_decal_fabricator import SurfaceDecalFabricationPlatform
from uaf.surface_decal.validation.surface_decal_validator import SurfaceDecalValidator
from uaf.surface_decal.package.surface_decal_package import SurfaceDecalPackage


def test_surface_decal_fabrication_all_ten_golden_presets():
    builders = [
        SurfaceDecalFabricationPlatform.build_golden_brushed_steel,
        SurfaceDecalFabricationPlatform.build_golden_damaged_steel,
        SurfaceDecalFabricationPlatform.build_golden_black_rubber,
        SurfaceDecalFabricationPlatform.build_golden_tactical_fabric,
        SurfaceDecalFabricationPlatform.build_golden_human_skin,
        SurfaceDecalFabricationPlatform.build_golden_alien_skin,
        SurfaceDecalFabricationPlatform.build_golden_concrete,
        SurfaceDecalFabricationPlatform.build_golden_rusted_metal,
        SurfaceDecalFabricationPlatform.build_golden_polished_chrome,
        SurfaceDecalFabricationPlatform.build_golden_obsidian,
    ]

    for builder in builders:
        spec, master_ref, inst_ref = builder()
        assert spec.is_valid_pbr is True
        assert master_ref.startswith("M_Master_")
        assert inst_ref.startswith("MI_")


def test_surface_decal_package_validation_and_serialization():
    spec, master_ref, inst_ref = SurfaceDecalFabricationPlatform.build_golden_damaged_steel("Mat_PkgDamagedSteel")

    report = SurfaceDecalValidator.validate_surface_authoring(spec, master_ref, inst_ref)
    assert report.is_valid is True
    assert report.review_status == "PASSED"
    assert report.quality_score.aggregate_score >= 0.85

    pkg = SurfaceDecalPackage(
        asset_id="Mat_PkgDamagedSteel",
        surface_spec=spec,
        master_material_ref=master_ref,
        instance_material_ref=inst_ref,
        validation_report=report,
    )

    assert len(pkg.package_hash) == 64
    data = pkg.to_dict()
    assert data["asset_id"] == "Mat_PkgDamagedSteel"
    assert data["surface_spec"]["material_family"] == "METAL"
    assert data["validation_report"]["review_status"] == "PASSED"
