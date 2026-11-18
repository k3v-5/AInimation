"""
Comprehensive Failure, Edge Cases & Quality Gate Tests (UAF-81.57 Section 226).
Covers all 23+ required failure modes and quality gate assertions.
"""

import pytest
from uaf.universal_ai import (
    UniversalAIValidator,
    AIValidationReport,
    SimulationDefinition,
    AIAgent,
    AgentProfile,
    AgentState,
    AgentLifecycleState,
    FSMDefinition,
    StateDefinition,
    StateTransition,
    BehaviorTree,
    BehaviorNode,
    BTNodeType,
    SquadDefinition,
    UniversalAIFabricator,
)


def _make_valid_agent(agent_id="NPC_TEST") -> AIAgent:
    return UniversalAIFabricator.spawn_agent(agent_id, AgentProfile(f"PROF_{agent_id}"))


def test_fail_machine_path_c_drive():
    sim = SimulationDefinition("SIM_FAIL", agents=[_make_valid_agent()])
    report = UniversalAIValidator.validate_simulation(sim, export_path="C:/Unreal/Sim.uasset")
    assert report.is_valid is False
    assert report.quality_score == 0.0
    assert any("Machine-dependent path" in err for err in report.failed_checks)


def test_fail_machine_path_d_drive():
    sim = SimulationDefinition("SIM_FAIL", agents=[_make_valid_agent()])
    report = UniversalAIValidator.validate_simulation(sim, export_path="D:\\Assets\\Sim.uasset")
    assert report.is_valid is False
    assert report.quality_score == 0.0


def test_fail_machine_path_e_drive():
    sim = SimulationDefinition("SIM_FAIL", agents=[_make_valid_agent()])
    report = UniversalAIValidator.validate_simulation(sim, export_path="E:/Game/AI.uasset")
    assert report.is_valid is False
    assert report.quality_score == 0.0


def test_fail_machine_path_agent_id():
    agent = _make_valid_agent()
    agent.agent_id = "C:\\Windows\\System32\\agent.dll"
    sim = SimulationDefinition("SIM_FAIL", agents=[agent])
    report = UniversalAIValidator.validate_simulation(sim, export_path="/Game/AI/Sim.uasset")
    assert report.is_valid is False
    assert report.quality_score == 0.0


def test_fail_empty_simulation_agents():
    sim = SimulationDefinition("SIM_EMPTY", agents=[])
    report = UniversalAIValidator.validate_simulation(sim, export_path="/Game/AI/Sim.uasset")
    assert report.is_valid is False
    assert report.quality_score == 0.0
    assert any("0 agents" in err for err in report.failed_checks)


def test_fail_dead_agent_acting_idle():
    agent = _make_valid_agent()
    agent.lifecycle = AgentLifecycleState.DEAD
    agent.state.current_action = "IDLE"

    sim = SimulationDefinition("SIM_DEAD_ACT", agents=[agent])
    report = UniversalAIValidator.validate_simulation(sim, export_path="/Game/AI/Sim.uasset")
    assert report.is_valid is False
    assert report.quality_score == 0.0
    assert any("Dead agent" in err for err in report.failed_checks)


def test_fail_dead_agent_acting_patrol():
    agent = _make_valid_agent()
    agent.lifecycle = AgentLifecycleState.DEAD
    agent.state.current_action = "PATROL"

    sim = SimulationDefinition("SIM_DEAD_PATROL", agents=[agent])
    report = UniversalAIValidator.validate_simulation(sim, export_path="/Game/AI/Sim.uasset")
    assert report.is_valid is False
    assert report.quality_score == 0.0


def test_fail_dead_agent_acting_attack():
    agent = _make_valid_agent()
    agent.lifecycle = AgentLifecycleState.DEAD
    agent.state.current_action = "ATTACK"

    sim = SimulationDefinition("SIM_DEAD_ATK", agents=[agent])
    report = UniversalAIValidator.validate_simulation(sim, export_path="/Game/AI/Sim.uasset")
    assert report.is_valid is False
    assert report.quality_score == 0.0


