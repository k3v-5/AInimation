"""
Tests for Finite State Machine (FSM) System (UAF-81.57 Sections 47-52, 226).
"""

import pytest
from uaf.universal_ai import (
    StateDefinition,
    StateTransition,
    FSMDefinition,
    AIAgent,
    AgentProfile,
    AgentState,
    AgentLifecycleState,
    SimulationDefinition,
    UniversalAIFabricator,
)


def test_fsm_definition():
    s_idle = StateDefinition(state_id="IDLE", name="Idle State")
    s_patrol = StateDefinition(state_id="PATROL", name="Patrol State")
    trans = StateTransition(
        source_state="IDLE",
        target_state="PATROL",
        condition="patrol_timer_elapsed",
        priority=1,
    )
    fsm = FSMDefinition(
        fsm_id="FSM_GUARD",
        initial_state="IDLE",
        states={"IDLE": s_idle, "PATROL": s_patrol},
        transitions=[trans],
    )
    assert fsm.fsm_id == "FSM_GUARD"
    assert fsm.initial_state == "IDLE"
    assert len(fsm.states) == 2
    assert len(fsm.transitions) == 1


def test_fsm_initial_state():
    fsm = FSMDefinition(
        fsm_id="FSM_BASIC",
        initial_state="RESTING",
        states={"RESTING": StateDefinition("RESTING", "Rest")},
    )
    assert fsm.initial_state == "RESTING"


def test_fsm_transition_true_condition():
    fsm = FSMDefinition(
        fsm_id="FSM_COMBAT",
        initial_state="IDLE",
        states={
            "IDLE": StateDefinition("IDLE", "Idle"),
            "ATTACK": StateDefinition("ATTACK", "Attack"),
        },
        transitions=[
            StateTransition(source_state="IDLE", target_state="ATTACK", condition="enemy_in_range")
        ],
    )
    next_st = UniversalAIFabricator.evaluate_fsm(fsm, "IDLE", {"enemy_in_range": True})
    assert next_st == "ATTACK"


def test_fsm_transition_false_condition():
    fsm = FSMDefinition(
        fsm_id="FSM_COMBAT",
        initial_state="IDLE",
        states={
            "IDLE": StateDefinition("IDLE", "Idle"),
            "ATTACK": StateDefinition("ATTACK", "Attack"),
        },
        transitions=[
            StateTransition(source_state="IDLE", target_state="ATTACK", condition="enemy_in_range")
        ],
    )
    next_st = UniversalAIFabricator.evaluate_fsm(fsm, "IDLE", {"enemy_in_range": False})
    assert next_st == "IDLE"


def test_fsm_unknown_transition():
    fsm = FSMDefinition(
        fsm_id="FSM_WANDER",
        initial_state="WANDER",
        states={"WANDER": StateDefinition("WANDER", "Wandering")},
        transitions=[],
    )
    next_st = UniversalAIFabricator.evaluate_fsm(fsm, "WANDER", {"any_condition": True})
    assert next_st == "WANDER"


def test_fsm_simulation_tick_integration():
    fsm = FSMDefinition(
        fsm_id="FSM_HEALTH",
        initial_state="PATROL",
        states={
            "PATROL": StateDefinition("PATROL", "Patrol"),
            "RETREAT": StateDefinition("RETREAT", "Retreat"),
        },
        transitions=[
            StateTransition(source_state="PATROL", target_state="RETREAT", condition="low_health")
        ],
    )
    prof = AgentProfile(profile_id="P_GUARD")
    agent = AIAgent(
        agent_id="GUARD_FSM",
        profile=prof,
        fsm=fsm,
        current_fsm_state="PATROL",
    )
    agent.state.health = 20.0  # Below 30.0 threshold

    sim = SimulationDefinition(simulation_id="SIM_FSM")
    sim.agents = [agent]

    UniversalAIFabricator.execute_simulation_tick(sim, dt=0.033)
    assert agent.current_fsm_state == "RETREAT"
