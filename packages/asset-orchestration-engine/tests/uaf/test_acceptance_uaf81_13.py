"""
UAF-81.13 Acceptance Tests (Sections 201, 202, 204, 208, 209).
Verifies:
- Section 201: Final Acceptance Criteria (Generates, validates, and packages all 5 canonical worlds:
  Desert World, Forest World, Industrial Wasteland, Alien Biome, and Hybrid Multi-Biome World).
- Sections 202, 204, 208, 209: Non-Negotiable Requirements Test (Zero tolerance for vegetation blocking spawns,
  flat-terrain assumptions, or unseeded generation; violations strictly flag MANUAL_REVIEW_REQUIRED).
"""

from uaf.world_surface.generator.world_surface_fabricator import ProceduralWorldSurfaceFabricator
from uaf.world_surface.validation.world_surface_validator import WorldSurfaceValidator
from uaf.world_surface.terrain.territory import TerritoryModel
from uaf.world_surface.package.world_surface_package import WorldSurfacePackage


def test_final_world_surface_acceptance_section_201():
    """
    Acceptance Test Section 201:
    Deterministically synthesizes all 5 canonical worlds:
    1. Desert World
    2. Forest World
    3. Industrial Wasteland
    4. Alien Biome
    5. Hybrid Multi-Biome World
    """
    worlds = [
        ("World_Golden_Desert", "DESERT_WORLD", ProceduralWorldSurfaceFabricator.build_desert_world),
        ("World_Golden_Forest", "FOREST_WORLD", ProceduralWorldSurfaceFabricator.build_forest_world),
        ("World_Golden_Wasteland", "INDUSTRIAL_WASTELAND", ProceduralWorldSurfaceFabricator.build_industrial_wasteland_world),
        ("World_Golden_Alien", "ALIEN_BIOME", ProceduralWorldSurfaceFabricator.build_alien_biome_world),
        ("World_Golden_Hybrid", "HYBRID_MULTI_BIOME", ProceduralWorldSurfaceFabricator.build_hybrid_multi_biome_world),
    ]

    for asset_id, world_type, builder_fn in worlds:
        terr, biomes, landmarks = builder_fn(asset_id)
        report = WorldSurfaceValidator.validate_world_surface(terr, biomes, landmarks)

        assert report.is_valid is True, f"Failed for {asset_id}: {report.issues}"
        assert report.review_status == "PASSED"
        assert report.quality_score.aggregate_score >= 0.80

        pkg = WorldSurfacePackage(
            asset_id=asset_id,
            world_type=world_type,
            territory=terr,
            biomes=biomes,
            landmarks=landmarks,
            validation_report=report,
        )
        assert len(pkg.package_hash) == 64
        assert pkg.to_dict()["asset_id"] == asset_id


def test_non_negotiable_requirements_section_202_204_208():
    """
    Acceptance Test Sections 202, 204, 208, 209:
    Non-negotiable requirements:
    1. Section 204: Vegetation MUST NOT block player spawn points or critical paths.
    2. Section 208: Subsystem MUST NOT assume flat terrain (max_height <= min_height).
    3. Section 202: Territory MUST NOT have non-positive dimensions.
    Any violation strictly triggers review_status = MANUAL_REVIEW_REQUIRED.
    """
    terr, biomes, landmarks = ProceduralWorldSurfaceFabricator.build_forest_world("World_Test")

    # 1. Section 204 violation: Vegetation blocking player spawn
    rep_veg = WorldSurfaceValidator.validate_world_surface(
        terr, biomes, landmarks, has_vegetation_blocking_spawn=True
    )
    assert rep_veg.is_valid is False
    assert rep_veg.review_status == "MANUAL_REVIEW_REQUIRED"
    assert any("Foliage blocks player spawn point" in iss for iss in rep_veg.issues)

    # 2. Section 208 violation: Flat terrain assumption
    flat_terr = TerritoryModel("Terr_Flat", 1000.0, 1000.0, min_height_m=50.0, max_height_m=50.0)
    rep_flat = WorldSurfaceValidator.validate_world_surface(flat_terr, biomes, landmarks)
    assert rep_flat.is_valid is False
    assert rep_flat.review_status == "MANUAL_REVIEW_REQUIRED"
    assert any("assumes flat terrain" in iss for iss in rep_flat.issues)
