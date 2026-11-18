"""
UAF-81.46 Acceptance Tests (Sections 114, 99, 100, 101, 112, 120, 121, 122, 124, 125).
Verifies:
- Section 114: Final Acceptance Criteria (Generates and validates all 7 Golden Surfaces:
  Skin, Metal, Fabric, Wood, Concrete, Glass, Organic).
- Sections 99, 100, 101, 112, 121, 122, 124: Hard Fail Conditions Test (Zero tolerance for invalid PBR ranges,
  non-POT or < 256 resolutions, missing normal/displacement maps, or absolute machine-dependent paths;
  violations strictly flag MANUAL_REVIEW_REQUIRED).
"""

from uaf.lookdev_surface.engine.lookdev_surface_fabricator import LookdevSurfaceFabricationPlatform
from uaf.lookdev_surface.validation.lookdev_surface_validator import LookdevSurfaceValidator
from uaf.lookdev_surface.models.definition import (
    LookdevSurfaceSpecification,
    MaterialFamily46,
    SurfacePBRProperties46,
)
from uaf.lookdev_surface.package.lookdev_surface_package import LookdevSurfacePackage


def test_final_lookdev_surface_acceptance_section_114():
    """
    Acceptance Test Section 114:
    Synthesizes and validates all 7 Golden Surfaces.
    """
    builders = [
        ("Surf_Gold_Skin", LookdevSurfaceFabricationPlatform.build_golden_skin),
        ("Surf_Gold_Metal", LookdevSurfaceFabricationPlatform.build_golden_metal),
        ("Surf_Gold_Fabric", LookdevSurfaceFabricationPlatform.build_golden_fabric),
        ("Surf_Gold_Wood", LookdevSurfaceFabricationPlatform.build_golden_wood),
        ("Surf_Gold_Concrete", LookdevSurfaceFabricationPlatform.build_golden_concrete),
        ("Surf_Gold_Glass", LookdevSurfaceFabricationPlatform.build_golden_glass),
        ("Surf_Gold_Organic", LookdevSurfaceFabricationPlatform.build_golden_organic),
    ]

    for surf_id, builder_fn in builders:
        spec, m_path, mi_path, t_path = builder_fn(surf_id)
        assert spec.is_valid_surface is True

        report = LookdevSurfaceValidator.validate_lookdev_surface(spec, m_path, mi_path, t_path)
        assert report.is_valid is True, f"Failed for {surf_id}: {report.issues}"
        assert report.review_status == "PASSED"
        assert report.quality_score.aggregate_score >= 0.85

        pkg = LookdevSurfacePackage(
            surface_id=surf_id,
            spec=spec,
            master_material_path=m_path,
            material_instance_path=mi_path,
            texture_set_path=t_path,
            validation_report=report,
        )
        assert len(pkg.package_hash) == 64
        assert pkg.to_dict()["surface_id"] == surf_id


def test_hard_fail_conditions_section_99_100_101_112_121_122_124():
    """
    Acceptance Test Sections 99, 100, 101, 112, 121, 122, 124:
    Hard fail conditions:
    1. INVALID_PBR_RANGE: Metallic, roughness, or ao outside [0, 1], emission < 0, RGB out of range.
    2. INVALID_RESOLUTION: Non-POT or < 256.
    3. MISSING_CORE_MAPS: has_normal or has_displacement is False.
    4. Path purity: Absolute machine-dependent reference paths.
    Any violation strictly triggers review_status = MANUAL_REVIEW_REQUIRED.
    """
    spec, m_path, mi_path, t_path = LookdevSurfaceFabricationPlatform.build_golden_metal("Surf_Fault_Test")

    # 1. PBR range violation: metallic = 1.8
    bad_pbr = SurfacePBRProperties46(metallic=1.8, roughness=0.5, ao=1.0, emission=0.0, resolution=2048)
    bad_spec_pbr = LookdevSurfaceSpecification(
        "Surf_BadMetallic",
        MaterialFamily46.METAL,
        pbr=bad_pbr,
    )
    rep_pbr = LookdevSurfaceValidator.validate_lookdev_surface(bad_spec_pbr, m_path, mi_path, t_path)
    assert rep_pbr.is_valid is False
    assert rep_pbr.review_status == "MANUAL_REVIEW_REQUIRED"
    assert any("INVALID_PBR_RANGE" in iss for iss in rep_pbr.issues)

    # 2. Resolution violation: 500 (not power of two)
    bad_res = SurfacePBRProperties46(resolution=500)
    bad_spec_res = LookdevSurfaceSpecification(
        "Surf_BadRes",
        MaterialFamily46.METAL,
        pbr=bad_res,
    )
    rep_res = LookdevSurfaceValidator.validate_lookdev_surface(bad_spec_res, m_path, mi_path, t_path)
    assert rep_res.is_valid is False
    assert rep_res.review_status == "MANUAL_REVIEW_REQUIRED"
    assert any("INVALID_RESOLUTION" in iss for iss in rep_res.issues)

    # 3. Missing normal map
    bad_spec_norm = LookdevSurfaceSpecification(
        "Surf_NoNorm",
        MaterialFamily46.METAL,
        has_normal=False,
    )
    rep_norm = LookdevSurfaceValidator.validate_lookdev_surface(bad_spec_norm, m_path, mi_path, t_path)
    assert rep_norm.is_valid is False
    assert rep_norm.review_status == "MANUAL_REVIEW_REQUIRED"
    assert any("MISSING_CORE_MAPS" in iss for iss in rep_norm.issues)

    # 4. Path purity violation: Absolute machine path
    bad_mat_path = "D:\\UnrealProjects\\Materials\\M_Metal.uasset"
    rep_path = LookdevSurfaceValidator.validate_lookdev_surface(spec, bad_mat_path, mi_path, t_path)
    assert rep_path.is_valid is False
    assert rep_path.review_status == "MANUAL_REVIEW_REQUIRED"
    assert any("Absolute machine-dependent path" in iss for iss in rep_path.issues)
