"""
Tests for SurfaceAuthoringEngine, SurfaceAuthoringValidator, and AuthoredSurfacePackage.
UAF-81.11 Sections 195, 196, 197, 198.
"""

from uaf.surface_authoring.authoring.authoring_engine import SurfaceAuthoringEngine
from uaf.surface_authoring.validation.authoring_validator import SurfaceAuthoringValidator
from uaf.surface_authoring.package.authored_package import AuthoredSurfacePackage


def test_surface_authoring_engine_nine_archetypes():
    # 1. Organic Humanoid
    g_org, t_org = SurfaceAuthoringEngine.author_organic_humanoid_surface("Char_Human")
    assert "reg_face" in g_org.regions
    assert t_org.get_texture("BASE_COLOR") is not None

    # 2. Robot
    g_rob, t_rob = SurfaceAuthoringEngine.author_robot_surface("Robot_Unit")
    assert t_rob.get_texture("EMISSIVE") is not None

    # 3. Creature
    g_cre, t_cre = SurfaceAuthoringEngine.author_creature_surface("Beast_Alpha")
    assert "reg_hide" in g_cre.regions

    # 4. Weapon
    g_wep, t_wep = SurfaceAuthoringEngine.author_weapon_surface("Wep_AssaultRifle")
    assert "reg_receiver" in g_wep.regions

    # 5. Armor Piece
    g_arm, t_arm = SurfaceAuthoringEngine.author_armor_surface("Armor_Cuirass")
    assert "reg_plates" in g_arm.regions

    # 6. Clothing Piece
    g_clo, t_clo = SurfaceAuthoringEngine.author_clothing_surface("Cloth_Parka")
    assert "reg_fabric" in g_clo.regions

    # 7. Industrial Prop
    g_prp, t_prp = SurfaceAuthoringEngine.author_industrial_prop_surface("Prop_Generator")
    assert "reg_main" in g_prp.compositions

    # 8. Architectural Block
    g_arc, t_arc = SurfaceAuthoringEngine.author_architectural_block_surface("Arch_ModularWall")
    assert "reg_wall" in g_arc.regions

    # 9. Natural Surface
    g_nat, t_nat = SurfaceAuthoringEngine.author_natural_surface("Env_CliffRock")
    assert "reg_rock" in g_nat.regions


def test_authored_surface_package_validation_and_serialization():
    graph, tex_set = SurfaceAuthoringEngine.author_industrial_prop_surface("Prop_Industrial_Crate")

    report = SurfaceAuthoringValidator.validate_surface_authoring(graph, tex_set)
    assert report.is_valid is True
    assert report.review_status == "PASSED"
    assert report.quality_score.aggregate_score >= 0.85

    pkg = AuthoredSurfacePackage(
        asset_id="Prop_Industrial_Crate",
        archetype_name="INDUSTRIAL_PROP",
        region_graph=graph,
        texture_set=tex_set,
        master_material_id="M_Master_IndustrialProp",
        material_instances=["MI_Crate_Dirty"],
        validation_report=report,
    )

    assert len(pkg.package_hash) == 64
    data = pkg.to_dict()
    assert data["archetype_name"] == "INDUSTRIAL_PROP"
    assert data["validation_report"]["review_status"] == "PASSED"
