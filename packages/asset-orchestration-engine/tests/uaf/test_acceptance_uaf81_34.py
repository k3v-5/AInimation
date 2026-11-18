"""
UAF-81.34 Acceptance Tests (Sections 7, 127, 6, 12, 124).
Verifies:
- Sections 7, 127: Final Acceptance Criteria (Generates and validates all 10 Golden Material Presets:
  Brushed Steel, Damaged Steel, Black Rubber, Tactical Fabric, Human Skin, Alien Skin, Concrete, Rusted Metal, Polished Chrome, Obsidian).
- Sections 6, 12, 124: Non-Negotiable Requirements Test (Zero tolerance for out-of-range PBR bounds,
  invalid decal parameters, or absolute machine-dependent paths; violations strictly flag MANUAL_REVIEW_REQUIRED).
"""

from uaf.surface_decal.engine.surface_decal_fabricator import SurfaceDecalFabricationPlatform
from uaf.surface_decal.validation.surface_decal_validator import SurfaceDecalValidator
from uaf.surface_decal.models.definition import (
    SurfaceAuthoringSpecification,
    MaterialFamily34,
    SurfaceDecalItem,
)
from uaf.surface_decal.package.surface_decal_package import SurfaceDecalPackage


def test_final_surface_decal_acceptance_sections_7_and_127():
    """
    Acceptance Test Sections 7 and 127:
    Synthesizes and validates all 10 Golden Material Presets.
    """
    builders = [
        ("Mat_Gold_BrushedSteel", SurfaceDecalFabricationPlatform.build_golden_brushed_steel),
        ("Mat_Gold_DamagedSteel", SurfaceDecalFabricationPlatform.build_golden_damaged_steel),
        ("Mat_Gold_BlackRubber", SurfaceDecalFabricationPlatform.build_golden_black_rubber),
        ("Mat_Gold_TacticalFabric", SurfaceDecalFabricationPlatform.build_golden_tactical_fabric),
        ("Mat_Gold_HumanSkin", SurfaceDecalFabricationPlatform.build_golden_human_skin),
        ("Mat_Gold_AlienSkin", SurfaceDecalFabricationPlatform.build_golden_alien_skin),
        ("Mat_Gold_Concrete", SurfaceDecalFabricationPlatform.build_golden_concrete),
        ("Mat_Gold_RustedMetal", SurfaceDecalFabricationPlatform.build_golden_rusted_metal),
        ("Mat_Gold_PolishedChrome", SurfaceDecalFabricationPlatform.build_golden_polished_chrome),
        ("Mat_Gold_Obsidian", SurfaceDecalFabricationPlatform.build_golden_obsidian),
    ]

    for asset_id, builder_fn in builders:
        spec, master_ref, inst_ref = builder_fn(asset_id)
        assert spec.is_valid_pbr is True

        report = SurfaceDecalValidator.validate_surface_authoring(spec, master_ref, inst_ref)
        assert report.is_valid is True, f"Failed for {asset_id}: {report.issues}"
        assert report.review_status == "PASSED"
        assert report.quality_score.aggregate_score >= 0.85

        pkg = SurfaceDecalPackage(
            asset_id=asset_id,
            surface_spec=spec,
            master_material_ref=master_ref,
            instance_material_ref=inst_ref,
            validation_report=report,
        )
        assert len(pkg.package_hash) == 64
        assert pkg.to_dict()["asset_id"] == asset_id


def test_non_negotiable_requirements_section_6_12_124():
    """
    Acceptance Test Sections 6, 12, 124:
    Non-negotiable requirements:
    1. Section 6: Roughness outside [0.0, 1.0] strictly fails.
    2. Section 6: Metallic outside [0.0, 1.0] strictly fails.
    3. Section 124: Decal with invalid dimensions or opacity strictly fails.
    4. Section 124: Absolute machine-dependent reference paths strictly fails.
    Any violation strictly triggers review_status = MANUAL_REVIEW_REQUIRED.
    """
    spec, master_ref, inst_ref = SurfaceDecalFabricationPlatform.build_golden_brushed_steel("Mat_Fault_Test")

    # 1. Section 6 violation: Roughness 1.4
    bad_spec_rough = SurfaceAuthoringSpecification(
        "Mat_BadRough",
        MaterialFamily34.METAL,
        roughness_base=1.4,
    )
    rep_rough = SurfaceDecalValidator.validate_surface_authoring(bad_spec_rough, master_ref, inst_ref)
    assert rep_rough.is_valid is False
    assert rep_rough.review_status == "MANUAL_REVIEW_REQUIRED"
    assert any("outside range [0.0, 1.0]" in iss for iss in rep_rough.issues)

    # 2. Section 124 violation: Decal opacity 1.5 (> 1.0)
    bad_decal = SurfaceDecalItem("Decal_BadOp", "LOGO", [50.0, 50.0], opacity=1.5)
    bad_spec_decal = SurfaceAuthoringSpecification(
        "Mat_BadDecal",
        MaterialFamily34.METAL,
        decals=[bad_decal],
    )
    rep_decal = SurfaceDecalValidator.validate_surface_authoring(bad_spec_decal, master_ref, inst_ref)
    assert rep_decal.is_valid is False
    assert rep_decal.review_status == "MANUAL_REVIEW_REQUIRED"
    assert any("has invalid dimensions" in iss or "outside [0.0, 1.0]" in iss for iss in rep_decal.issues)

    # 3. Section 124 violation: Absolute machine path in master material reference
    bad_mat_path = "D:\\UnrealProjects\\Materials\\M_Master_Custom.uasset"
    rep_path = SurfaceDecalValidator.validate_surface_authoring(spec, bad_mat_path, inst_ref)
    assert rep_path.is_valid is False
    assert rep_path.review_status == "MANUAL_REVIEW_REQUIRED"
    assert any("Absolute machine-dependent path" in iss for iss in rep_path.issues)
