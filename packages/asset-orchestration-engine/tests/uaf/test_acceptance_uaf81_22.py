"""
UAF-81.22 Acceptance Tests (Sections 157, 148, 151, 156).
Verifies:
- Section 157: Final Acceptance Criteria (Generates and validates all 15 required surface types:
  painted metal with wear, corroded metal, fabric, leather, skin, concrete, wood, glass, emissive,
  procedural tileable, trim sheet, atlas, decal set, multilayer composite, highpoly baked).
- Sections 148, 151: Non-Negotiable Requirements Test (Zero tolerance for sRGB data channels on Normal/ORM,
  non-power-of-two resolutions, or absolute machine-dependent paths; violations strictly flag MANUAL_REVIEW_REQUIRED).
"""

from uaf.surface_detail.engine.detail_fabricator import SurfaceDetailFabricationPlatform
from uaf.surface_detail.validation.detail_validator import SurfaceDetailValidator
from uaf.surface_detail.models.definition import SurfaceDetailDefinition, PhysicalMaterialClass
from uaf.surface_detail.models.textures import SurfaceDetailChannel
from uaf.surface_detail.package.detail_package import SurfaceDetailPackage


def test_final_surface_detail_acceptance_section_157():
    """
    Acceptance Test Section 157:
    Synthesizes and validates all 15 required surface types.
    """
    builders = [
        ("Surf_Gold_PaintedMetal", SurfaceDetailFabricationPlatform.build_painted_metal_with_wear),
        ("Surf_Gold_CorrodedMetal", SurfaceDetailFabricationPlatform.build_corroded_metal),
        ("Surf_Gold_Fabric", SurfaceDetailFabricationPlatform.build_fabric_material),
        ("Surf_Gold_Leather", SurfaceDetailFabricationPlatform.build_leather_material),
        ("Surf_Gold_Skin", SurfaceDetailFabricationPlatform.build_skin_material),
        ("Surf_Gold_Concrete", SurfaceDetailFabricationPlatform.build_concrete_material),
        ("Surf_Gold_Wood", SurfaceDetailFabricationPlatform.build_wood_material),
        ("Surf_Gold_Glass", SurfaceDetailFabricationPlatform.build_glass_material),
        ("Surf_Gold_Emissive", SurfaceDetailFabricationPlatform.build_emissive_material),
        ("Surf_Gold_Tileable", SurfaceDetailFabricationPlatform.build_procedural_tileable_material),
        ("Surf_Gold_TrimSheet", SurfaceDetailFabricationPlatform.build_trim_sheet_material),
        ("Surf_Gold_Atlas", SurfaceDetailFabricationPlatform.build_texture_atlas_material),
        ("Surf_Gold_Decal", SurfaceDetailFabricationPlatform.build_decal_set_material),
        ("Surf_Gold_Multilayer", SurfaceDetailFabricationPlatform.build_multilayer_composite_material),
        ("Surf_Gold_HighPoly", SurfaceDetailFabricationPlatform.build_highpoly_baked_material),
    ]

    for asset_id, builder_fn in builders:
        s_def, textures, master_id, inst_id = builder_fn(asset_id)
        assert len(textures) >= 3

        report = SurfaceDetailValidator.validate_surface(s_def, textures, master_id, inst_id)
        assert report.is_valid is True, f"Failed for {asset_id}: {report.issues}"
        assert report.review_status == "PASSED"
        assert report.quality_score.aggregate_score >= 0.85

        pkg = SurfaceDetailPackage(
            asset_id=asset_id,
            surface_def=s_def,
            textures=textures,
            master_material_id=master_id,
            material_instance_id=inst_id,
            validation_report=report,
        )
        assert len(pkg.package_hash) == 64
        assert pkg.to_dict()["asset_id"] == asset_id


def test_non_negotiable_requirements_section_148_151():
    """
    Acceptance Test Sections 148, 151:
    Non-negotiable requirements:
    1. Section 148: Data map (NORMAL, ORM) with sRGB strictly fails.
    2. Section 148: Non-power-of-two texture resolution strictly fails.
    3. Section 151: Absolute machine-dependent material reference path strictly fails.
    Any violation strictly triggers review_status = MANUAL_REVIEW_REQUIRED.
    """
    s_def, textures, master_id, inst_id = SurfaceDetailFabricationPlatform.build_painted_metal_with_wear("Surf_Fault_Test")

    # 1. Section 148 violation: NORMAL map set to sRGB
    bad_textures_srgb = [
        SurfaceDetailChannel("T_Albedo", "ALBEDO", "sRGB", 2048),
        SurfaceDetailChannel("T_Normal", "NORMAL", "sRGB", 2048),  # VIOLATION: must be LINEAR!
        SurfaceDetailChannel("T_ORM", "ORM", "LINEAR", 2048),
    ]
    rep_srgb = SurfaceDetailValidator.validate_surface(s_def, bad_textures_srgb, master_id, inst_id)
    assert rep_srgb.is_valid is False
    assert rep_srgb.review_status == "MANUAL_REVIEW_REQUIRED"
    assert any("must be LINEAR" in iss for iss in rep_srgb.issues)

    # 2. Section 148 violation: Non-power-of-two resolution (e.g. 1920)
    bad_textures_npot = [
        SurfaceDetailChannel("T_Albedo", "ALBEDO", "sRGB", 1920),  # VIOLATION: NPOT!
        SurfaceDetailChannel("T_Normal", "NORMAL", "LINEAR", 1920),
        SurfaceDetailChannel("T_ORM", "ORM", "LINEAR", 1920),
    ]
    rep_npot = SurfaceDetailValidator.validate_surface(s_def, bad_textures_npot, master_id, inst_id)
    assert rep_npot.is_valid is False
    assert rep_npot.review_status == "MANUAL_REVIEW_REQUIRED"
    assert any("not a power of two" in iss for iss in rep_npot.issues)

    # 3. Section 151 violation: Absolute machine path in material instance ID
    bad_mat_path = "D:\\UnrealEngine\\Content\\Materials\\MI_Fault.uasset"
    rep_path = SurfaceDetailValidator.validate_surface(s_def, textures, master_id, bad_mat_path)
    assert rep_path.is_valid is False
    assert rep_path.review_status == "MANUAL_REVIEW_REQUIRED"
    assert any("machine-dependent path detected" in iss for iss in rep_path.issues)
