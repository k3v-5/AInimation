"""
Tests for Progression, Leveling, Skill Trees, and Abilities (UAF-81.58 Sections 141-155, 187).
"""
import pytest
from src.uaf.universal_gameplay.models.definition import (
    ProgressionProfile,
    SkillNode,
    SkillTree,
    AbilityDefinition,
    AbilityCost,
    EntityType,
    GameplayCommand,
    GameplayCommandType,
    CommandFailureCode,
    GameplayState,
)
from src.uaf.universal_gameplay.engine.universal_gameplay_fabricator import (
    UniversalGameplayFabricator,
)


def test_progression_profile_defaults():
    profile = ProgressionProfile(entity_id="PLAYER_1")
    assert profile.entity_id == "PLAYER_1"
    assert profile.current_level == 1
    assert profile.current_xp == 0
    assert profile.xp_for_next_level == 100
    assert profile.skill_points == 0
    assert profile.attribute_points == 0


def test_progression_add_xp_without_level_up():
    profile = ProgressionProfile(entity_id="PLAYER_1")
    leveled = profile.add_xp(50)
    assert leveled is False
    assert profile.current_xp == 50
    assert profile.current_level == 1
    assert profile.skill_points == 0


def test_progression_single_level_up():
    profile = ProgressionProfile(entity_id="PLAYER_1")
    leveled = profile.add_xp(120)
    assert leveled is True
    assert profile.current_level == 2
    assert profile.current_xp == 20
    assert profile.skill_points == 1
    assert profile.attribute_points == 2
    assert profile.xp_for_next_level == 150  # int(100 * 1.5)


def test_progression_multi_level_up():
    profile = ProgressionProfile(entity_id="PLAYER_1")
    # Level 1 requires 100 XP -> Level 2 requires 150 XP -> Total 250 XP for level 3
    leveled = profile.add_xp(270)
    assert leveled is True
    assert profile.current_level == 3
    assert profile.current_xp == 20
    assert profile.skill_points == 2
    assert profile.attribute_points == 4


def test_skill_node_initialization():
    node = SkillNode(skill_id="fireball", name="Fireball", max_rank=3, current_rank=0)
    assert node.skill_id == "fireball"
    assert node.max_rank == 3
    assert node.current_rank == 0
    assert node.prerequisites == []


def test_skill_tree_assembly():
    tree = SkillTree(tree_id="tree_magic", name="Elemental Magic")
    tree.skills["fireball"] = SkillNode("fireball", "Fireball", max_rank=3)
    tree.skills["pyroblast"] = SkillNode("pyroblast", "Pyroblast", max_rank=1, prerequisites=["fireball"])
    assert tree.tree_id == "tree_magic"
    assert len(tree.skills) == 2
    assert tree.skills["pyroblast"].prerequisites == ["fireball"]


def test_learn_skill_success():
    state = GameplayState("SIM_PROG")
    player = UniversalGameplayFabricator.spawn_entity("HERO", EntityType.PLAYER)
    player.progression.skill_points = 1
    state.entities[player.entity_id] = player

    tree = SkillTree("TREE_COMBAT", "Combat")
    tree.skills["SLASH"] = SkillNode("SLASH", "Heavy Slash", max_rank=3)
    state.skill_trees[tree.tree_id] = tree

    cmd = GameplayCommand(
        command_id="cmd_learn",
        source=player.entity_id,
        target="SLASH",
        command_type=GameplayCommandType.LEARN_SKILL,
        payload={"tree_id": "TREE_COMBAT", "skill_id": "SLASH"},
    )
    res = UniversalGameplayFabricator.execute_command(state, cmd)
    assert res.success
    assert tree.skills["SLASH"].current_rank == 1
    assert player.progression.skill_points == 0


def test_learn_skill_max_rank_cap():
    state = GameplayState("SIM_PROG")
    player = UniversalGameplayFabricator.spawn_entity("HERO", EntityType.PLAYER)
    player.progression.skill_points = 5
    state.entities[player.entity_id] = player

    tree = SkillTree("TREE_COMBAT", "Combat")
    tree.skills["SLASH"] = SkillNode("SLASH", "Heavy Slash", max_rank=1, current_rank=1)
    state.skill_trees[tree.tree_id] = tree

    cmd = GameplayCommand(
        command_id="cmd_learn_max",
        source=player.entity_id,
        target="SLASH",
        command_type=GameplayCommandType.LEARN_SKILL,
        payload={"tree_id": "TREE_COMBAT", "skill_id": "SLASH"},
    )
    res = UniversalGameplayFabricator.execute_command(state, cmd)
    assert not res.success
    assert res.failure_code == CommandFailureCode.CONDITION_FAILED
    assert "already max rank" in res.message


