"""
UAF-81.27 Acceptance Tests (Sections 130 to 133, 15, 19, 119, 120, 129).
Verifies:
- Sections 130 to 133: Final Acceptance Criteria (Generates and validates all 4 canonical scenarios:
  Character Surface, Weapon Surface, Environment Surface, Modular Kit Surface).
- Sections 15, 19, 119, 120, 129: Non-Negotiable Requirements Test (Zero tolerance for data maps with sRGB,
  non-power-of-two resolutions, or absolute machine-dependent paths; violations strictly flag MANUAL_REVIEW_REQUIRED).
"""

from uaf.surface_pipeline.engine.pipeline_fabricator import SurfacePipelineFabricationPlatform
from uaf.surface_pipeline.validation.pipeline_validator import SurfacePipelineValidator
from uaf.surface_pipeline.models.definition import (
    SurfaceDefinition27,
    SurfaceClass27,
    UVStrategyType,
    TextureMapDefinition,
    ColorSpace27,
)
from uaf.surface_pipeline.package.pipeline_package import SurfacePipelinePackage


def test_final_surface_pipeline_acceptance_sections_130_to_133():
    """
    Acceptance Test Sections 130 to 133:
    Synthesizes and validates all 4 canonical scenarios.
    """
    builders = [
        ("Surf_Gold_Character", SurfacePipelineFabricationPlatform.build_character_surface),
        ("Surf_Gold_Weapon", SurfacePipelineFabricationPlatform.build_weapon_surface),
        ("Surf_Gold_Environment", SurfacePipelineFabricationPlatform.build_environment_surface),
        ("Surf_Gold_ModularKit", SurfacePipelineFabricationPlatform.build_modular_kit_surface),
    ]

    for asset_id, builder_fn in builders:
        s_def, master_ref, inst_ref = builder_fn(asset_id)
        assert len(s_def.textures) >= 3

        report = SurfacePipelineValidator.validate_surface(s_def, master_ref, inst_ref)
        assert report.is_valid is True, f"Failed for {asset_id}: {report.issues}"
        assert report.review_status == "PASSED"
        assert report.quality_score.aggregate_score >= 0.85

        pkg = SurfacePipelinePackage(
            asset_id=asset_id,
            surface_def=s_def,
            master_material_ref=master_ref,
            instance_material_ref=inst_ref,
            validation_report=report,
        )
        assert len(pkg.package_hash) == 64
        assert pkg.to_dict()["asset_id"] == asset_id


def test_non_negotiable_requirements_section_15_19_119_120():
    """
    Acceptance Test Sections 15, 19, 119, 120, 129:
    Non-negotiable requirements:
    1. Section 19: Data maps (NORMAL, ORM, MASK) marked sRGB strictly fails.
    2. Section 15: Texture resolution not a power of two >= 256 strictly fails.
    3. Section 119 & 120: Absolute machine-dependent reference paths strictly fails.
    Any violation strictly triggers review_status = MANUAL_REVIEW_REQUIRED.
    """
    s_def, master_ref, inst_ref = SurfacePipelineFabricationPlatform.build_weapon_surface("Surf_Fault_Test")

    # 1. Section 19 violation: Data map with sRGB
    bad_data_map = [
        TextureMapDefinition("T_Albedo", "BASE_COLOR", 2048, ColorSpace27.SRGB),
        TextureMapDefinition("T_Normal", "NORMAL", 2048, ColorSpace27.SRGB),  # VIOLATION: must be LINEAR/NORMAL_MAP!
        TextureMapDefinition("T_ORM", "ORM", 2048, ColorSpace27.LINEAR),
    ]
    bad_sdef_srgb = SurfaceDefinition27(
        "Surf_Fault_SRGB",
        "Asset_Fault",
        SurfaceClass27.METAL,
        textures=bad_data_map,
    )
    rep_srgb = SurfacePipelineValidator.validate_surface(bad_sdef_srgb, master_ref, inst_ref)
    assert rep_srgb.is_valid is False
    assert rep_srgb.review_status == "MANUAL_REVIEW_REQUIRED"
    assert any("must be LINEAR or NORMAL_MAP" in iss for iss in rep_srgb.issues)

    # 2. Section 15 violation: Non-power-of-two resolution (e.g. 1920)
    bad_npot_map = [
        TextureMapDefinition("T_Albedo", "BASE_COLOR", 1920, ColorSpace27.SRGB),  # VIOLATION: NPOT!
        TextureMapDefinition("T_Normal", "NORMAL", 1920, ColorSpace27.NORMAL_MAP),
        TextureMapDefinition("T_ORM", "ORM", 1920, ColorSpace27.LINEAR),
    ]
    bad_sdef_npot = SurfaceDefinition27(
        "Surf_Fault_NPOT",
        "Asset_Fault",
        SurfaceClass27.METAL,
        textures=bad_npot_map,
    )
    rep_npot = SurfacePipelineValidator.validate_surface(bad_sdef_npot, master_ref, inst_ref)
    assert rep_npot.is_valid is False
    assert rep_npot.review_status == "MANUAL_REVIEW_REQUIRED"
    assert any("not a valid power of two" in iss for iss in rep_npot.issues)

    # 3. Section 119 & 120 violation: Absolute machine path in material instance reference
    bad_mat_path = "D:\\UnrealProjects\\Shaders\\Materials\\MI_PBR.uasset"
    rep_path = SurfacePipelineValidator.validate_surface(s_def, master_ref, bad_mat_path)
    assert rep_path.is_valid is False
    assert rep_path.review_status == "MANUAL_REVIEW_REQUIRED"
    assert any("Absolute machine-dependent path" in iss for iss in rep_path.issues)