def test_dead_agent_acting_dead_allowed():
    agent = _make_valid_agent()
    agent.lifecycle = AgentLifecycleState.DEAD
    agent.state.current_action = "DEAD"

    sim = SimulationDefinition("SIM_DEAD_OK", agents=[agent])
    report = UniversalAIValidator.validate_simulation(sim, export_path="/Game/AI/Sim.uasset")
    assert report.is_valid is True
    assert "CHECK_AGENT_LIFECYCLE_SANITY" in report.passed_checks


def test_fail_fsm_missing_initial_state():
    fsm = FSMDefinition(fsm_id="FSM_BAD", initial_state="MISSING_STATE", states={})
    agent = _make_valid_agent()
    agent.fsm = fsm

    sim = SimulationDefinition("SIM_FSM_BAD", agents=[agent])
    report = UniversalAIValidator.validate_simulation(sim, export_path="/Game/AI/Sim.uasset")
    assert report.is_valid is False
    assert any("FSM initial state" in err for err in report.failed_checks)


def test_fail_fsm_transition_missing_source_state():
    fsm = FSMDefinition(
        fsm_id="FSM_BAD_TRANS",
        initial_state="STATE_A",
        states={"STATE_A": StateDefinition("STATE_A", "A")},
        transitions=[StateTransition("MISSING_SRC", "STATE_A", "cond")],
    )
    agent = _make_valid_agent()
    agent.fsm = fsm

    sim = SimulationDefinition("SIM_FSM_SRC", agents=[agent])
    report = UniversalAIValidator.validate_simulation(sim, export_path="/Game/AI/Sim.uasset")
    assert report.is_valid is False
    assert any("FSM transition" in err for err in report.failed_checks)


def test_fail_fsm_transition_missing_target_state():
    fsm = FSMDefinition(
        fsm_id="FSM_BAD_TGT",
        initial_state="STATE_A",
        states={"STATE_A": StateDefinition("STATE_A", "A")},
        transitions=[StateTransition("STATE_A", "MISSING_TGT", "cond")],
    )
    agent = _make_valid_agent()
    agent.fsm = fsm

    sim = SimulationDefinition("SIM_FSM_TGT", agents=[agent])
    report = UniversalAIValidator.validate_simulation(sim, export_path="/Game/AI/Sim.uasset")
    assert report.is_valid is False
    assert any("FSM transition" in err for err in report.failed_checks)


def test_fail_bt_missing_root_node():
    bt = BehaviorTree(tree_id="BT_BAD", root_node_id="GHOST_ROOT", nodes={})
    agent = _make_valid_agent()
    agent.behavior_tree = bt

    sim = SimulationDefinition("SIM_BT_BAD", agents=[agent])
    report = UniversalAIValidator.validate_simulation(sim, export_path="/Game/AI/Sim.uasset")
    assert report.is_valid is False
    assert any("BT root node" in err for err in report.failed_checks)


def test_warning_negative_health():
    agent = _make_valid_agent()
    agent.state.health = -10.0

    sim = SimulationDefinition("SIM_NEG_HP", agents=[agent])
    report = UniversalAIValidator.validate_simulation(sim, export_path="/Game/AI/Sim.uasset")
    assert report.is_valid is True
    assert report.quality_score == 95.0
    assert any("negative health" in w for w in report.warnings)


def test_warning_negative_stamina():
    agent = _make_valid_agent()
    agent.state.stamina = -5.0

    sim = SimulationDefinition("SIM_NEG_STM", agents=[agent])
    report = UniversalAIValidator.validate_simulation(sim, export_path="/Game/AI/Sim.uasset")
    assert report.is_valid is True
    assert report.quality_score == 95.0
    assert any("negative health or stamina" in w for w in report.warnings)


def test_warning_squad_leader_not_in_simulation():
    agent = _make_valid_agent("MEMBER_1")
    squad = SquadDefinition(squad_id="SQ1", leader_id="GHOST_LEADER", member_ids=["MEMBER_1"])

    sim = SimulationDefinition("SIM_GHOST_LEAD", agents=[agent], squads=[squad])
    report = UniversalAIValidator.validate_simulation(sim, export_path="/Game/AI/Sim.uasset")
    assert report.is_valid is True
    assert report.quality_score == 90.0
    assert any("leader GHOST_LEADER not present" in w for w in report.warnings)


