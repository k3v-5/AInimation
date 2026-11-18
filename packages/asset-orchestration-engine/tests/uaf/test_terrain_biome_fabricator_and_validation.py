"""
Tests for Terrain Biome Fabricator, Validator, and Package.
UAF-81.36 Sections 123, 126, 127.
"""

from uaf.terrain_biome.engine.terrain_biome_fabricator import TerrainBiomeFabricationPlatform
from uaf.terrain_biome.validation.terrain_biome_validator import TerrainBiomeValidator
from uaf.terrain_biome.package.terrain_biome_package import TerrainBiomePackage


def test_terrain_biome_fabrication_all_seven_golden_worlds():
    builders = [
        TerrainBiomeFabricationPlatform.build_golden_forest,
        TerrainBiomeFabricationPlatform.build_golden_desert,
        TerrainBiomeFabricationPlatform.build_golden_mountain,
        TerrainBiomeFabricationPlatform.build_golden_swamp,
        TerrainBiomeFabricationPlatform.build_golden_river_valley,
        TerrainBiomeFabricationPlatform.build_golden_urban_outdoor,
        TerrainBiomeFabricationPlatform.build_golden_alien_biome,
    ]

    for builder in builders:
        spec, land_path = builder()
        assert spec.is_valid_scale is True
        assert land_path.startswith("/Game/Environments/Landscapes/")


def test_terrain_biome_package_validation_and_serialization():
    spec, land_path = TerrainBiomeFabricationPlatform.build_golden_forest("Terrain_PkgForest")

    report = TerrainBiomeValidator.validate_terrain_biome(spec, land_path)
    assert report.is_valid is True
    assert report.review_status == "PASSED"
    assert report.quality_score.aggregate_score >= 0.85

    pkg = TerrainBiomePackage(
        terrain_id="Terrain_PkgForest",
        spec=spec,
        landscape_asset_path=land_path,
        validation_report=report,
    )

    assert len(pkg.package_hash) == 64
    data = pkg.to_dict()
    assert data["terrain_id"] == "Terrain_PkgForest"
    assert data["spec"]["primary_biome"] == "FOREST"
    assert data["validation_report"]["review_status"] == "PASSED"
