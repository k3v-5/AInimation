"""
UAF-81.51 Acceptance Tests (Sections 135, 134, 145, 146, 147, 139, 142).
Verifies:
- Section 135: Final Acceptance Criteria (Generates and validates all 6 Golden Environments:
  Forest, Desert, Mountain, Swamp, Coastal, Hybrid).
- Sections 134, 145, 146, 147: Hard Fail Conditions Test (Zero tolerance for invalid terrain dimensions,
  height scale < 10m, missing erosion, vegetation, rocks, water, nav, or streaming, or absolute machine-dependent paths;
  violations strictly flag MANUAL_REVIEW_REQUIRED).
"""

from uaf.natural_ecosystem.engine.natural_ecosystem_fabricator import NaturalEcosystemFabricationPlatform
from uaf.natural_ecosystem.validation.natural_ecosystem_validator import NaturalEcosystemValidator
from uaf.natural_ecosystem.models.definition import (
    NaturalEcosystemSpecification,
    NaturalBiomeType51,
    TerrainType51,
    NaturalTerrainDimensions51,
)
from uaf.natural_ecosystem.package.natural_ecosystem_package import NaturalEcosystemPackage


def test_final_natural_ecosystem_acceptance_section_135():
    """
    Acceptance Test Section 135:
    Synthesizes and validates all 6 Golden Environments.
    """
    builders = [
        ("Eco_Gold_Forest51", NaturalEcosystemFabricationPlatform.build_golden_forest),
        ("Eco_Gold_Desert51", NaturalEcosystemFabricationPlatform.build_golden_desert),
        ("Eco_Gold_Mountain51", NaturalEcosystemFabricationPlatform.build_golden_mountain),
        ("Eco_Gold_Swamp51", NaturalEcosystemFabricationPlatform.build_golden_swamp),
        ("Eco_Gold_Coastal51", NaturalEcosystemFabricationPlatform.build_golden_coastal),
        ("Eco_Gold_Hybrid51", NaturalEcosystemFabricationPlatform.build_golden_hybrid),
    ]

    for eco_id, builder_fn in builders:
        spec, land_path, fol_path, water_path, nav_path = builder_fn(eco_id)
        assert spec.is_valid_ecosystem is True

        report = NaturalEcosystemValidator.validate_natural_ecosystem(spec, land_path, fol_path, water_path, nav_path)
        assert report.is_valid is True, f"Failed for {eco_id}: {report.issues}"
        assert report.review_status == "PASSED"
        assert report.quality_score.aggregate_score >= 0.85

        pkg = NaturalEcosystemPackage(
            ecosystem_id=eco_id,
            spec=spec,
            landscape_asset_path=land_path,
            foliage_asset_path=fol_path,
            water_mesh_path=water_path,
            navmesh_path=nav_path,
            validation_report=report,
        )
        assert len(pkg.package_hash) == 64
        assert pkg.to_dict()["ecosystem_id"] == eco_id


def test_hard_fail_conditions_section_134_145_146_147():
    """
    Acceptance Test Sections 134, 145, 146, 147:
    Hard fail conditions:
    1. INVALID_TERRAIN_DIMENSIONS: Non-positive width/length or height scale < 10m.
    2. MISSING_CORE_SUBSYSTEMS: has_erosion, has_vegetation, has_rocks, has_water, has_poi, has_navigation, or has_streaming is False.
    3. Path purity: Absolute machine-dependent reference paths.
    Any violation strictly triggers review_status = MANUAL_REVIEW_REQUIRED.
    """
    spec, land_path, fol_path, water_path, nav_path = NaturalEcosystemFabricationPlatform.build_golden_forest("Eco_Fault_Test")

    # 1. Height scale violation: 4.0m (< 10.0m)
    bad_dims = NaturalTerrainDimensions51(width_m=2000.0, length_m=2000.0, height_scale_m=4.0)
    bad_spec_dims = NaturalEcosystemSpecification(
        "Eco_FlatScale",
        NaturalBiomeType51.FOREST,
        TerrainType51.ROLLING,
        dimensions=bad_dims,
    )
    rep_dims = NaturalEcosystemValidator.validate_natural_ecosystem(bad_spec_dims, land_path, fol_path, water_path, nav_path)
    assert rep_dims.is_valid is False
    assert rep_dims.review_status == "MANUAL_REVIEW_REQUIRED"
    assert any("INVALID_TERRAIN_DIMENSIONS" in iss for iss in rep_dims.issues)

    # 2. Missing water system
    bad_spec_water = NaturalEcosystemSpecification(
        "Eco_NoWater",
        NaturalBiomeType51.FOREST,
        TerrainType51.ROLLING,
        has_water=False,
    )
    rep_water = NaturalEcosystemValidator.validate_natural_ecosystem(bad_spec_water, land_path, fol_path, water_path, nav_path)
    assert rep_water.is_valid is False
    assert rep_water.review_status == "MANUAL_REVIEW_REQUIRED"
    assert any("MISSING_CORE_SUBSYSTEMS" in iss for iss in rep_water.issues)

    # 3. Missing vegetation
    bad_spec_veg = NaturalEcosystemSpecification(
        "Eco_NoVeg",
        NaturalBiomeType51.FOREST,
        TerrainType51.ROLLING,
        has_vegetation=False,
    )
    rep_veg = NaturalEcosystemValidator.validate_natural_ecosystem(bad_spec_veg, land_path, fol_path, water_path, nav_path)
    assert rep_veg.is_valid is False
    assert rep_veg.review_status == "MANUAL_REVIEW_REQUIRED"
    assert any("MISSING_CORE_SUBSYSTEMS" in iss for iss in rep_veg.issues)

    # 4. Path purity violation: Absolute machine path
    bad_land_path = "D:\\UnrealProjects\\Natural\\Landscape_Forest.umap"
    rep_path = NaturalEcosystemValidator.validate_natural_ecosystem(spec, bad_land_path, fol_path, water_path, nav_path)
    assert rep_path.is_valid is False
    assert rep_path.review_status == "MANUAL_REVIEW_REQUIRED"
    assert any("Absolute machine-dependent path" in iss for iss in rep_path.issues)