def test_learn_skill_no_points():
    state = GameplayState("SIM_PROG")
    player = UniversalGameplayFabricator.spawn_entity("HERO", EntityType.PLAYER)
    player.progression.skill_points = 0
    state.entities[player.entity_id] = player

    tree = SkillTree("TREE_COMBAT", "Combat")
    tree.skills["SLASH"] = SkillNode("SLASH", "Heavy Slash", max_rank=3)
    state.skill_trees[tree.tree_id] = tree

    cmd = GameplayCommand(
        command_id="cmd_learn_fail",
        source=player.entity_id,
        target="SLASH",
        command_type=GameplayCommandType.LEARN_SKILL,
        payload={"tree_id": "TREE_COMBAT", "skill_id": "SLASH"},
    )
    res = UniversalGameplayFabricator.execute_command(state, cmd)
    assert not res.success
    assert res.failure_code == CommandFailureCode.INSUFFICIENT_RESOURCE


def test_learn_skill_prerequisite_not_met():
    state = GameplayState("SIM_PROG")
    player = UniversalGameplayFabricator.spawn_entity("HERO", EntityType.PLAYER)
    player.progression.skill_points = 2
    state.entities[player.entity_id] = player

    tree = SkillTree("TREE_MAGIC", "Magic")
    tree.skills["TIER_1"] = SkillNode("TIER_1", "Spark", max_rank=1, current_rank=0)
    tree.skills["TIER_2"] = SkillNode("TIER_2", "Thunderbolt", max_rank=1, prerequisites=["TIER_1"])
    state.skill_trees[tree.tree_id] = tree

    cmd = GameplayCommand(
        command_id="cmd_learn_child",
        source=player.entity_id,
        target="TIER_2",
        command_type=GameplayCommandType.LEARN_SKILL,
        payload={"tree_id": "TREE_MAGIC", "skill_id": "TIER_2"},
    )
    res = UniversalGameplayFabricator.execute_command(state, cmd)
    assert not res.success
    assert res.failure_code == CommandFailureCode.CONDITION_FAILED


def test_learn_skill_prerequisite_met():
    state = GameplayState("SIM_PROG")
    player = UniversalGameplayFabricator.spawn_entity("HERO", EntityType.PLAYER)
    player.progression.skill_points = 2
    state.entities[player.entity_id] = player

    tree = SkillTree("TREE_MAGIC", "Magic")
    tree.skills["TIER_1"] = SkillNode("TIER_1", "Spark", max_rank=1, current_rank=1)
    tree.skills["TIER_2"] = SkillNode("TIER_2", "Thunderbolt", max_rank=1, prerequisites=["TIER_1"])
    state.skill_trees[tree.tree_id] = tree

    cmd = GameplayCommand(
        command_id="cmd_learn_child_ok",
        source=player.entity_id,
        target="TIER_2",
        command_type=GameplayCommandType.LEARN_SKILL,
        payload={"tree_id": "TREE_MAGIC", "skill_id": "TIER_2"},
    )
    res = UniversalGameplayFabricator.execute_command(state, cmd)
    assert res.success
    assert tree.skills["TIER_2"].current_rank == 1


def test_ability_use_success():
    state = GameplayState("SIM_PROG")
    player = UniversalGameplayFabricator.spawn_entity("HERO", EntityType.PLAYER)
    state.entities[player.entity_id] = player

    ability = AbilityDefinition(
        ability_id="AB_HEAL",
        name="Lesser Heal",
        cooldown=10.0,
        current_cooldown=0.0,
        effect_id="REGEN_BUFF",
    )
    state.abilities[ability.ability_id] = ability

    cmd = GameplayCommand(
        command_id="cmd_heal",
        source=player.entity_id,
        target=ability.ability_id,
        command_type=GameplayCommandType.USE_ABILITY,
        payload={"ability_id": ability.ability_id},
    )
    res = UniversalGameplayFabricator.execute_command(state, cmd)
    assert res.success
    assert ability.current_cooldown == 10.0
    assert len(player.active_effects) == 1
    assert "REGEN_BUFF" in player.active_effects[0].effect_id


def test_ability_use_cooldown_active():
    state = GameplayState("SIM_PROG")
    player = UniversalGameplayFabricator.spawn_entity("HERO", EntityType.PLAYER)
    state.entities[player.entity_id] = player

    ability = AbilityDefinition(
        ability_id="AB_FIRE",
        name="Fireball",
        cooldown=8.0,
        current_cooldown=4.5,
    )
    state.abilities[ability.ability_id] = ability

    cmd = GameplayCommand(
        command_id="cmd_fire_cd",
        source=player.entity_id,
        target=ability.ability_id,
        command_type=GameplayCommandType.USE_ABILITY,
        payload={"ability_id": ability.ability_id},
    )
    res = UniversalGameplayFabricator.execute_command(state, cmd)
    assert not res.success
    assert res.failure_code == CommandFailureCode.COOLDOWN_ACTIVE
