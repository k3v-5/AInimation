"""
Tests for Gameplay Triggers and Spatial/State Activations (UAF-81.58 Sections 156-165, 187).
"""
import pytest
from src.uaf.universal_gameplay.models.definition import (
    TriggerType,
    GameplayTrigger,
    InteractionCondition,
    InteractionConditionType,
    InteractionAction,
    InteractionActionType,
    GameplayState,
)


def test_trigger_type_enum():
    types = {t.value for t in TriggerType}
    expected = {
        "ON_ENTER_AREA",
        "ON_EXIT_AREA",
        "ON_HEALTH_BELOW",
        "ON_INTERACTION",
        "ON_TIME",
        "ON_CUSTOM",
    }
    assert types == expected


def test_gameplay_trigger_creation():
    trigger = GameplayTrigger(
        trigger_id="trig_boss_room",
        trigger_type=TriggerType.ON_ENTER_AREA,
        is_active=True,
    )
    assert trigger.trigger_id == "trig_boss_room"
    assert trigger.trigger_type == TriggerType.ON_ENTER_AREA
    assert trigger.is_active is True
    assert len(trigger.conditions) == 0
    assert len(trigger.actions) == 0


def test_trigger_enter_area():
    trig = GameplayTrigger(
        trigger_id="trig_dungeon_entry",
        trigger_type=TriggerType.ON_ENTER_AREA,
    )
    assert trig.trigger_type == TriggerType.ON_ENTER_AREA


def test_trigger_exit_area():
    trig = GameplayTrigger(
        trigger_id="trig_safe_zone_exit",
        trigger_type=TriggerType.ON_EXIT_AREA,
    )
    assert trig.trigger_type == TriggerType.ON_EXIT_AREA


def test_trigger_health_below():
    trig = GameplayTrigger(
        trigger_id="trig_boss_enrage",
        trigger_type=TriggerType.ON_HEALTH_BELOW,
    )
    assert trig.trigger_type == TriggerType.ON_HEALTH_BELOW


def test_trigger_interaction():
    trig = GameplayTrigger(
        trigger_id="trig_chest_open",
        trigger_type=TriggerType.ON_INTERACTION,
    )
    assert trig.trigger_type == TriggerType.ON_INTERACTION


def test_trigger_time():
    trig = GameplayTrigger(
        trigger_id="trig_nightfall",
        trigger_type=TriggerType.ON_TIME,
    )
    assert trig.trigger_type == TriggerType.ON_TIME


def test_trigger_with_conditions_and_actions():
    cond = InteractionCondition(
        condition_type=InteractionConditionType.HAS_TAG,
        target_key="VIP",
        expected_value=True,
    )
    act = InteractionAction(
        action_type=InteractionActionType.TRIGGER_EVENT,
        payload={"event_name": "OPEN_SECRET_DOOR"},
    )
    trig = GameplayTrigger(
        trigger_id="trig_vip_door",
        trigger_type=TriggerType.ON_ENTER_AREA,
        conditions=[cond],
        actions=[act],
    )
    assert len(trig.conditions) == 1
    assert len(trig.actions) == 1
    assert trig.conditions[0].target_key == "VIP"
    assert trig.actions[0].payload["event_name"] == "OPEN_SECRET_DOOR"


def test_trigger_activation_deactivation():
    trig = GameplayTrigger(
        trigger_id="trig_trap",
        trigger_type=TriggerType.ON_ENTER_AREA,
        is_active=True,
    )
    assert trig.is_active is True
    # Disarm trap
    trig.is_active = False
    assert trig.is_active is False


def test_triggers_in_gameplay_state():
    state = GameplayState("SIM_TRIGGERS")
    t1 = GameplayTrigger("t_gate", TriggerType.ON_ENTER_AREA)
    t2 = GameplayTrigger("t_ambush", TriggerType.ON_TIME)
    state.triggers[t1.trigger_id] = t1
    state.triggers[t2.trigger_id] = t2

    assert len(state.triggers) == 2
    assert "t_gate" in state.triggers
    assert "t_ambush" in state.triggers
