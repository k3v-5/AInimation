"""
Tests for Behavior Tree System (UAF-81.57 Sections 51-56, 226).
"""

import pytest
from uaf.universal_ai import (
    BTNodeType,
    BTNodeStatus,
    BTAbortMode,
    BehaviorNode,
    BehaviorTree,
    UniversalAIFabricator,
)


def test_bt_node_types_enum():
    types = {t.value for t in BTNodeType}
    expected = {
        "SEQUENCE",
        "SELECTOR",
        "PARALLEL",
        "DECORATOR",
        "CONDITION",
        "ACTION",
        "WAIT",
        "REPEAT",
        "RANDOM_SELECTOR",
        "UTILITY_SELECTOR",
    }
    assert types == expected


def test_bt_node_status_enum():
    statuses = {s.value for s in BTNodeStatus}
    expected = {"RUNNING", "SUCCESS", "FAILURE", "ABORTED"}
    assert statuses == expected


def test_bt_abort_mode_enum():
    modes = {m.value for m in BTAbortMode}
    expected = {"SELF", "LOWER_PRIORITY", "BOTH", "NONE"}
    assert modes == expected


def test_bt_action_node_success():
    tree = BehaviorTree(
        tree_id="BT_ACTION",
        root_node_id="ACT_01",
        nodes={
            "ACT_01": BehaviorNode(
                node_id="ACT_01",
                node_type=BTNodeType.ACTION,
                action_name="do_work",
            )
        },
    )
    context = {"do_work": lambda: BTNodeStatus.SUCCESS}
    res = UniversalAIFabricator.tick_behavior_tree(tree, "ACT_01", context)
    assert res == BTNodeStatus.SUCCESS


def test_bt_action_node_failure():
    tree = BehaviorTree(
        tree_id="BT_FAIL",
        root_node_id="ACT_FAIL",
        nodes={
            "ACT_FAIL": BehaviorNode(
                node_id="ACT_FAIL",
                node_type=BTNodeType.ACTION,
                action_name="fail_task",
            )
        },
    )
    context = {"fail_task": lambda: BTNodeStatus.FAILURE}
    res = UniversalAIFabricator.tick_behavior_tree(tree, "ACT_FAIL", context)
    assert res == BTNodeStatus.FAILURE


def test_bt_condition_node():
    tree = BehaviorTree(
        tree_id="BT_COND",
        root_node_id="COND_01",
        nodes={
            "COND_01": BehaviorNode(
                node_id="COND_01",
                node_type=BTNodeType.CONDITION,
                condition_name="has_ammo",
            )
        },
    )
    res_true = UniversalAIFabricator.tick_behavior_tree(tree, "COND_01", {"has_ammo": True})
    assert res_true == BTNodeStatus.SUCCESS

    res_false = UniversalAIFabricator.tick_behavior_tree(tree, "COND_01", {"has_ammo": False})
    assert res_false == BTNodeStatus.FAILURE


def test_bt_sequence_success():
    tree = BehaviorTree(
        tree_id="BT_SEQ",
        root_node_id="ROOT_SEQ",
        nodes={
            "ROOT_SEQ": BehaviorNode(
                node_id="ROOT_SEQ",
                node_type=BTNodeType.SEQUENCE,
                children=["STEP_1", "STEP_2"],
            ),
            "STEP_1": BehaviorNode(
                node_id="STEP_1",
                node_type=BTNodeType.ACTION,
                action_name="step_one",
            ),
            "STEP_2": BehaviorNode(
                node_id="STEP_2",
                node_type=BTNodeType.ACTION,
                action_name="step_two",
            ),
        },
    )
    executed = []
    context = {
        "step_one": lambda: (executed.append(1) or BTNodeStatus.SUCCESS),
        "step_two": lambda: (executed.append(2) or BTNodeStatus.SUCCESS),
    }
    res = UniversalAIFabricator.tick_behavior_tree(tree, "ROOT_SEQ", context)
    assert res == BTNodeStatus.SUCCESS
    assert executed == [1, 2]


def test_bt_sequence_failure_short_circuit():
    tree = BehaviorTree(
        tree_id="BT_SEQ_FAIL",
        root_node_id="ROOT_SEQ",
        nodes={
            "ROOT_SEQ": BehaviorNode(
                node_id="ROOT_SEQ",
                node_type=BTNodeType.SEQUENCE,
                children=["FAIL_FIRST", "NEVER_REACHED"],
            ),
            "FAIL_FIRST": BehaviorNode(
                node_id="FAIL_FIRST",
                node_type=BTNodeType.ACTION,
                action_name="fail_fn",
            ),
            "NEVER_REACHED": BehaviorNode(
                node_id="NEVER_REACHED",
                node_type=BTNodeType.ACTION,
                action_name="reached_fn",
            ),
        },
    )
    executed = []
    context = {
        "fail_fn": lambda: (executed.append("failed") or BTNodeStatus.FAILURE),
        "reached_fn": lambda: (executed.append("reached") or BTNodeStatus.SUCCESS),
    }
    res = UniversalAIFabricator.tick_behavior_tree(tree, "ROOT_SEQ", context)
    assert res == BTNodeStatus.FAILURE
    assert executed == ["failed"]


def test_bt_selector_fallback():
    tree = BehaviorTree(
        tree_id="BT_SEL",
        root_node_id="ROOT_SEL",
        nodes={
            "ROOT_SEL": BehaviorNode(
                node_id="ROOT_SEL",
                node_type=BTNodeType.SELECTOR,
                children=["TRY_MELEE", "TRY_RANGED"],
            ),
            "TRY_MELEE": BehaviorNode(
                node_id="TRY_MELEE",
                node_type=BTNodeType.CONDITION,
                condition_name="can_melee",
            ),
            "TRY_RANGED": BehaviorNode(
                node_id="TRY_RANGED",
                node_type=BTNodeType.ACTION,
                action_name="fire_bow",
            ),
        },
    )
    context = {
        "can_melee": False,
        "fire_bow": lambda: BTNodeStatus.SUCCESS,
    }
    res = UniversalAIFabricator.tick_behavior_tree(tree, "ROOT_SEL", context)
    assert res == BTNodeStatus.SUCCESS


def test_bt_missing_node_returns_failure():
    tree = BehaviorTree(tree_id="BT_EMPTY", root_node_id="NON_EXISTENT")
    res = UniversalAIFabricator.tick_behavior_tree(tree, "NON_EXISTENT", {})
    assert res == BTNodeStatus.FAILURE
