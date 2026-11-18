"""
Determinism Tests for Universal AI System (UAF-81.57 Section 226).
Ensures 100% bitwise determinism across random streams, ticks, solvers, and packages.
"""

import pytest
from uaf.universal_ai import (
    AIRandomStream,
    SimulationDefinition,
    AIAgent,
    AgentProfile,
    AgentState,
    AgentType,
    FormationType,
    CoverPoint,
    UtilityAction,
    UtilityConsideration,
    UtilityCurveType,
    GOAPAction,
    GOAPGoal,
    AIQuery,
    AIQueryType,
    ProductionReadySimulation,
    UniversalAIFabricator,
)


def test_random_stream_determinism_same_seed():
    s1 = AIRandomStream(seed=12345)
    s2 = AIRandomStream(seed=12345)
    seq1 = [s1.next_float() for _ in range(20)]
    seq2 = [s2.next_float() for _ in range(20)]
    assert seq1 == seq2


def test_random_stream_divergence_different_seeds():
    s1 = AIRandomStream(seed=100)
    s2 = AIRandomStream(seed=200)
    seq1 = [s1.next_float() for _ in range(10)]
    seq2 = [s2.next_float() for _ in range(10)]
    assert seq1 != seq2


def test_random_stream_range_determinism():
    s1 = AIRandomStream(seed=777)
    s2 = AIRandomStream(seed=777)
    r1 = [s1.next_range(-10.0, 10.0) for _ in range(15)]
    r2 = [s2.next_range(-10.0, 10.0) for _ in range(15)]
    assert r1 == r2


def test_random_stream_int_determinism():
    s1 = AIRandomStream(seed=333)
    s2 = AIRandomStream(seed=333)
    i1 = [s1.next_int(1, 100) for _ in range(25)]
    i2 = [s2.next_int(1, 100) for _ in range(25)]
    assert i1 == i2


def test_simulation_hash_determinism():
    sim1 = UniversalAIFabricator.build_golden_patrol()
    sim2 = UniversalAIFabricator.build_golden_patrol()
    assert sim1.simulation_hash == sim2.simulation_hash


def test_simulation_hash_divergence_on_seed():
    sim1 = UniversalAIFabricator.create_golden_scenario(UniversalAIFabricator.GOLDEN_PATROL, seed=100)
    sim2 = UniversalAIFabricator.create_golden_scenario(UniversalAIFabricator.GOLDEN_PATROL, seed=200)
    assert sim1.simulation_hash != sim2.simulation_hash


def test_simulation_hash_divergence_on_agent_count():
    sim1 = UniversalAIFabricator.build_golden_idle_npc()
    sim2 = UniversalAIFabricator.build_golden_idle_npc()
    extra_agent = UniversalAIFabricator.spawn_agent("EXTRA", AgentProfile("P_EXTRA"))
    sim2.agents.append(extra_agent)
    assert sim1.simulation_hash != sim2.simulation_hash


def test_simulation_hash_divergence_on_tick():
    sim = UniversalAIFabricator.build_golden_idle_npc()
    hash_t0 = sim.simulation_hash
    UniversalAIFabricator.execute_simulation_tick(sim, dt=0.033)
    hash_t1 = sim.simulation_hash
    assert hash_t0 != hash_t1


def test_simulation_tick_determinism_movement():
    sim1 = UniversalAIFabricator.build_golden_idle_npc()
    sim2 = UniversalAIFabricator.build_golden_idle_npc()

    sim1.agents[0].state.velocity = (100.0, 50.0, 0.0)
    sim2.agents[0].state.velocity = (100.0, 50.0, 0.0)

    for _ in range(10):
        UniversalAIFabricator.execute_simulation_tick(sim1, dt=0.033)
        UniversalAIFabricator.execute_simulation_tick(sim2, dt=0.033)

    assert sim1.agents[0].state.position == sim2.agents[0].state.position


def test_simulation_tick_determinism_needs():
    sim1 = UniversalAIFabricator.build_golden_idle_npc()
    sim2 = UniversalAIFabricator.build_golden_idle_npc()

    for _ in range(15):
        UniversalAIFabricator.execute_simulation_tick(sim1, dt=0.1)
        UniversalAIFabricator.execute_simulation_tick(sim2, dt=0.1)

    assert sim1.agents[0].needs.hunger == sim2.agents[0].needs.hunger
    assert sim1.agents[0].needs.thirst == sim2.agents[0].needs.thirst
    assert sim1.agents[0].needs.energy == sim2.agents[0].needs.energy


def test_simulation_tick_determinism_perception():
    sim1 = UniversalAIFabricator.build_golden_combat()
    sim2 = UniversalAIFabricator.build_golden_combat()

    for _ in range(5):
        UniversalAIFabricator.execute_simulation_tick(sim1, dt=0.033)
        UniversalAIFabricator.execute_simulation_tick(sim2, dt=0.033)

    assert len(sim1.agents[0].memory.records) == len(sim2.agents[0].memory.records)


def test_simulation_tick_determinism_fsm():
    sim1 = UniversalAIFabricator.build_golden_patrol()
    sim2 = UniversalAIFabricator.build_golden_patrol()

    for _ in range(5):
        UniversalAIFabricator.execute_simulation_tick(sim1, dt=0.033)
        UniversalAIFabricator.execute_simulation_tick(sim2, dt=0.033)

    assert sim1.agents[0].current_fsm_state == sim2.agents[0].current_fsm_state


def test_pathfinding_determinism():
    start = (100.0, 200.0, 0.0)
    dest = (800.0, 900.0, 0.0)

    p1 = UniversalAIFabricator.compute_path(start, dest)
    p2 = UniversalAIFabricator.compute_path(start, dest)

    assert p1.waypoints == p2.waypoints
    assert p1.distance == p2.distance
    assert p1.cost == p2.cost


