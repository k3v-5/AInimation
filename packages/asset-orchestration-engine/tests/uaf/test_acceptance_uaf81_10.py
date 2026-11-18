"""
UAF-81.10 Acceptance Tests (Sections 165, 166, 167, 168).
Verifies:
- Section 165: Final Acceptance Criteria (Generates all 6 required archetypes:
  Organic Humanoid, Clothed Humanoid, Armored Humanoid, Mechanical Entity, Creature, and Hybrid Entity).
- Section 167 & 168: Non-Negotiable Requirements Test (Layering integrity and primary forms strictly enforced;
  inversions or missing forms flag MANUAL_REVIEW_REQUIRED).
"""

from uaf.fabrication.generator.character_fabricator import ProceduralCharacterFabricator
from uaf.fabrication.validation.fabrication_validator import FabricationValidator
from uaf.fabrication.anatomy.proportions import ProportionProfile
from uaf.fabrication.anatomy.body_graph import SemanticBodyGraph, FormLevel
from uaf.fabrication.garments.garment import GarmentDefinition, GarmentLayer
from uaf.fabrication.package.fabricated_package import FabricatedCharacterPackage


def test_final_character_fabrication_acceptance_section_165():
    """
    Acceptance Test Section 165:
    Generates all 6 required archetypes without relying on a single global remesh:
    1. Organic Humanoid
    2. Clothed Humanoid
    3. Armored Humanoid
    4. Mechanical Character
    5. Creature
    6. Hybrid Character
    """
    proportions = ProportionProfile.create_heroic_profile("Prop_Golden_Hero")

    # 1. Organic Humanoid
    g_org = ProceduralCharacterFabricator.build_organic_humanoid("Char_Golden_Organic")
    r_org = FabricationValidator.validate_fabrication(g_org, proportions)
    assert r_org.is_valid is True
    assert r_org.review_status == "PASSED"

    # 2. Clothed Humanoid
    g_cloth, garments_cloth = ProceduralCharacterFabricator.build_clothed_humanoid("Char_Golden_Clothed")
    r_cloth = FabricationValidator.validate_fabrication(g_cloth, proportions, garments_cloth)
    assert r_cloth.is_valid is True
    assert r_cloth.review_status == "PASSED"

    # 3. Armored Humanoid
    g_arm, garments_arm = ProceduralCharacterFabricator.build_armored_humanoid("Char_Golden_Armored")
    r_arm = FabricationValidator.validate_fabrication(g_arm, proportions, garments_arm)
    assert r_arm.is_valid is True
    assert r_arm.review_status == "PASSED"

    # 4. Mechanical Character
    g_mech = ProceduralCharacterFabricator.build_mechanical_character("Char_Golden_Mech")
    r_mech = FabricationValidator.validate_fabrication(g_mech, proportions)
    assert r_mech.is_valid is True
    assert r_mech.review_status == "PASSED"

    # 5. Creature
    g_creature = ProceduralCharacterFabricator.build_creature("Char_Golden_Creature")
    r_creature = FabricationValidator.validate_fabrication(g_creature, proportions)
    assert r_creature.is_valid is True
    assert r_creature.review_status == "PASSED"

    # 6. Hybrid Character
    g_hyb, garments_hyb = ProceduralCharacterFabricator.build_hybrid_character("Char_Golden_Hybrid")
    r_hyb = FabricationValidator.validate_fabrication(g_hyb, proportions, garments_hyb)
    assert r_hyb.is_valid is True
    assert r_hyb.review_status == "PASSED"

    # Full packaging of golden armored hero
    pkg = FabricatedCharacterPackage(
        asset_id="Char_Golden_Armored_Hero",
        archetype_name="ARMORED_HUMANOID",
        body_graph=g_arm,
        proportions=proportions,
        garments=garments_arm,
        validation_report=r_arm,
    )
    assert len(pkg.package_hash) == 64
    assert pkg.to_dict()["asset_id"] == "Char_Golden_Armored_Hero"


def test_non_negotiable_requirements_section_167_168():
    """
    Acceptance Test Sections 167 & 168:
    Non-negotiable requirement:
    - If primary anatomical components are missing (e.g. empty body graph), OR
    - If garment layers on the same target component are inverted (e.g. Underwear over Armor),
    the validator MUST report review_status = MANUAL_REVIEW_REQUIRED.
    """
    # 1. Missing primary forms violation
    empty_graph = SemanticBodyGraph(character_id="Char_Empty")
    rep_empty = FabricationValidator.validate_fabrication(empty_graph)
    assert rep_empty.is_valid is False
    assert rep_empty.review_status == "MANUAL_REVIEW_REQUIRED"
    assert any("no primary anatomical forms" in iss for iss in rep_empty.issues)

    # 2. Inverted garment layers violation
    valid_graph = SemanticBodyGraph.create_standard_humanoid_graph("Char_Inverted")
    armor_first = GarmentDefinition(
        garment_id="G_Armor",
        name="Heavy Plate",
        layer=GarmentLayer.ARMOR_PLATE,  # Layer 3
        target_body_components=["body.torso"],
    )
    underwear_over_armor = GarmentDefinition(
        garment_id="G_Underwear",
        name="Boxers Over Armor",
        layer=GarmentLayer.UNDERWEAR,    # Layer 0 (INVERSION!)
        target_body_components=["body.torso"],
    )

    rep_invert = FabricationValidator.validate_fabrication(
        valid_graph,
        garments=[armor_first, underwear_over_armor],
    )
    assert rep_invert.is_valid is False
    assert rep_invert.review_status == "MANUAL_REVIEW_REQUIRED"
    assert any("Inverted garment layers" in iss for iss in rep_invert.issues)