def test_quality_score_compounded_deductions():
    agent = _make_valid_agent("A1")
    agent.state.health = -1.0  # -5.0
    squad = SquadDefinition(squad_id="SQ1", leader_id="MISSING_LEAD")  # -10.0

    sim = SimulationDefinition("SIM_COMPOUND", agents=[agent], squads=[squad])
    report = UniversalAIValidator.validate_simulation(sim, export_path="/Game/AI/Sim.uasset")
    assert report.is_valid is True
    assert report.quality_score == 85.0


def test_quality_score_clamped_at_zero():
    agents = []
    for i in range(25):
        a = _make_valid_agent(f"NEG_{i}")
        a.state.health = -10.0  # 25 * 5 = 125 deductions
        agents.append(a)

    sim = SimulationDefinition("SIM_ZERO_SCORE", agents=agents)
    report = UniversalAIValidator.validate_simulation(sim, export_path="/Game/AI/Sim.uasset")
    assert report.is_valid is True
    assert report.quality_score == 0.0


def test_validation_report_to_dict():
    rep = AIValidationReport(
        is_valid=True,
        quality_score=92.5,
        passed_checks=["CHECK_A", "CHECK_B"],
        warnings=["WARN_1"],
    )
    d = rep.to_dict()
    assert d["is_valid"] is True
    assert d["quality_score"] == 92.5
    assert len(d["passed_checks"]) == 2
    assert len(d["warnings"]) == 1


def test_fail_utility_empty_actions_raises():
    with pytest.raises(ValueError):
        UniversalAIFabricator.evaluate_utility([], {})


def test_fail_golden_scenario_unknown_name_raises():
    with pytest.raises(ValueError):
        UniversalAIFabricator.create_golden_scenario("NON_EXISTENT_SCENARIO")


def test_pathfinding_all_obstacles_blocking():
    from uaf.universal_ai import DynamicObstacle
    obs1 = DynamicObstacle("O1", position=(500.0, 0.0, 0.0), radius=50.0)
    obs2 = DynamicObstacle("O2", position=(500.0, 50.0, 0.0), radius=50.0)

    res = UniversalAIFabricator.compute_path((0.0, 0.0, 0.0), (1000.0, 0.0, 0.0), obstacles=[obs1, obs2])
    assert len(res.waypoints) == 3


def test_crowd_deadlock_unmoving_agents():
    from uaf.universal_ai import CrowdAgent
    a1 = CrowdAgent("STUCK_1", position=(0.0, 0.0, 0.0), velocity=(0.0, 0.0, 0.0), desired_velocity=(100.0, 0.0, 0.0))
    a2 = CrowdAgent("STUCK_2", position=(1.0, 0.0, 0.0), velocity=(0.0, 0.0, 0.0), desired_velocity=(100.0, 0.0, 0.0))

    deadlocks = UniversalAIFabricator.detect_crowd_deadlocks([a1, a2])
    assert len(deadlocks) == 2


def test_fsm_no_matching_transition():
    fsm = FSMDefinition(
        fsm_id="FSM_STUCK",
        initial_state="IDLE",
        states={"IDLE": StateDefinition("IDLE", "Idle")},
        transitions=[StateTransition("IDLE", "ATTACK", "impossible_condition")],
    )
    res = UniversalAIFabricator.evaluate_fsm(fsm, "IDLE", {"impossible_condition": False})
    assert res == "IDLE"


def test_valid_simulation_quality_score_100():
    sim = UniversalAIFabricator.build_golden_idle_npc()
    report = UniversalAIValidator.validate_simulation(sim, export_path="/Game/AI/IdleSim.uasset")
    assert report.is_valid is True
    assert report.quality_score == 100.0
    assert len(report.failed_checks) == 0
    assert len(report.warnings) == 0
