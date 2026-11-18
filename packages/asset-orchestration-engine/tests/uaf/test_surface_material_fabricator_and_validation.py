"""
Tests for Surface Material Fabricator, Validator, and Package.
UAF-81.30 Sections 140, 142, 149, 160, 161.
"""

from uaf.surface_material.engine.material_fabricator import SurfaceMaterialProductionPlatform
from uaf.surface_material.validation.material_validator import SurfaceMaterialValidator
from uaf.surface_material.package.material_package import SurfaceMaterialPackage


def test_surface_material_fabrication_all_eight_golden_surfaces():
    builders = [
        SurfaceMaterialProductionPlatform.build_golden_skin,
        SurfaceMaterialProductionPlatform.build_golden_metal,
        SurfaceMaterialProductionPlatform.build_golden_fabric,
        SurfaceMaterialProductionPlatform.build_golden_concrete,
        SurfaceMaterialProductionPlatform.build_golden_wood,
        SurfaceMaterialProductionPlatform.build_golden_glass,
        SurfaceMaterialProductionPlatform.build_golden_energy,
        SurfaceMaterialProductionPlatform.build_golden_terrain,
    ]

    for builder in builders:
        s_def, master_ref, inst_ref = builder()
        assert s_def.is_valid_pbr is True
        assert len(s_def.maps) >= 3
        assert master_ref.startswith("M_Master_")
        assert inst_ref.startswith("MI_")


def test_surface_material_package_validation_and_serialization():
    s_def, master_ref, inst_ref = SurfaceMaterialProductionPlatform.build_golden_metal("Surf_PkgMetal")

    report = SurfaceMaterialValidator.validate_surface_production(s_def, master_ref, inst_ref)
    assert report.is_valid is True
    assert report.review_status == "PASSED"
    assert report.quality_score.aggregate_score >= 0.85

    pkg = SurfaceMaterialPackage(
        asset_id="Surf_PkgMetal",
        surface_def=s_def,
        master_material_ref=master_ref,
        instance_material_ref=inst_ref,
        validation_report=report,
    )

    assert len(pkg.package_hash) == 64
    data = pkg.to_dict()
    assert data["asset_id"] == "Surf_PkgMetal"
    assert data["surface_def"]["surface_type"] == "METAL"
    assert data["validation_report"]["review_status"] == "PASSED"
