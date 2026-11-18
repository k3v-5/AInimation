"""
UAF-81.32 Acceptance Tests (Sections 122, 9, 10, 27, 33, 119).
Verifies:
- Section 122: Final Acceptance Criteria (Generates and validates all 5 Golden Reference Worlds:
  Golden Small Combat Map, Golden Sci-Fi Facility, Golden Industrial Complex, Golden Outdoor Combat Map, Golden Hybrid Level).
- Sections 9, 10, 27, 33, 119: Non-Negotiable Requirements Test (Zero tolerance for invalid world bounds,
  out-of-range biome parameters, missing terrain references, or absolute machine-dependent paths; violations strictly flag MANUAL_REVIEW_REQUIRED).
"""

from uaf.world_biome.engine.biome_fabricator import WorldBiomeFabricationPlatform
from uaf.world_biome.validation.biome_validator import WorldBiomeValidator
from uaf.world_biome.models.definition import (
    BiomeWorldDefinition,
    WorldType32,
    BiomeType32,
    WorldBounds32,
    BiomeDefinition32,
)
from uaf.world_biome.package.biome_package import WorldBiomePackage


def test_final_world_biome_acceptance_section_122():
    """
    Acceptance Test Section 122:
    Synthesizes and validates all 5 Golden Reference Worlds.
    """
    builders = [
        ("World_Gold_Combat", WorldBiomeFabricationPlatform.build_golden_small_combat_map),
        ("World_Gold_Facility", WorldBiomeFabricationPlatform.build_golden_scifi_facility),
        ("World_Gold_Industrial", WorldBiomeFabricationPlatform.build_golden_industrial_complex),
        ("World_Gold_Outdoor", WorldBiomeFabricationPlatform.build_golden_outdoor_combat_map),
        ("World_Gold_Hybrid", WorldBiomeFabricationPlatform.build_golden_hybrid_level),
    ]

    for asset_id, builder_fn in builders:
        w_def, tr_ref, lvl_ref = builder_fn(asset_id)
        assert w_def.bounds.is_valid is True
        assert len(w_def.biomes) >= 1

        report = WorldBiomeValidator.validate_world_biome(w_def, tr_ref, lvl_ref)
        assert report.is_valid is True, f"Failed for {asset_id}: {report.issues}"
        assert report.review_status == "PASSED"
        assert report.quality_score.aggregate_score >= 0.85

        pkg = WorldBiomePackage(
            asset_id=asset_id,
            world_def=w_def,
            terrain_ref=tr_ref,
            level_ref=lvl_ref,
            validation_report=report,
        )
        assert len(pkg.package_hash) == 64
        assert pkg.to_dict()["asset_id"] == asset_id


def test_non_negotiable_requirements_section_9_10_27_33_119():
    """
    Acceptance Test Sections 9, 10, 27, 33, 119:
    Non-negotiable requirements:
    1. Section 9 & 10: Invalid bounds (min >= max or span < 100cm) strictly fails.
    2. Section 28 & 33: Invalid biome parameter (temperature/humidity not in [0.0, 1.0]) strictly fails.
    3. Section 27: Missing terrain reference strictly fails.
    4. Section 119: Absolute machine-dependent reference paths strictly fails.
    Any violation strictly triggers review_status = MANUAL_REVIEW_REQUIRED.
    """
    w_def, tr_ref, lvl_ref = WorldBiomeFabricationPlatform.build_golden_small_combat_map("World_Fault_Test")

    # 1. Section 9 & 10 violation: Inverted bounds
    bad_bounds = WorldBounds32(min_x=5000.0, max_x=-5000.0)
    bad_wdef_bounds = BiomeWorldDefinition(
        "World_BadBounds",
        WorldType32.ROOM_BASED,
        bad_bounds,
        w_def.biomes,
    )
    rep_bounds = WorldBiomeValidator.validate_world_biome(bad_wdef_bounds, tr_ref, lvl_ref)
    assert rep_bounds.is_valid is False
    assert rep_bounds.review_status == "MANUAL_REVIEW_REQUIRED"
    assert any("World bounds are invalid" in iss for iss in rep_bounds.issues)

    # 2. Section 28 & 33 violation: Biome temperature > 1.0
    bad_biome = BiomeDefinition32("Biome_SuperHot", BiomeType32.VOLCANIC_WASTELAND, temperature=2.5)
    bad_wdef_biome = BiomeWorldDefinition(
        "World_BadBiome",
        WorldType32.ROOM_BASED,
        w_def.bounds,
        [bad_biome],
    )
    rep_biome = WorldBiomeValidator.validate_world_biome(bad_wdef_biome, tr_ref, lvl_ref)
    assert rep_biome.is_valid is False
    assert rep_biome.review_status == "MANUAL_REVIEW_REQUIRED"
    assert any("invalid parameter ranges" in iss for iss in rep_biome.issues)

    # 3. Section 27 violation: Missing terrain reference
    rep_tr = WorldBiomeValidator.validate_world_biome(w_def, "", lvl_ref)
    assert rep_tr.is_valid is False
    assert rep_tr.review_status == "MANUAL_REVIEW_REQUIRED"
    assert any("lacks heightmap terrain" in iss for iss in rep_tr.issues)

    # 4. Section 119 violation: Absolute machine path in level reference
    bad_lvl_path = "D:\\UnrealProjects\\Maps\\LV_Arena.umap"
    rep_path = WorldBiomeValidator.validate_world_biome(w_def, tr_ref, bad_lvl_path)
    assert rep_path.is_valid is False
    assert rep_path.review_status == "MANUAL_REVIEW_REQUIRED"
    assert any("Absolute machine-dependent path" in iss for iss in rep_path.issues)
