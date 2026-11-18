"""
Tests for PBR Surface Fabricator, Validator, and Package.
UAF-81.43 Sections 149, 166, 178.
"""

from uaf.pbr_surface.engine.pbr_surface_fabricator import PBRSurfaceFabricationPlatform
from uaf.pbr_surface.validation.pbr_surface_validator import PBRSurfaceValidator
from uaf.pbr_surface.package.pbr_surface_package import PBRSurfacePackage


def test_pbr_surface_fabrication_all_ten_golden_materials():
    builders = [
        PBRSurfaceFabricationPlatform.build_golden_skin,
        PBRSurfaceFabricationPlatform.build_golden_metal,
        PBRSurfaceFabricationPlatform.build_golden_painted_metal,
        PBRSurfaceFabricationPlatform.build_golden_fabric,
        PBRSurfaceFabricationPlatform.build_golden_leather,
        PBRSurfaceFabricationPlatform.build_golden_concrete,
        PBRSurfaceFabricationPlatform.build_golden_glass,
        PBRSurfaceFabricationPlatform.build_golden_organic,
        PBRSurfaceFabricationPlatform.build_golden_emissive,
        PBRSurfaceFabricationPlatform.build_golden_technical,
    ]

    for builder in builders:
        spec, master_path, mi_path, tex_path = builder()
        assert spec.is_valid_surface is True
        assert master_path.startswith("/Game/Materials/Masters/")
        assert mi_path.startswith("/Game/Materials/Instances/")
        assert tex_path.startswith("/Game/Textures/Sets/")


def test_pbr_surface_package_validation_and_serialization():
    spec, master_path, mi_path, tex_path = PBRSurfaceFabricationPlatform.build_golden_metal("Mat_PkgMetal")

    report = PBRSurfaceValidator.validate_pbr_surface(spec, master_path, mi_path, tex_path)
    assert report.is_valid is True
    assert report.review_status == "PASSED"
    assert report.quality_score.aggregate_score >= 0.85

    pkg = PBRSurfacePackage(
        material_id="Mat_PkgMetal",
        spec=spec,
        master_material_path=master_path,
        material_instance_path=mi_path,
        texture_set_path=tex_path,
        validation_report=report,
    )

    assert len(pkg.package_hash) == 64
    data = pkg.to_dict()
    assert data["material_id"] == "Mat_PkgMetal"
    assert data["spec"]["category"] == "METAL"
    assert data["validation_report"]["review_status"] == "PASSED"
