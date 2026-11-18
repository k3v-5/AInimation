"""
Tests for Lighting & VFX Fabricator, Validator, and Package.
UAF-81.25 Sections 148, 149, 150, 151, 152, 153, 157.
"""

from uaf.lighting_vfx.engine.presentation_fabricator import LightingVFXFabricationPlatform
from uaf.lighting_vfx.validation.presentation_validator import LightingVFXValidator
from uaf.lighting_vfx.package.presentation_package import LightingVFXPackage


def test_lighting_vfx_fabrication_all_six_golden_scenes():
    builders = [
        LightingVFXFabricationPlatform.build_empty_world_presentation,
        LightingVFXFabricationPlatform.build_full_scifi_scene_presentation,
        LightingVFXFabricationPlatform.build_night_scene_presentation,
        LightingVFXFabricationPlatform.build_storm_scene_presentation,
        LightingVFXFabricationPlatform.build_combat_scene_presentation,
        LightingVFXFabricationPlatform.build_cinematic_scene_presentation,
    ]

    for builder in builders:
        p_def, pp_ref = builder()
        assert len(p_def.lights) >= 1
        assert pp_ref.startswith("PP_")


def test_lighting_vfx_package_validation_and_serialization():
    p_def, pp_ref = LightingVFXFabricationPlatform.build_full_scifi_scene_presentation("Pres_PkgSciFi")

    report = LightingVFXValidator.validate_presentation(p_def, pp_ref)
    assert report.is_valid is True
    assert report.review_status == "PASSED"
    assert report.quality_score.aggregate_score >= 0.85

    pkg = LightingVFXPackage(
        asset_id="Pres_PkgSciFi",
        presentation_def=p_def,
        post_process_ref=pp_ref,
        validation_report=report,
    )

    assert len(pkg.package_hash) == 64
    data = pkg.to_dict()
    assert data["asset_id"] == "Pres_PkgSciFi"
    assert len(data["presentation_def"]["lights"]) >= 3
    assert data["validation_report"]["review_status"] == "PASSED"
