"""
UAF-81.36 Acceptance Tests (Sections 123, 117, 8, 14, 126, 127).
Verifies:
- Section 123: Final Acceptance Criteria (Generates and validates all 7 Golden Worlds:
  Forest, Desert, Mountain, Swamp, River Valley, Urban Outdoor, Alien Biome).
- Section 117: Hard Fail Conditions Test (Zero tolerance for invalid height range, non-positive scales,
  impossible ecology, or absolute machine-dependent paths; violations strictly flag MANUAL_REVIEW_REQUIRED).
"""

from uaf.terrain_biome.engine.terrain_biome_fabricator import TerrainBiomeFabricationPlatform
from uaf.terrain_biome.validation.terrain_biome_validator import TerrainBiomeValidator
from uaf.terrain_biome.models.definition import (
    TerrainBiomeSpecification,
    BiomeType36,
    VegetationCategory36,
    TerrainBounds36,
)
from uaf.terrain_biome.package.terrain_biome_package import TerrainBiomePackage


def test_final_terrain_biome_acceptance_section_123():
    """
    Acceptance Test Section 123:
    Synthesizes and validates all 7 Golden Worlds.
    """
    builders = [
        ("Terrain_Gold_Forest", TerrainBiomeFabricationPlatform.build_golden_forest),
        ("Terrain_Gold_Desert", TerrainBiomeFabricationPlatform.build_golden_desert),
        ("Terrain_Gold_Mountain", TerrainBiomeFabricationPlatform.build_golden_mountain),
        ("Terrain_Gold_Swamp", TerrainBiomeFabricationPlatform.build_golden_swamp),
        ("Terrain_Gold_RiverValley", TerrainBiomeFabricationPlatform.build_golden_river_valley),
        ("Terrain_Gold_UrbanOutdoor", TerrainBiomeFabricationPlatform.build_golden_urban_outdoor),
        ("Terrain_Gold_AlienBiome", TerrainBiomeFabricationPlatform.build_golden_alien_biome),
    ]

    for terrain_id, builder_fn in builders:
        spec, land_path = builder_fn(terrain_id)
        assert spec.is_valid_scale is True

        report = TerrainBiomeValidator.validate_terrain_biome(spec, land_path)
        assert report.is_valid is True, f"Failed for {terrain_id}: {report.issues}"
        assert report.review_status == "PASSED"
        assert report.quality_score.aggregate_score >= 0.85

        pkg = TerrainBiomePackage(
            terrain_id=terrain_id,
            spec=spec,
            landscape_asset_path=land_path,
            validation_report=report,
        )
        assert len(pkg.package_hash) == 64
        assert pkg.to_dict()["terrain_id"] == terrain_id


def test_hard_fail_conditions_section_117():
    """
    Acceptance Test Section 117:
    Hard fail conditions:
    1. INVALID_HEIGHT_RANGE/SCALE: min >= max or span < 10m, dimensions <= 0.
    2. IMPOSSIBLE_ECOLOGY: Fern/Root in arid Desert, Alien plant in Urban.
    3. Path purity: Absolute machine-dependent reference paths.
    Any violation strictly triggers review_status = MANUAL_REVIEW_REQUIRED.
    """
    spec, land_path = TerrainBiomeFabricationPlatform.build_golden_forest("Terrain_Fault_Test")

    # 1. Height range violation: Flat terrain with 2m span (< 10m)
    bad_bounds = TerrainBounds36(min_height_m=10.0, max_height_m=12.0)
    bad_spec_bounds = TerrainBiomeSpecification(
        "Terrain_Flat",
        BiomeType36.FOREST,
        bounds=bad_bounds,
    )
    rep_bounds = TerrainBiomeValidator.validate_terrain_biome(bad_spec_bounds, land_path)
    assert rep_bounds.is_valid is False
    assert rep_bounds.review_status == "MANUAL_REVIEW_REQUIRED"
    assert any("INVALID_HEIGHT_RANGE/SCALE" in iss for iss in rep_bounds.issues)

    # 2. Ecological violation: Fern in arid desert
    bad_desert = TerrainBiomeSpecification(
        "Terrain_FernDesert",
        BiomeType36.DESERT,
        vegetation_categories=[VegetationCategory36.FERN],
    )
    rep_eco = TerrainBiomeValidator.validate_terrain_biome(bad_desert, land_path)
    assert rep_eco.is_valid is False
    assert rep_eco.review_status == "MANUAL_REVIEW_REQUIRED"
    assert any("IMPOSSIBLE_ECOLOGY" in iss for iss in rep_eco.issues)

    # 3. Path purity violation: Absolute machine path
    bad_land_path = "D:\\UnrealProjects\\Landscapes\\Terrain_Test.umap"
    rep_path = TerrainBiomeValidator.validate_terrain_biome(spec, bad_land_path)
    assert rep_path.is_valid is False
    assert rep_path.review_status == "MANUAL_REVIEW_REQUIRED"
    assert any("Absolute machine-dependent path" in iss for iss in rep_path.issues)
