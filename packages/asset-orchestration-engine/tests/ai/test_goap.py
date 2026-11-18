"""
Tests for Goal-Oriented Action Planning (GOAP) System (UAF-81.57 Sections 58-63, 226).
"""

import pytest
from uaf.universal_ai import (
    WorldFact,
    GOAPAction,
    GOAPGoal,
    ActionPlan,
    UniversalAIFabricator,
)


def test_world_fact():
    fact = WorldFact(key="has_weapon", value=True)
    assert fact.key == "has_weapon"
    assert fact.value is True


def test_goap_action_creation():
    act = GOAPAction(
        action_id="PICKUP_AXE",
        preconditions={"axe_nearby": True},
        effects={"has_axe": True},
        cost=2.0,
        duration=1.5,
    )
    assert act.action_id == "PICKUP_AXE"
    assert act.preconditions == {"axe_nearby": True}
    assert act.effects == {"has_axe": True}
    assert act.cost == 2.0


def test_goap_goal_creation():
    goal = GOAPGoal(
        goal_id="CHOP_TREE",
        desired_state={"has_wood": True},
        priority=2.5,
    )
    assert goal.goal_id == "CHOP_TREE"
    assert goal.desired_state == {"has_wood": True}
    assert goal.priority == 2.5


def test_goap_plan_already_satisfied():
    goal = GOAPGoal(goal_id="SURVIVE", desired_state={"is_safe": True})
    current_state = {"is_safe": True}
    plan = UniversalAIFabricator.plan_goap([], current_state, goal)

    assert plan.is_valid is True
    assert len(plan.actions) == 0
    assert plan.total_cost == 0.0


def test_goap_single_step_plan():
    act = GOAPAction(
        action_id="DRAW_SWORD",
        preconditions={"armed": False},
        effects={"armed": True},
        cost=1.0,
    )
    goal = GOAPGoal(goal_id="GET_ARMED", desired_state={"armed": True})
    current_state = {"armed": False}

    plan = UniversalAIFabricator.plan_goap([act], current_state, goal)
    assert plan.is_valid is True
    assert len(plan.actions) == 1
    assert plan.actions[0].action_id == "DRAW_SWORD"
    assert plan.total_cost == 1.0


def test_goap_multi_step_plan():
    act1 = GOAPAction(
        action_id="CHOP_WOOD",
        preconditions={"near_tree": True},
        effects={"has_wood": True},
        cost=2.0,
    )
    act2 = GOAPAction(
        action_id="BUILD_SHELTER",
        preconditions={"has_wood": True},
        effects={"has_shelter": True},
        cost=5.0,
    )
    goal = GOAPGoal(goal_id="SHELTER", desired_state={"has_shelter": True})
    current_state = {"near_tree": True, "has_wood": False}

    plan = UniversalAIFabricator.plan_goap([act1, act2], current_state, goal)
    assert plan.is_valid is True
    assert len(plan.actions) == 2
    assert [a.action_id for a in plan.actions] == ["CHOP_WOOD", "BUILD_SHELTER"]
    assert plan.total_cost == 7.0


def test_goap_cost_optimization():
    # Two actions that achieve {"target_dead": True}
    # One is cheap (MELEE, cost 2), one is expensive (MAGIC, cost 10)
    act_magic = GOAPAction(
        action_id="CAST_SPELL",
        preconditions={"in_combat": True},
        effects={"target_dead": True},
        cost=10.0,
    )
    act_melee = GOAPAction(
        action_id="SLASH_SWORD",
        preconditions={"in_combat": True},
        effects={"target_dead": True},
        cost=2.0,
    )
    goal = GOAPGoal(goal_id="ELIMINATE", desired_state={"target_dead": True})
    current_state = {"in_combat": True}

    plan = UniversalAIFabricator.plan_goap([act_magic, act_melee], current_state, goal)
    assert plan.is_valid is True
    assert len(plan.actions) == 1
    assert plan.actions[0].action_id == "SLASH_SWORD"
    assert plan.total_cost == 2.0


def test_goap_unachievable_goal():
    act = GOAPAction(
        action_id="FARM",
        preconditions={"has_hoe": True},
        effects={"has_food": True},
        cost=3.0,
    )
    # Agent does not have hoe, and no action provides hoe
    goal = GOAPGoal(goal_id="EAT", desired_state={"has_food": True})
    current_state = {"has_hoe": False}

    plan = UniversalAIFabricator.plan_goap([act], current_state, goal)
    assert plan.is_valid is False
    assert len(plan.actions) == 0
