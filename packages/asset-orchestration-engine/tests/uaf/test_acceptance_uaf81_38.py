"""
UAF-81.38 Acceptance Tests (Sections 147, 145, 6, 7, 11, 12, 143, 149).
Verifies:
- Section 147: Final Acceptance Criteria (Generates and validates all 14 Golden Surfaces:
  Skin, Metal, Fabric, Leather, Concrete, Rock, Wood, Glass, Plastic, Energy, Robot Surface, Armor Surface, Weapon Surface, Environment Surface).
- Section 145: Hard Fail Conditions Test (Zero tolerance for out-of-range PBR parameters,
  non-POT/low resolutions, or absolute machine-dependent paths; violations strictly flag MANUAL_REVIEW_REQUIRED).
"""

from uaf.surface_lookdev.engine.surface_lookdev_fabricator import SurfaceLookdevFabricationPlatform
from uaf.surface_lookdev.validation.surface_lookdev_validator import SurfaceLookdevValidator
from uaf.surface_lookdev.models.definition import (
    SurfaceLookdevSpecification,
    MaterialType38,
    PBRSurfaceProperties38,
)
from uaf.surface_lookdev.package.surface_lookdev_package import SurfaceLookdevPackage


def test_final_surface_lookdev_acceptance_section_147():
    """
    Acceptance Test Section 147:
    Synthesizes and validates all 14 Golden Surfaces.
    """
    builders = [
        ("Lookdev_Gold_Skin", SurfaceLookdevFabricationPlatform.build_golden_skin),
        ("Lookdev_Gold_Metal", SurfaceLookdevFabricationPlatform.build_golden_metal),
        ("Lookdev_Gold_Fabric", SurfaceLookdevFabricationPlatform.build_golden_fabric),
        ("Lookdev_Gold_Leather", SurfaceLookdevFabricationPlatform.build_golden_leather),
        ("Lookdev_Gold_Concrete", SurfaceLookdevFabricationPlatform.build_golden_concrete),
        ("Lookdev_Gold_Rock", SurfaceLookdevFabricationPlatform.build_golden_rock),
        ("Lookdev_Gold_Wood", SurfaceLookdevFabricationPlatform.build_golden_wood),
        ("Lookdev_Gold_Glass", SurfaceLookdevFabricationPlatform.build_golden_glass),
        ("Lookdev_Gold_Plastic", SurfaceLookdevFabricationPlatform.build_golden_plastic),
        ("Lookdev_Gold_Energy", SurfaceLookdevFabricationPlatform.build_golden_energy),
        ("Lookdev_Gold_RobotSurface", SurfaceLookdevFabricationPlatform.build_golden_robot_surface),
        ("Lookdev_Gold_ArmorSurface", SurfaceLookdevFabricationPlatform.build_golden_armor_surface),
        ("Lookdev_Gold_WeaponSurface", SurfaceLookdevFabricationPlatform.build_golden_weapon_surface),
        ("Lookdev_Gold_EnvSurface", SurfaceLookdevFabricationPlatform.build_golden_environment_surface),
    ]

    for surf_id, builder_fn in builders:
        spec, master_path, inst_path = builder_fn(surf_id)
        assert spec.properties.is_valid is True

        report = SurfaceLookdevValidator.validate_surface_lookdev(spec, master_path, inst_path)
        assert report.is_valid is True, f"Failed for {surf_id}: {report.issues}"
        assert report.review_status == "PASSED"
        assert report.quality_score.aggregate_score >= 0.85

        pkg = SurfaceLookdevPackage(
            surface_id=surf_id,
            spec=spec,
            master_material_path=master_path,
            material_instance_path=inst_path,
            validation_report=report,
        )
        assert len(pkg.package_hash) == 64
        assert pkg.to_dict()["surface_id"] == surf_id


def test_hard_fail_conditions_section_145():
    """
    Acceptance Test Section 145:
    Hard fail conditions:
    1. INVALID_PBR_RANGE: Roughness, metallic, or specular outside [0.0, 1.0].
    2. INVALID_RESOLUTION: Non-POT resolution or resolution < 256.
    3. Path purity: Absolute machine-dependent reference paths.
    Any violation strictly triggers review_status = MANUAL_REVIEW_REQUIRED.
    """
    spec, master_path, inst_path = SurfaceLookdevFabricationPlatform.build_golden_metal("Lookdev_Fault_Test")

    # 1. PBR boundary violation: Roughness 1.35 (> 1.0)
    bad_props = PBRSurfaceProperties38(roughness=1.35)
    bad_spec_props = SurfaceLookdevSpecification(
        "Surf_RoughFail",
        MaterialType38.METAL,
        properties=bad_props,
    )
    rep_props = SurfaceLookdevValidator.validate_surface_lookdev(bad_spec_props, master_path, inst_path)
    assert rep_props.is_valid is False
    assert rep_props.review_status == "MANUAL_REVIEW_REQUIRED"
    assert any("INVALID_PBR_RANGE" in iss for iss in rep_props.issues)

    # 2. Resolution violation: NPOT 1000x1000
    bad_spec_res = SurfaceLookdevSpecification(
        "Surf_ResFail",
        MaterialType38.METAL,
        resolution_width=1000,
        resolution_height=1000,
    )
    rep_res = SurfaceLookdevValidator.validate_surface_lookdev(bad_spec_res, master_path, inst_path)
    assert rep_res.is_valid is False
    assert rep_res.review_status == "MANUAL_REVIEW_REQUIRED"
    assert any("INVALID_RESOLUTION" in iss for iss in rep_res.issues)

    # 3. Path purity violation: Absolute machine path
    bad_inst_path = "D:\\UnrealProjects\\Materials\\MI_Metal.uasset"
    rep_path = SurfaceLookdevValidator.validate_surface_lookdev(spec, master_path, bad_inst_path)
    assert rep_path.is_valid is False
    assert rep_path.review_status == "MANUAL_REVIEW_REQUIRED"
    assert any("Absolute machine-dependent path" in iss for iss in rep_path.issues)
