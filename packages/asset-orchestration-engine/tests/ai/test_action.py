"""
Tests for Action System (UAF-81.57 Sections 64-68, 226).
"""

import pytest
from uaf.universal_ai import (
    AIActionType,
    AIActionState,
    AIAction,
    AIAgent,
    AgentProfile,
    SimulationDefinition,
    UniversalAIFabricator,
)


def test_action_type_enum():
    types = {t.value for t in AIActionType}
    expected = {
        "MOVE",
        "LOOK",
        "WAIT",
        "INTERACT",
        "PICKUP",
        "DROP",
        "USE",
        "TALK",
        "ATTACK",
        "DEFEND",
        "FLEE",
        "FOLLOW",
        "GUARD",
        "SEARCH",
        "SLEEP",
        "EAT",
        "DRINK",
        "WORK",
        "CUSTOM",
    }
    assert types == expected


def test_action_state_enum():
    states = {s.value for s in AIActionState}
    expected = {"QUEUED", "RUNNING", "SUCCESS", "FAILED", "CANCELLED", "INTERRUPTED"}
    assert states == expected


def test_action_creation():
    act = AIAction(
        action_id="ACT_001",
        action_type=AIActionType.INTERACT,
        target_id="CHEST_01",
        target_pos=(100.0, 50.0, 0.0),
        priority=3,
        duration=2.5,
    )
    assert act.action_id == "ACT_001"
    assert act.action_type == AIActionType.INTERACT
    assert act.target_id == "CHEST_01"
    assert act.target_pos == (100.0, 50.0, 0.0)
    assert act.priority == 3
    assert act.state == AIActionState.QUEUED
    assert act.duration == 2.5
    assert act.elapsed == 0.0


def test_action_to_dict():
    act = AIAction(
        action_id="ACT_MOVE",
        action_type=AIActionType.MOVE,
        target_id="WAYPOINT_A",
        priority=2,
        state=AIActionState.RUNNING,
    )
    d = act.to_dict()
    assert d["action_id"] == "ACT_MOVE"
    assert d["action_type"] == "MOVE"
    assert d["target_id"] == "WAYPOINT_A"
    assert d["priority"] == 2
    assert d["state"] == "RUNNING"


def test_action_progress_and_completion():
    prof = AgentProfile(profile_id="P_ACT")
    agent = AIAgent(agent_id="AGENT_ACT", profile=prof)
    action = AIAction(
        action_id="ACT_WAIT",
        action_type=AIActionType.WAIT,
        duration=0.1,
        state=AIActionState.RUNNING,
    )
    agent.current_action_obj = action
    agent.state.current_action = "WAIT"

    sim = SimulationDefinition(simulation_id="SIM_ACT")
    sim.agents = [agent]

    # Tick 1: dt = 0.05 -> elapsed = 0.05 < 0.1
    UniversalAIFabricator.execute_simulation_tick(sim, dt=0.05)
    assert action.state == AIActionState.RUNNING
    assert round(action.elapsed, 3) == 0.05

    # Tick 2: dt = 0.06 -> elapsed = 0.11 >= 0.1 -> SUCCESS
    UniversalAIFabricator.execute_simulation_tick(sim, dt=0.06)
    assert action.state == AIActionState.SUCCESS
    assert agent.state.current_action == "IDLE"


def test_action_interruption():
    act = AIAction(
        action_id="ACT_INTERRUPT",
        action_type=AIActionType.WORK,
        state=AIActionState.RUNNING,
    )
    assert act.state == AIActionState.RUNNING
    act.state = AIActionState.INTERRUPTED
    assert act.state == AIActionState.INTERRUPTED


def test_action_cancellation():
    act = AIAction(
        action_id="ACT_CANCEL",
        action_type=AIActionType.SLEEP,
        state=AIActionState.QUEUED,
    )
    assert act.state == AIActionState.QUEUED
    act.state = AIActionState.CANCELLED
    assert act.state == AIActionState.CANCELLED
