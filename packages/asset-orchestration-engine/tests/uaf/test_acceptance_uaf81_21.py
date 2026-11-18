"""
UAF-81.21 Acceptance Tests (Sections 146, 147, 11, 12, 156, 171).
Verifies:
- Section 146 & 147: Final Acceptance Criteria (Generates and validates all 8 golden character archetypes:
  Human, Robot, Alien, Creature, Heavy Armor, Light Armor, Cloth Heavy, Cloth Light, plus Section 147 complex multi-layer character).
- Sections 11, 12, 147, 156: Non-Negotiable Requirements Test (Zero tolerance for anatomical violations,
  absolute machine-dependent paths, or zero/negative equipment clearance causing clipping; violations strictly flag MANUAL_REVIEW_REQUIRED).
"""

from uaf.character_creature.engine.creature_fabricator import CharacterCreatureFabricationPlatform
from uaf.character_creature.validation.creature_validator import CharacterCreatureValidator
from uaf.character_creature.models.definition import CharacterDefinition21, CharacterSpecies, AnatomicalLandmarks
from uaf.character_creature.models.equipment import BodyPartType, ModularEquipmentLayer, EquipmentLayerType
from uaf.character_creature.package.creature_package import CharacterCreaturePackage


def test_final_character_creature_acceptance_section_146_147():
    """
    Acceptance Test Sections 146 & 147:
    Synthesizes and validates all 8 golden character archetypes plus complex multi-layer character.
    """
    builders = [
        ("Char_Golden_Human", CharacterCreatureFabricationPlatform.build_human_character),
        ("Char_Golden_Robot", CharacterCreatureFabricationPlatform.build_robot_character),
        ("Char_Golden_Alien", CharacterCreatureFabricationPlatform.build_alien_character),
        ("Char_Golden_Creature", CharacterCreatureFabricationPlatform.build_creature_character),
        ("Char_Golden_HeavyArmor", CharacterCreatureFabricationPlatform.build_heavy_armor_character),
        ("Char_Golden_LightArmor", CharacterCreatureFabricationPlatform.build_light_armor_character),
        ("Char_Golden_ClothHeavy", CharacterCreatureFabricationPlatform.build_cloth_heavy_character),
        ("Char_Golden_ClothLight", CharacterCreatureFabricationPlatform.build_cloth_light_character),
        ("Char_Golden_Complex", CharacterCreatureFabricationPlatform.build_complex_multilayer_character),
    ]

    for asset_id, builder_fn in builders:
        char_def, parts, layers, skel_ref = builder_fn(asset_id)
        assert len(parts) >= 5
        assert len(layers) >= 1

        report = CharacterCreatureValidator.validate_character(char_def, parts, layers, skel_ref)
        assert report.is_valid is True, f"Failed for {asset_id}: {report.issues}"
        assert report.review_status == "PASSED"
        assert report.quality_score.aggregate_score >= 0.85

        pkg = CharacterCreaturePackage(
            asset_id=asset_id,
            character_def=char_def,
            body_parts=parts,
            equipment_layers=layers,
            skeleton_ref=skel_ref,
            validation_report=report,
        )
        assert len(pkg.package_hash) == 64
        assert pkg.to_dict()["asset_id"] == asset_id


def test_non_negotiable_requirements_section_11_12_147_156():
    """
    Acceptance Test Sections 11, 12, 147, 156:
    Non-negotiable requirements:
    1. Section 11 & 12: Height outside [50cm, 500cm] strictly fails.
    2. Section 156: Absolute machine-dependent skeleton paths strictly fails.
    3. Section 147: Non-body equipment layer with clearance <= 0mm (causing mesh penetration/clipping) strictly fails.
    Any violation strictly triggers review_status = MANUAL_REVIEW_REQUIRED.
    """
    char_def, parts, layers, skel_ref = CharacterCreatureFabricationPlatform.build_human_character("Char_Fault_Test")

    # 1. Section 11 & 12 violation: Anatomical height 10cm (<50cm minimum)
    bad_char_anat = CharacterDefinition21("Char_Tiny", CharacterSpecies.HUMAN, height_cm=10.0)
    rep_anat = CharacterCreatureValidator.validate_character(bad_char_anat, parts, layers, skel_ref)
    assert rep_anat.is_valid is False
    assert rep_anat.review_status == "MANUAL_REVIEW_REQUIRED"
    assert any("outside anatomical bounds" in iss for iss in rep_anat.issues)

    # 2. Section 156 violation: Absolute machine path in skeleton reference
    bad_skel_path = "C:\\Engine\\Content\\Characters\\Skeletons\\SKEL_Human.uasset"
    rep_skel = CharacterCreatureValidator.validate_character(char_def, parts, layers, bad_skel_path)
    assert rep_skel.is_valid is False
    assert rep_skel.review_status == "MANUAL_REVIEW_REQUIRED"
    assert any("machine-dependent skeleton reference" in iss for iss in rep_skel.issues)

    # 3. Section 147 violation: Armor layer with 0.0mm clearance (causes z-fighting/clipping with shirt)
    bad_layers_clipping = [
        ModularEquipmentLayer("Layer_Body", EquipmentLayerType.BODY, False, 0.0),
        ModularEquipmentLayer("Layer_Shirt", EquipmentLayerType.SHIRT, False, 2.0),
        ModularEquipmentLayer("Layer_ArmorVest", EquipmentLayerType.ARMOR_CHEST, True, 0.0),  # VIOLATION: 0.0mm clearance on armor!
    ]
    rep_clip = CharacterCreatureValidator.validate_character(char_def, parts, bad_layers_clipping, skel_ref)
    assert rep_clip.is_valid is False
    assert rep_clip.review_status == "MANUAL_REVIEW_REQUIRED"
    assert any("non-positive clearance" in iss for iss in rep_clip.issues)
