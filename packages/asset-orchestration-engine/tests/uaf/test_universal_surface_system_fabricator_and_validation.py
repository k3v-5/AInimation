"""
Tests for Universal Surface System Fabricator, Validator, and Package.
UAF-81.52 Sections 143, 147, 150.
"""

from uaf.universal_surface.engine.universal_surface_fabricator import UniversalSurfaceFabricationPlatform
from uaf.universal_surface.validation.universal_surface_validator import UniversalSurfaceValidator
from uaf.universal_surface.package.universal_surface_package import UniversalSurfacePackage


def test_universal_surface_system_fabrication_all_ten_golden_materials():
    builders = [
        UniversalSurfaceFabricationPlatform.build_golden_metal,
        UniversalSurfaceFabricationPlatform.build_golden_wood,
        UniversalSurfaceFabricationPlatform.build_golden_stone,
        UniversalSurfaceFabricationPlatform.build_golden_concrete,
        UniversalSurfaceFabricationPlatform.build_golden_fabric,
        UniversalSurfaceFabricationPlatform.build_golden_glass,
        UniversalSurfaceFabricationPlatform.build_golden_leather,
        UniversalSurfaceFabricationPlatform.build_golden_terrain,
        UniversalSurfaceFabricationPlatform.build_golden_vegetation,
        UniversalSurfaceFabricationPlatform.build_golden_water,
    ]

    for builder in builders:
        spec, mat_path, inst_path, tex_path = builder()
        assert spec.is_valid_surface is True
        assert mat_path.startswith("/Game/Materials/Universal/Master/")
        assert inst_path.startswith("/Game/Materials/Universal/Instances/")
        assert tex_path.startswith("/Game/Materials/Universal/Textures/")


def test_universal_surface_package_validation_and_serialization():
    spec, mat_path, inst_path, tex_path = UniversalSurfaceFabricationPlatform.build_golden_metal("Surf_PkgMetal52")

    report = UniversalSurfaceValidator.validate_universal_surface(spec, mat_path, inst_path, tex_path)
    assert report.is_valid is True
    assert report.review_status == "PASSED"
    assert report.quality_score.aggregate_score >= 0.85

    pkg = UniversalSurfacePackage(
        surface_id="Surf_PkgMetal52",
        spec=spec,
        master_material_path=mat_path,
        material_instance_path=inst_path,
        texture_set_path=tex_path,
        validation_report=report,
    )

    assert len(pkg.package_hash) == 64
    data = pkg.to_dict()
    assert data["surface_id"] == "Surf_PkgMetal52"
    assert data["spec"]["surface_type"] == "METAL"
    assert data["validation_report"]["review_status"] == "PASSED"
