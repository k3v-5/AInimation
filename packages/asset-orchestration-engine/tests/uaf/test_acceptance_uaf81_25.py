"""
UAF-81.25 Acceptance Tests (Sections 148 to 153, 6, 17, 139, 160).
Verifies:
- Sections 148 to 153: Final Acceptance Criteria (Generates and validates all 6 golden presentation scenes:
  Empty World, Full Sci-Fi, Night Scene, Storm, Combat, Cinematic).
- Sections 6, 17, 139, 160: Non-Negotiable Requirements Test (Zero tolerance for negative light intensity,
  particle overflow, or absolute machine-dependent paths; violations strictly flag MANUAL_REVIEW_REQUIRED).
"""

from uaf.lighting_vfx.engine.presentation_fabricator import LightingVFXFabricationPlatform
from uaf.lighting_vfx.validation.presentation_validator import LightingVFXValidator
from uaf.lighting_vfx.models.lighting import LightSourceDefinition, LightType25, LightMobility, LightRole
from uaf.lighting_vfx.models.vfx import VFXEffectDefinition, VFXEffectType
from uaf.lighting_vfx.models.presentation import PresentationDefinition25
from uaf.lighting_vfx.package.presentation_package import LightingVFXPackage


def test_final_lighting_vfx_acceptance_sections_148_to_153():
    """
    Acceptance Test Sections 148 to 153:
    Synthesizes and validates all 6 golden presentation scenes.
    """
    builders = [
        ("Pres_Gold_EmptyWorld", LightingVFXFabricationPlatform.build_empty_world_presentation),
        ("Pres_Gold_FullSciFi", LightingVFXFabricationPlatform.build_full_scifi_scene_presentation),
        ("Pres_Gold_NightCity", LightingVFXFabricationPlatform.build_night_scene_presentation),
        ("Pres_Gold_Storm", LightingVFXFabricationPlatform.build_storm_scene_presentation),
        ("Pres_Gold_Combat", LightingVFXFabricationPlatform.build_combat_scene_presentation),
        ("Pres_Gold_Cinematic", LightingVFXFabricationPlatform.build_cinematic_scene_presentation),
    ]

    for asset_id, builder_fn in builders:
        p_def, pp_ref = builder_fn(asset_id)
        assert len(p_def.lights) >= 1

        report = LightingVFXValidator.validate_presentation(p_def, pp_ref)
        assert report.is_valid is True, f"Failed for {asset_id}: {report.issues}"
        assert report.review_status == "PASSED"
        assert report.quality_score.aggregate_score >= 0.85

        pkg = LightingVFXPackage(
            asset_id=asset_id,
            presentation_def=p_def,
            post_process_ref=pp_ref,
            validation_report=report,
        )
        assert len(pkg.package_hash) == 64
        assert pkg.to_dict()["asset_id"] == asset_id


def test_non_negotiable_requirements_section_6_139_160():
    """
    Acceptance Test Sections 6, 139, 160:
    Non-negotiable requirements:
    1. Section 6: Light with negative intensity strictly fails.
    2. Section 160: VFX system exceeding particle budget strictly fails.
    3. Section 139: Absolute machine-dependent reference paths strictly fails.
    Any violation strictly triggers review_status = MANUAL_REVIEW_REQUIRED.
    """
    p_def, pp_ref = LightingVFXFabricationPlatform.build_empty_world_presentation("Pres_Fault_Test")

    # 1. Section 6 violation: Negative light intensity
    bad_light = LightSourceDefinition("L_Neg_Int", LightType25.POINT, LightMobility.MOVABLE, LightRole.KEY, intensity_lux=-500.0)
    bad_pdef_light = PresentationDefinition25("Pres_NegLight", p_def.sky_atmosphere, [bad_light], [])
    rep_light = LightingVFXValidator.validate_presentation(bad_pdef_light, pp_ref)
    assert rep_light.is_valid is False
    assert rep_light.review_status == "MANUAL_REVIEW_REQUIRED"
    assert any("negative intensity" in iss for iss in rep_light.issues)

    # 2. Section 160 violation: VFX particle budget overflow (>50,000)
    bad_vfx = VFXEffectDefinition("VFX_Overbudget", VFXEffectType.NIAGARA_PARTICLE, max_particles=100000)
    bad_pdef_vfx = PresentationDefinition25("Pres_OverVFX", p_def.sky_atmosphere, p_def.lights, [bad_vfx])
    rep_vfx = LightingVFXValidator.validate_presentation(bad_pdef_vfx, pp_ref)
    assert rep_vfx.is_valid is False
    assert rep_vfx.review_status == "MANUAL_REVIEW_REQUIRED"
    assert any("exceeds particle budget" in iss for iss in rep_vfx.issues)

    # 3. Section 139 violation: Absolute machine path in post-process reference
    bad_pp_path = "E:\\UnrealProjects\\Shaders\\PostProcess\\PP_Grade.uasset"
    rep_pp = LightingVFXValidator.validate_presentation(p_def, bad_pp_path)
    assert rep_pp.is_valid is False
    assert rep_pp.review_status == "MANUAL_REVIEW_REQUIRED"
    assert any("Absolute machine-dependent path" in iss for iss in rep_pp.issues)