def test_crowd_simulation_determinism():
    from uaf.universal_ai import CrowdAgent
    c1 = [CrowdAgent("A1", (0.0, 0.0, 0.0), desired_velocity=(50.0, 0.0, 0.0))]
    c2 = [CrowdAgent("A1", (0.0, 0.0, 0.0), desired_velocity=(50.0, 0.0, 0.0))]

    UniversalAIFabricator.simulate_crowd(c1, dt=0.1)
    UniversalAIFabricator.simulate_crowd(c2, dt=0.1)

    assert c1[0].position == c2[0].position
    assert c1[0].velocity == c2[0].velocity


def test_formation_slots_determinism_line():
    slots1 = UniversalAIFabricator.compute_formation_slots(FormationType.LINE, count=5, spacing=120.0)
    slots2 = UniversalAIFabricator.compute_formation_slots(FormationType.LINE, count=5, spacing=120.0)
    assert slots1 == slots2


def test_formation_slots_determinism_column():
    slots1 = UniversalAIFabricator.compute_formation_slots(FormationType.COLUMN, count=4, spacing=100.0)
    slots2 = UniversalAIFabricator.compute_formation_slots(FormationType.COLUMN, count=4, spacing=100.0)
    assert slots1 == slots2


def test_formation_slots_determinism_wedge():
    slots1 = UniversalAIFabricator.compute_formation_slots(FormationType.WEDGE, count=6, spacing=150.0)
    slots2 = UniversalAIFabricator.compute_formation_slots(FormationType.WEDGE, count=6, spacing=150.0)
    assert slots1 == slots2


def test_formation_slots_determinism_circle():
    slots1 = UniversalAIFabricator.compute_formation_slots(FormationType.CIRCLE, count=8, spacing=100.0)
    slots2 = UniversalAIFabricator.compute_formation_slots(FormationType.CIRCLE, count=8, spacing=100.0)
    assert slots1 == slots2


def test_cover_selection_determinism():
    agent_pos = (50.0, 50.0, 0.0)
    threat_pos = (500.0, 500.0, 0.0)
    covers = [
        CoverPoint("C1", (100.0, 100.0, 0.0), (0.0, 1.0, 0.0), protection_score=0.7),
        CoverPoint("C2", (150.0, 150.0, 0.0), (0.0, 1.0, 0.0), protection_score=0.9),
    ]

    best1 = UniversalAIFabricator.find_best_cover(agent_pos, threat_pos, covers)
    best2 = UniversalAIFabricator.find_best_cover(agent_pos, threat_pos, covers)
    assert best1.cover_id == best2.cover_id


def test_flee_direction_determinism():
    d1 = UniversalAIFabricator.compute_flee_direction((100.0, 200.0, 0.0), (50.0, 50.0, 0.0))
    d2 = UniversalAIFabricator.compute_flee_direction((100.0, 200.0, 0.0), (50.0, 50.0, 0.0))
    assert d1 == d2


def test_utility_evaluation_determinism():
    c = UtilityConsideration("urgency", UtilityCurveType.LINEAR)
    act1 = UtilityAction("A1", [c], weight=1.0)
    act2 = UtilityAction("A2", [c], weight=2.0)

    best1 = UniversalAIFabricator.evaluate_utility([act1, act2], {"urgency": 0.5})
    best2 = UniversalAIFabricator.evaluate_utility([act1, act2], {"urgency": 0.5})
    assert best1.action_id == best2.action_id


def test_goap_planning_determinism():
    act = GOAPAction("DRAW", preconditions={"armed": False}, effects={"armed": True}, cost=1.0)
    goal = GOAPGoal("G", desired_state={"armed": True})
    cur = {"armed": False}

    p1 = UniversalAIFabricator.plan_goap([act], cur, goal)
    p2 = UniversalAIFabricator.plan_goap([act], cur, goal)
    assert [a.action_id for a in p1.actions] == [a.action_id for a in p2.actions]
    assert p1.total_cost == p2.total_cost


def test_spatial_query_determinism():
    sim = UniversalAIFabricator.build_golden_city_population()
    query = AIQuery(query_type=AIQueryType.VISIBLE_TARGETS, origin=(0.0, 0.0, 0.0), radius=500.0)

    r1 = UniversalAIFabricator.solve_ai_query(sim, query)
    r2 = UniversalAIFabricator.solve_ai_query(sim, query)
    assert [x["agent_id"] for x in r1] == [x["agent_id"] for x in r2]


def test_save_load_determinism():
    prof = AgentProfile("P_DET")
    agent = UniversalAIFabricator.spawn_agent("A_DET", prof, (10.0, 20.0, 30.0))
    agent.needs.hunger = 0.5

    save1 = UniversalAIFabricator.save_agent(agent)
    save2 = UniversalAIFabricator.save_agent(agent)

    assert save1.transform == save2.transform
    assert save1.state.position == save2.state.position
    assert save1.needs.hunger == save2.needs.hunger


def test_production_package_canonical_hash_determinism():
    sim1 = UniversalAIFabricator.build_golden_idle_npc()
    sim2 = UniversalAIFabricator.build_golden_idle_npc()

    pkg1 = ProductionReadySimulation(simulation=sim1)
    pkg2 = ProductionReadySimulation(simulation=sim2)

    assert pkg1.canonical_hash == pkg2.canonical_hash


def test_production_package_readback_determinism():
    sim = UniversalAIFabricator.build_golden_squad()
    pkg = ProductionReadySimulation(simulation=sim)

    rb1 = pkg.verify_readback()
    rb2 = pkg.verify_readback()

    assert rb1 == rb2
    assert rb1["agent_count"] == 3
    assert rb1["squad_count"] == 1
