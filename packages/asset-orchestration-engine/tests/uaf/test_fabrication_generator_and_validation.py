"""
Tests for ProceduralCharacterFabricator, FabricationValidator, and FabricatedCharacterPackage.
UAF-81.10 Sections 26, 30, 141, 156, 165.
"""

from uaf.fabrication.generator.character_fabricator import (
    ProceduralCharacterFabricator,
    TopologyStrategyType,
    FabricationQuality,
)
from uaf.fabrication.validation.fabrication_validator import (
    FabricationValidator,
    FabricationQualityScore,
)
from uaf.fabrication.anatomy.proportions import ProportionProfile
from uaf.fabrication.package.fabricated_package import FabricatedCharacterPackage


def test_fabricator_archetypes_and_no_global_remesh():
    # 1. Organic
    organic = ProceduralCharacterFabricator.build_organic_humanoid("Char_Human_Naked")
    assert len(organic.components) >= 7

    # 2. Clothed
    clothed_graph, garments = ProceduralCharacterFabricator.build_clothed_humanoid("Char_Civilian")
    assert len(garments) == 2

    # 3. Armored
    armored_graph, armor_garments = ProceduralCharacterFabricator.build_armored_humanoid("Char_Knight")
    assert any(g.is_rigid for g in armor_garments)

    # 4. Mechanical
    mech = ProceduralCharacterFabricator.build_mechanical_character("Robot_Enforcer")
    assert all(c.is_rigid for c in mech.components.values())

    # 5. Creature
    creature = ProceduralCharacterFabricator.build_creature("Beast_Hound")
    assert "creature.tail" in creature.components

    # 6. Hybrid
    hybrid_graph, hybrid_garments = ProceduralCharacterFabricator.build_hybrid_character("Cyborg_Commando")
    assert hybrid_graph.components["body.arm_R"].is_rigid is True


def test_fabrication_validator_passing_and_package():
    graph, garments = ProceduralCharacterFabricator.build_armored_humanoid("Char_Paladin")
    proportions = ProportionProfile.create_heroic_profile("Prop_Paladin")

    report = FabricationValidator.validate_fabrication(
        body_graph=graph,
        proportions=proportions,
        garments=garments,
    )

    assert report.is_valid is True
    assert report.review_status == "PASSED"
    assert report.quality_score.aggregate_score >= 0.85

    pkg = FabricatedCharacterPackage(
        asset_id="Char_Paladin_Hero",
        archetype_name="ARMORED_HUMANOID",
        body_graph=graph,
        proportions=proportions,
        garments=garments,
        validation_report=report,
    )

    assert len(pkg.package_hash) == 64
    data = pkg.to_dict()
    assert data["archetype_name"] == "ARMORED_HUMANOID"
    assert len(data["garments"]) == 2
