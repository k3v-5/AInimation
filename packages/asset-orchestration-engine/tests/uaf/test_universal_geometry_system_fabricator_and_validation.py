"""
Tests for Universal Geometry System Fabricator, Validator, and Package.
UAF-81.53 Sections 164, 165, 167.
"""

from uaf.universal_geometry.engine.universal_geometry_fabricator import UniversalGeometryFabricationPlatform
from uaf.universal_geometry.validation.universal_geometry_validator import UniversalGeometryValidator
from uaf.universal_geometry.package.universal_geometry_package import UniversalGeometryPackage


def test_universal_geometry_system_fabrication_all_ten_golden_meshes():
    builders = [
        UniversalGeometryFabricationPlatform.build_golden_character,
        UniversalGeometryFabricationPlatform.build_golden_robot,
        UniversalGeometryFabricationPlatform.build_golden_creature,
        UniversalGeometryFabricationPlatform.build_golden_weapon,
        UniversalGeometryFabricationPlatform.build_golden_prop,
        UniversalGeometryFabricationPlatform.build_golden_architecture,
        UniversalGeometryFabricationPlatform.build_golden_rock,
        UniversalGeometryFabricationPlatform.build_golden_tree,
        UniversalGeometryFabricationPlatform.build_golden_modular_kit,
        UniversalGeometryFabricationPlatform.build_golden_complex_mesh,
    ]

    for builder in builders:
        spec, sm_path, col_path, lod_path = builder()
        assert spec.is_valid_mesh is True
        assert sm_path.startswith("/Game/Geometry/Meshes/")
        assert col_path.startswith("/Game/Geometry/Meshes/")
        assert lod_path.startswith("/Game/Geometry/Meshes/")


def test_universal_geometry_package_validation_and_serialization():
    spec, sm_path, col_path, lod_path = UniversalGeometryFabricationPlatform.build_golden_prop("Mesh_PkgProp53")

    report = UniversalGeometryValidator.validate_universal_geometry(spec, sm_path, col_path, lod_path)
    assert report.is_valid is True
    assert report.review_status == "PASSED"
    assert report.quality_score.aggregate_score >= 0.85

    pkg = UniversalGeometryPackage(
        mesh_id="Mesh_PkgProp53",
        spec=spec,
        static_mesh_path=sm_path,
        collision_mesh_path=col_path,
        lod_mesh_path=lod_path,
        validation_report=report,
    )

    assert len(pkg.package_hash) == 64
    data = pkg.to_dict()
    assert data["mesh_id"] == "Mesh_PkgProp53"
    assert data["spec"]["category"] == "PROP"
    assert data["validation_report"]["review_status"] == "PASSED"
