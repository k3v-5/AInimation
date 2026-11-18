"""
Tests for World Biome Fabricator, Validator, and Package.
UAF-81.32 Sections 122, 128, 129, 130.
"""

from uaf.world_biome.engine.biome_fabricator import WorldBiomeFabricationPlatform
from uaf.world_biome.validation.biome_validator import WorldBiomeValidator
from uaf.world_biome.package.biome_package import WorldBiomePackage


def test_world_biome_fabrication_all_five_golden_worlds():
    builders = [
        WorldBiomeFabricationPlatform.build_golden_small_combat_map,
        WorldBiomeFabricationPlatform.build_golden_scifi_facility,
        WorldBiomeFabricationPlatform.build_golden_industrial_complex,
        WorldBiomeFabricationPlatform.build_golden_outdoor_combat_map,
        WorldBiomeFabricationPlatform.build_golden_hybrid_level,
    ]

    for builder in builders:
        w_def, tr_ref, lvl_ref = builder()
        assert w_def.bounds.is_valid is True
        assert len(w_def.biomes) >= 1
        assert tr_ref.startswith("TR_")
        assert lvl_ref.startswith("LV_")


def test_world_biome_package_validation_and_serialization():
    w_def, tr_ref, lvl_ref = WorldBiomeFabricationPlatform.build_golden_scifi_facility("World_PkgSciFi")

    report = WorldBiomeValidator.validate_world_biome(w_def, tr_ref, lvl_ref)
    assert report.is_valid is True
    assert report.review_status == "PASSED"
    assert report.quality_score.aggregate_score >= 0.85

    pkg = WorldBiomePackage(
        asset_id="World_PkgSciFi",
        world_def=w_def,
        terrain_ref=tr_ref,
        level_ref=lvl_ref,
        validation_report=report,
    )

    assert len(pkg.package_hash) == 64
    data = pkg.to_dict()
    assert data["asset_id"] == "World_PkgSciFi"
    assert data["world_def"]["world_type"] == "FACILITY"
    assert data["validation_report"]["review_status"] == "PASSED"
