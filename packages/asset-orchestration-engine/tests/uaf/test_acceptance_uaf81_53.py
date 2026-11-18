"""
UAF-81.53 Acceptance Tests (Sections 164, 142, 162, 165, 138, 167).
Verifies:
- Section 164: Final Acceptance Criteria (Generates and validates all 10 Golden Meshes:
  Character, Robot, Creature, Weapon, Prop, Architecture, Rock, Tree, Modular Kit, Complex Mesh).
- Sections 142, 162, 165: Hard Fail Conditions Test (Zero tolerance for non-positive dimensions,
  vertex count < 3, triangle count < 1, missing normals, tangents, UVs, collision, or LODs, or absolute machine-dependent paths;
  violations strictly flag MANUAL_REVIEW_REQUIRED).
"""

from uaf.universal_geometry.engine.universal_geometry_fabricator import UniversalGeometryFabricationPlatform
from uaf.universal_geometry.validation.universal_geometry_validator import UniversalGeometryValidator
from uaf.universal_geometry.models.definition import (
    UniversalMeshSpecification,
    MeshCategory53,
    TopologyType53,
    MeshDimensions53,
)
from uaf.universal_geometry.package.universal_geometry_package import UniversalGeometryPackage


def test_final_universal_geometry_acceptance_section_164():
    """
    Acceptance Test Section 164:
    Synthesizes and validates all 10 Golden Meshes.
    """
    builders = [
        ("Mesh_Gold_Char53", UniversalGeometryFabricationPlatform.build_golden_character),
        ("Mesh_Gold_Robot53", UniversalGeometryFabricationPlatform.build_golden_robot),
        ("Mesh_Gold_Creature53", UniversalGeometryFabricationPlatform.build_golden_creature),
        ("Mesh_Gold_Weapon53", UniversalGeometryFabricationPlatform.build_golden_weapon),
        ("Mesh_Gold_Prop53", UniversalGeometryFabricationPlatform.build_golden_prop),
        ("Mesh_Gold_Arch53", UniversalGeometryFabricationPlatform.build_golden_architecture),
        ("Mesh_Gold_Rock53", UniversalGeometryFabricationPlatform.build_golden_rock),
        ("Mesh_Gold_Tree53", UniversalGeometryFabricationPlatform.build_golden_tree),
        ("Mesh_Gold_ModKit53", UniversalGeometryFabricationPlatform.build_golden_modular_kit),
        ("Mesh_Gold_Complex53", UniversalGeometryFabricationPlatform.build_golden_complex_mesh),
    ]

    for mesh_id, builder_fn in builders:
        spec, sm_path, col_path, lod_path = builder_fn(mesh_id)
        assert spec.is_valid_mesh is True

        report = UniversalGeometryValidator.validate_universal_geometry(spec, sm_path, col_path, lod_path)
        assert report.is_valid is True, f"Failed for {mesh_id}: {report.issues}"
        assert report.review_status == "PASSED"
        assert report.quality_score.aggregate_score >= 0.85

        pkg = UniversalGeometryPackage(
            mesh_id=mesh_id,
            spec=spec,
            static_mesh_path=sm_path,
            collision_mesh_path=col_path,
            lod_mesh_path=lod_path,
            validation_report=report,
        )
        assert len(pkg.package_hash) == 64
        assert pkg.to_dict()["mesh_id"] == mesh_id


def test_hard_fail_conditions_section_142_162_165():
    """
    Acceptance Test Sections 142, 162, 165:
    Hard fail conditions:
    1. INVALID_MESH_DIMENSIONS: Non-positive width, length, or height.
    2. INVALID_TOPOLOGY_COUNTS: vertex_count < 3 or triangle_count < 1.
    3. MISSING_CORE_SUBSYSTEMS: Missing normals, tangents, UVs, collision, or LODs.
    4. Path purity: Absolute machine-dependent reference paths.
    Any violation strictly triggers review_status = MANUAL_REVIEW_REQUIRED.
    """
    spec, sm_path, col_path, lod_path = UniversalGeometryFabricationPlatform.build_golden_prop("Mesh_Fault_Test")

    # 1. Non-positive dimensions: height = 0.0
    bad_dims = MeshDimensions53(width_cm=100.0, length_cm=100.0, height_cm=0.0)
    bad_spec_dims = UniversalMeshSpecification(
        "Mesh_ZeroHeight",
        MeshCategory53.PROP,
        dimensions=bad_dims,
    )
    rep_dims = UniversalGeometryValidator.validate_universal_geometry(bad_spec_dims, sm_path, col_path, lod_path)
    assert rep_dims.is_valid is False
    assert rep_dims.review_status == "MANUAL_REVIEW_REQUIRED"
    assert any("INVALID_MESH_DIMENSIONS" in iss for iss in rep_dims.issues)

    # 2. Topology counts: vertex_count = 2 (< 3)
    bad_spec_top = UniversalMeshSpecification(
        "Mesh_FewVertices",
        MeshCategory53.PROP,
        vertex_count=2,
        triangle_count=0,
    )
    rep_top = UniversalGeometryValidator.validate_universal_geometry(bad_spec_top, sm_path, col_path, lod_path)
    assert rep_top.is_valid is False
    assert rep_top.review_status == "MANUAL_REVIEW_REQUIRED"
    assert any("INVALID_TOPOLOGY_COUNTS" in iss for iss in rep_top.issues)

    # 3. Missing UVs
    bad_spec_uv = UniversalMeshSpecification(
        "Mesh_NoUV",
        MeshCategory53.PROP,
        has_uv=False,
    )
    rep_uv = UniversalGeometryValidator.validate_universal_geometry(bad_spec_uv, sm_path, col_path, lod_path)
    assert rep_uv.is_valid is False
    assert rep_uv.review_status == "MANUAL_REVIEW_REQUIRED"
    assert any("MISSING_CORE_SUBSYSTEMS" in iss for iss in rep_uv.issues)

    # 4. Path purity violation: Absolute machine path
    bad_sm_path = "D:\\UnrealProjects\\Meshes\\SM_Crate.uasset"
    rep_path = UniversalGeometryValidator.validate_universal_geometry(spec, bad_sm_path, col_path, lod_path)
    assert rep_path.is_valid is False
    assert rep_path.review_status == "MANUAL_REVIEW_REQUIRED"
    assert any("Absolute machine-dependent path" in iss for iss in rep_path.issues)
