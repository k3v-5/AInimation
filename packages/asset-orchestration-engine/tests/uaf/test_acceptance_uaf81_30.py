"""
UAF-81.30 Acceptance Tests (Sections 149, 10, 11, 13, 14, 142).
Verifies:
- Section 149: Final Acceptance Criteria (Generates and validates all 8 Golden Reference Surfaces:
  Golden Skin, Golden Metal, Golden Fabric, Golden Concrete, Golden Wood, Golden Glass, Golden Energy, Golden Terrain).
- Sections 10, 11, 13, 14, 142: Non-Negotiable Requirements Test (Zero tolerance for data maps with sRGB,
  non-power-of-two resolutions, invalid PBR bounds, or absolute machine-dependent paths; violations strictly flag MANUAL_REVIEW_REQUIRED).
"""

from uaf.surface_material.engine.material_fabricator import SurfaceMaterialProductionPlatform
from uaf.surface_material.validation.material_validator import SurfaceMaterialValidator
from uaf.surface_material.models.definition import (
    ProductionSurfaceDefinition,
    SurfaceType30,
    MaterialModel30,
    SurfaceMapItem,
    ColorSpace30,
)
from uaf.surface_material.package.material_package import SurfaceMaterialPackage


def test_final_surface_material_acceptance_section_149():
    """
    Acceptance Test Section 149:
    Synthesizes and validates all 8 Golden Reference Surfaces.
    """
    builders = [
        ("Surf_Gold_Skin", SurfaceMaterialProductionPlatform.build_golden_skin),
        ("Surf_Gold_Metal", SurfaceMaterialProductionPlatform.build_golden_metal),
        ("Surf_Gold_Fabric", SurfaceMaterialProductionPlatform.build_golden_fabric),
        ("Surf_Gold_Concrete", SurfaceMaterialProductionPlatform.build_golden_concrete),
        ("Surf_Gold_Wood", SurfaceMaterialProductionPlatform.build_golden_wood),
        ("Surf_Gold_Glass", SurfaceMaterialProductionPlatform.build_golden_glass),
        ("Surf_Gold_Energy", SurfaceMaterialProductionPlatform.build_golden_energy),
        ("Surf_Gold_Terrain", SurfaceMaterialProductionPlatform.build_golden_terrain),
    ]

    for asset_id, builder_fn in builders:
        s_def, master_ref, inst_ref = builder_fn(asset_id)
        assert s_def.is_valid_pbr is True
        assert len(s_def.maps) >= 3

        report = SurfaceMaterialValidator.validate_surface_production(s_def, master_ref, inst_ref)
        assert report.is_valid is True, f"Failed for {asset_id}: {report.issues}"
        assert report.review_status == "PASSED"
        assert report.quality_score.aggregate_score >= 0.85

        pkg = SurfaceMaterialPackage(
            asset_id=asset_id,
            surface_def=s_def,
            master_material_ref=master_ref,
            instance_material_ref=inst_ref,
            validation_report=report,
        )
        assert len(pkg.package_hash) == 64
        assert pkg.to_dict()["asset_id"] == asset_id


def test_non_negotiable_requirements_section_10_11_13_14_142():
    """
    Acceptance Test Sections 10, 11, 13, 14, 142:
    Non-negotiable requirements:
    1. Section 14 & 142: Data maps (NORMAL, ORM, MASK) marked sRGB strictly fails.
    2. Section 11: Texture resolution not a power of two >= 256 strictly fails.
    3. PBR bounds: Roughness/metallic outside [0.0, 1.0] strictly fails.
    4. Section 142: Absolute machine-dependent reference paths strictly fails.
    Any violation strictly triggers review_status = MANUAL_REVIEW_REQUIRED.
    """
    s_def, master_ref, inst_ref = SurfaceMaterialProductionPlatform.build_golden_metal("Surf_Fault_Test")

    # 1. Section 14 & 142 violation: Data map with sRGB
    bad_maps_srgb = [
        SurfaceMapItem("T_Color", "BASE_COLOR", 2048, ColorSpace30.SRGB),
        SurfaceMapItem("T_Norm", "NORMAL", 2048, ColorSpace30.SRGB),  # VIOLATION: Normal must be LINEAR/NORMAL_MAP
    ]
    bad_sdef_srgb = ProductionSurfaceDefinition(
        "Surf_Bad_SRGB",
        SurfaceType30.METAL,
        MaterialModel30.PBR_METALLIC_ROUGHNESS,
        maps=bad_maps_srgb,
    )
    rep_srgb = SurfaceMaterialValidator.validate_surface_production(bad_sdef_srgb, master_ref, inst_ref)
    assert rep_srgb.is_valid is False
    assert rep_srgb.review_status == "MANUAL_REVIEW_REQUIRED"
    assert any("must be LINEAR or NORMAL_MAP" in iss for iss in rep_srgb.issues)

    # 2. Section 11 violation: Non-power-of-two resolution (e.g. 1920)
    bad_maps_npot = [
        SurfaceMapItem("T_Color", "BASE_COLOR", 1920, ColorSpace30.SRGB),  # VIOLATION: NPOT
    ]
    bad_sdef_npot = ProductionSurfaceDefinition(
        "Surf_Bad_NPOT",
        SurfaceType30.METAL,
        MaterialModel30.PBR_METALLIC_ROUGHNESS,
        maps=bad_maps_npot,
    )
    rep_npot = SurfaceMaterialValidator.validate_surface_production(bad_sdef_npot, master_ref, inst_ref)
    assert rep_npot.is_valid is False
    assert rep_npot.review_status == "MANUAL_REVIEW_REQUIRED"
    assert any("not a valid power of two" in iss for iss in rep_npot.issues)

    # 3. PBR bounds violation (Roughness 1.8)
    bad_sdef_pbr = ProductionSurfaceDefinition(
        "Surf_Bad_PBR",
        SurfaceType30.METAL,
        MaterialModel30.PBR_METALLIC_ROUGHNESS,
        maps=s_def.maps,
        roughness_base=1.8,
    )
    rep_pbr = SurfaceMaterialValidator.validate_surface_production(bad_sdef_pbr, master_ref, inst_ref)
    assert rep_pbr.is_valid is False
    assert rep_pbr.review_status == "MANUAL_REVIEW_REQUIRED"
    assert any("out of range" in iss for iss in rep_pbr.issues)

    # 4. Section 142 violation: Absolute machine path in master material reference
    bad_mat_path = "D:\\UnrealProjects\\Shaders\\Master_PBR.uasset"
    rep_path = SurfaceMaterialValidator.validate_surface_production(s_def, bad_mat_path, inst_ref)
    assert rep_path.is_valid is False
    assert rep_path.review_status == "MANUAL_REVIEW_REQUIRED"
    assert any("Absolute machine-dependent path" in iss for iss in rep_path.issues)
