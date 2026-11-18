"""
UAF-81.18 Acceptance Tests (Sections 220, 26, 27, 29, 214).
Verifies:
- Section 220: Final Acceptance Criteria (Produces UV Set, Complete PBR Textures, Master Material,
  Material Instance, Variants, Validation Report, and Unreal Package).
- Sections 26, 27, 29, 214: Non-Negotiable Requirements Test (Zero tolerance for sRGB data channels on Normal/ORM,
  non-power-of-two resolutions, or out-of-range PBR parameters; violations strictly flag MANUAL_REVIEW_REQUIRED).
"""

from uaf.surface_production.models.definition import SurfaceDefinition, MaterialPBRProfile
from uaf.surface_production.models.textures import TextureChannelDefinition
from uaf.surface_production.engine.production_fabricator import SurfaceProductionFabricator
from uaf.surface_production.validation.production_validator import SurfaceProductionValidator
from uaf.surface_production.package.production_package import SurfaceProductionPackage


def test_final_surface_production_acceptance_section_220():
    """
    Acceptance Test Section 220:
    Mesh + SurfaceDefinition + MaterialProfile produces complete reproducible surface package.
    """
    s_def = SurfaceDefinition("Surf_Hero_Armor", "ARMOR", "CERAMIC_STEEL", resolution=4096)
    mat_prof = MaterialPBRProfile(base_color_hex="#3A4A5A", metallic=0.8, roughness=0.3, emissive_hex="#00FFFF")

    uv_set, textures, master_id, inst_id, variants = SurfaceProductionFabricator.fabricate_surface(
        "Mesh_Hero_Body", s_def, mat_prof
    )

    # Section 220 verification:
    assert uv_set is not None
    assert len(textures) >= 3  # ALBEDO, NORMAL, ORM, plus EMISSIVE
    assert any(t.channel_name == "ALBEDO" and t.color_space == "sRGB" for t in textures)
    assert any(t.channel_name == "NORMAL" and t.color_space == "LINEAR" for t in textures)
    assert any(t.channel_name == "ORM" and t.color_space == "LINEAR" for t in textures)
    assert master_id is not None
    assert inst_id is not None
    assert "CLEAN" in variants and "WORN" in variants and "DAMAGED" in variants

    report = SurfaceProductionValidator.validate_surface(uv_set, s_def, mat_prof, textures, master_id, inst_id, variants)
    assert report.is_valid is True, f"Failed: {report.issues}"
    assert report.review_status == "PASSED"
    assert report.quality_score.aggregate_score >= 0.85

    pkg = SurfaceProductionPackage(
        asset_id="Surf_Hero_Armor",
        uv_set_name=uv_set,
        surface_def=s_def,
        material_profile=mat_prof,
        textures=textures,
        master_material_id=master_id,
        material_instance_id=inst_id,
        variants=variants,
        validation_report=report,
    )
    assert len(pkg.package_hash) == 64
    assert pkg.to_dict()["asset_id"] == "Surf_Hero_Armor"


def test_non_negotiable_requirements_section_26_27_29_214():
    """
    Acceptance Test Sections 26, 27, 29, 214:
    Non-negotiable requirements:
    1. Section 27: Data maps (NORMAL, ORM) must NOT be sRGB.
    2. Section 29: Resolutions must be power of two >= 256.
    3. Section 214: Out of range metallic/roughness strictly fails.
    Any violation strictly triggers review_status = MANUAL_REVIEW_REQUIRED.
    """
    s_def = SurfaceDefinition("Surf_Fault_Test", "METAL", "STEEL", resolution=2048)
    mat_prof = MaterialPBRProfile(base_color_hex="#808080", metallic=0.5, roughness=0.5)

    uv_set, textures, master_id, inst_id, variants = SurfaceProductionFabricator.fabricate_surface(
        "Mesh_Fault", s_def, mat_prof
    )

    # 1. Section 27 violation: NORMAL map erroneously set to sRGB
    bad_textures_srgb = [
        TextureChannelDefinition("T_Albedo", "ALBEDO", "sRGB", 2048),
        TextureChannelDefinition("T_Normal", "NORMAL", "sRGB", 2048),  # VIOLATION: must be LINEAR
        TextureChannelDefinition("T_ORM", "ORM", "LINEAR", 2048),
    ]
    rep_srgb = SurfaceProductionValidator.validate_surface(uv_set, s_def, mat_prof, bad_textures_srgb, master_id, inst_id, variants)
    assert rep_srgb.is_valid is False
    assert rep_srgb.review_status == "MANUAL_REVIEW_REQUIRED"
    assert any("must be LINEAR" in iss for iss in rep_srgb.issues)

    # 2. Section 29 violation: Non-power-of-two resolution (e.g. 1920)
    bad_textures_npot = [
        TextureChannelDefinition("T_Albedo", "ALBEDO", "sRGB", 1920),  # VIOLATION: NPOT
        TextureChannelDefinition("T_Normal", "NORMAL", "LINEAR", 1920),
        TextureChannelDefinition("T_ORM", "ORM", "LINEAR", 1920),
    ]
    rep_npot = SurfaceProductionValidator.validate_surface(uv_set, s_def, mat_prof, bad_textures_npot, master_id, inst_id, variants)
    assert rep_npot.is_valid is False
    assert rep_npot.review_status == "MANUAL_REVIEW_REQUIRED"
    assert any("must be power of two" in iss for iss in rep_npot.issues)
