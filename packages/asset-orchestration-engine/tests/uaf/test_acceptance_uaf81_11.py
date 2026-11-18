"""
UAF-81.11 Acceptance Tests (Sections 196, 197, 198).
Verifies:
- Section 196: Final Acceptance Criteria (Synthesizes, validates, and packages PBR surfaces for
  all 9 canonical archetypes: Organic Humanoid, Robot, Creature, Weapon, Armor Piece, Clothing Piece,
  Industrial Prop, Architectural Block, and Natural Surface).
- Sections 197 & 198: Non-Negotiable Requirements Test (Zero tolerance for color-space mismatch or
  flat unvaried colors; violations strictly flag MANUAL_REVIEW_REQUIRED).
"""

from uaf.surface_authoring.authoring.authoring_engine import SurfaceAuthoringEngine
from uaf.surface_authoring.validation.authoring_validator import SurfaceAuthoringValidator
from uaf.surface_authoring.package.authored_package import AuthoredSurfacePackage
from uaf.surface_authoring.models.regions import MaterialRegionGraph, SurfaceRegion, MaterialFamilyType
from uaf.surface.models.texture_set import TextureSet
from uaf.surface.models.texture_definition import TextureDefinition
from uaf.surface.models.channels import ColorSpace, PBRChannel


def test_final_surface_authoring_acceptance_section_196():
    """
    Acceptance Test Section 196:
    Synthesizes and validates PBR materials for all 9 canonical archetypes:
    1. Organic Humanoid
    2. Robot
    3. Creature
    4. Weapon
    5. Armor Piece
    6. Clothing Piece
    7. Industrial Prop
    8. Architectural Block
    9. Natural Surface
    """
    archetypes = [
        ("Char_Golden_Human", SurfaceAuthoringEngine.author_organic_humanoid_surface),
        ("Robot_Golden_Android", SurfaceAuthoringEngine.author_robot_surface),
        ("Creature_Golden_Dragon", SurfaceAuthoringEngine.author_creature_surface),
        ("Weapon_Golden_Rifle", SurfaceAuthoringEngine.author_weapon_surface),
        ("Armor_Golden_Cuirass", SurfaceAuthoringEngine.author_armor_surface),
        ("Cloth_Golden_Cloak", SurfaceAuthoringEngine.author_clothing_surface),
        ("Prop_Golden_Container", SurfaceAuthoringEngine.author_industrial_prop_surface),
        ("Arch_Golden_Column", SurfaceAuthoringEngine.author_architectural_block_surface),
        ("Env_Golden_Boulder", SurfaceAuthoringEngine.author_natural_surface),
    ]

    for asset_id, author_fn in archetypes:
        graph, tex_set = author_fn(asset_id)
        report = SurfaceAuthoringValidator.validate_surface_authoring(graph, tex_set)

        assert report.is_valid is True, f"Failed for {asset_id}: {report.issues}"
        assert report.review_status == "PASSED"
        assert report.quality_score.aggregate_score >= 0.85

        pkg = AuthoredSurfacePackage(
            asset_id=asset_id,
            archetype_name=asset_id.split("_")[0],
            region_graph=graph,
            texture_set=tex_set,
            master_material_id="M_Master_PBR",
            material_instances=[f"MI_{asset_id}"],
            validation_report=report,
        )
        assert len(pkg.package_hash) == 64
        assert pkg.to_dict()["asset_id"] == asset_id


def test_non_negotiable_requirements_section_197_198():
    """
    Acceptance Test Sections 197 & 198:
    Non-negotiable requirements:
    1. Rule 197: No flat code-assigned colors alone (must have spatial texture variation).
    2. Rule 198: Zero tolerance for color space mismatch (e.g. Normal in sRGB, Linear maps in sRGB).
    Any violation strictly triggers review_status = MANUAL_REVIEW_REQUIRED.
    """
    graph = MaterialRegionGraph(asset_id="Asset_Flawed")
    graph.add_region(SurfaceRegion("reg_body", MaterialFamilyType.METAL))

    # 1. Color space mismatch (Normal map marked as sRGB)
    bad_tex_set = TextureSet(set_id="Flawed_TexSet")
    bad_normal = TextureDefinition(
        texture_id="T_Flawed_Normal",
        channel="NORMAL",
        resolution=2048,
        color_space=ColorSpace.SRGB,  # VIOLATION: Normal must be NORMAL_MAP!
    )
    good_base = TextureDefinition(
        texture_id="T_Valid_BaseColor",
        channel="BASE_COLOR",
        resolution=2048,
        color_space=ColorSpace.SRGB,
    )
    bad_tex_set.add_texture("NORMAL", bad_normal)
    bad_tex_set.add_texture("BASE_COLOR", good_base)

    rep_cs = SurfaceAuthoringValidator.validate_surface_authoring(graph, bad_tex_set)
    assert rep_cs.is_valid is False
    assert rep_cs.review_status == "MANUAL_REVIEW_REQUIRED"
    assert any("invalid color space" in iss for iss in rep_cs.issues)

    # 2. Flat color without texture variation (Rule 197)
    flat_tex_set = TextureSet(set_id="Flat_TexSet")
    flat_tex_set.add_texture("BASE_COLOR", good_base)  # Only 1 single map, no normal/ORM

    rep_flat = SurfaceAuthoringValidator.validate_surface_authoring(graph, flat_tex_set)
    assert rep_flat.is_valid is False
    assert rep_flat.review_status == "MANUAL_REVIEW_REQUIRED"
    assert any("lacks spatial texture variance" in iss for iss in rep_flat.issues)
