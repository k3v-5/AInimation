"""
Tests for World Surface Fabricator, Validation, and Package.
UAF-81.13 Sections 190, 200, 201.
"""

from uaf.world_surface.generator.world_surface_fabricator import ProceduralWorldSurfaceFabricator
from uaf.world_surface.validation.world_surface_validator import WorldSurfaceValidator
from uaf.world_surface.package.world_surface_package import WorldSurfacePackage


def test_world_surface_fabricator_five_worlds():
    # 1. Desert
    t_des, b_des, l_des = ProceduralWorldSurfaceFabricator.build_desert_world("World_Desert_Test")
    assert len(b_des) == 1
    assert len(l_des) == 2

    # 2. Forest
    t_for, b_for, l_for = ProceduralWorldSurfaceFabricator.build_forest_world("World_Forest_Test")
    assert b_for[0].has_water is True

    # 3. Wasteland
    t_wst, b_wst, l_wst = ProceduralWorldSurfaceFabricator.build_industrial_wasteland_world("World_Wasteland_Test")
    assert b_wst[0].rock_density >= 0.5

    # 4. Alien
    t_aln, b_aln, l_aln = ProceduralWorldSurfaceFabricator.build_alien_biome_world("World_Alien_Test")
    assert any(lm.prominence == 1.0 for lm in l_aln)

    # 5. Hybrid Multi-Biome
    t_hyb, b_hyb, l_hyb = ProceduralWorldSurfaceFabricator.build_hybrid_multi_biome_world("World_Multi_Test")
    assert len(b_hyb) == 3


def test_world_surface_package_validation_and_serialization():
    terr, biomes, landmarks = ProceduralWorldSurfaceFabricator.build_forest_world("World_Forest_Pkg")

    report = WorldSurfaceValidator.validate_world_surface(terr, biomes, landmarks)
    assert report.is_valid is True
    assert report.review_status == "PASSED"
    assert report.quality_score.aggregate_score >= 0.80

    pkg = WorldSurfacePackage(
        asset_id="World_Forest_Package",
        world_type="FOREST_WORLD",
        territory=terr,
        biomes=biomes,
        landmarks=landmarks,
        validation_report=report,
    )

    assert len(pkg.package_hash) == 64
    data = pkg.to_dict()
    assert data["world_type"] == "FOREST_WORLD"
    assert len(data["biomes"]) == 1
    assert data["validation_report"]["review_status"] == "PASSED"
