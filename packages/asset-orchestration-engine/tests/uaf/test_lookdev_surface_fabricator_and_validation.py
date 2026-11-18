"""
Tests for Lookdev Surface Fabricator, Validator, and Package.
UAF-81.46 Sections 114, 124, 125.
"""

from uaf.lookdev_surface.engine.lookdev_surface_fabricator import LookdevSurfaceFabricationPlatform
from uaf.lookdev_surface.validation.lookdev_surface_validator import LookdevSurfaceValidator
from uaf.lookdev_surface.package.lookdev_surface_package import LookdevSurfacePackage


def test_lookdev_surface_fabrication_all_seven_golden_surfaces():
    builders = [
        LookdevSurfaceFabricationPlatform.build_golden_skin,
        LookdevSurfaceFabricationPlatform.build_golden_metal,
        LookdevSurfaceFabricationPlatform.build_golden_fabric,
        LookdevSurfaceFabricationPlatform.build_golden_wood,
        LookdevSurfaceFabricationPlatform.build_golden_concrete,
        LookdevSurfaceFabricationPlatform.build_golden_glass,
        LookdevSurfaceFabricationPlatform.build_golden_organic,
    ]

    for builder in builders:
        spec, m_path, mi_path, t_path = builder()
        assert spec.is_valid_surface is True
        assert m_path.startswith("/Game/Lookdev/Materials/")
        assert mi_path.startswith("/Game/Lookdev/Instances/")
        assert t_path.startswith("/Game/Lookdev/Textures/")


def test_lookdev_surface_package_validation_and_serialization():
    spec, m_path, mi_path, t_path = LookdevSurfaceFabricationPlatform.build_golden_metal("Surf_PkgMetal")

    report = LookdevSurfaceValidator.validate_lookdev_surface(spec, m_path, mi_path, t_path)
    assert report.is_valid is True
    assert report.review_status == "PASSED"
    assert report.quality_score.aggregate_score >= 0.85

    pkg = LookdevSurfacePackage(
        surface_id="Surf_PkgMetal",
        spec=spec,
        master_material_path=m_path,
        material_instance_path=mi_path,
        texture_set_path=t_path,
        validation_report=report,
    )

    assert len(pkg.package_hash) == 64
    data = pkg.to_dict()
    assert data["surface_id"] == "Surf_PkgMetal"
    assert data["spec"]["material_family"] == "METAL"
    assert data["validation_report"]["review_status"] == "PASSED"
