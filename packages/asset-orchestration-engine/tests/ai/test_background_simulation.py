"""
Tests for Background & Abstract Simulation System (UAF-81.57 Sections 157-161, 226).
"""

import pytest
from uaf.universal_ai import (
    AbstractAgentState,
    AIAgent,
    AgentProfile,
    AgentType,
    SimulationDefinition,
    UniversalAIFabricator,
)


def test_background_simulation_abstract_agent():
    state = AbstractAgentState(
        group_id="VILLAGE_FARMERS",
        population=120,
        resource_level=0.5,
    )
    # Simulate 5 coarse time steps of production
    for _ in range(5):
        state.resource_level = min(1.0, state.resource_level + 0.05)

    assert round(state.resource_level, 2) == 0.75


def test_background_simulation_population_growth_and_attrition():
    state = AbstractAgentState(group_id="NOMAD_TRIBE", population=100)

    # 5% natural increase
    births = int(state.population * 0.05)
    # 2% natural mortality
    deaths = int(state.population * 0.02)
    state.population = state.population + births - deaths

    assert state.population == 103


def test_background_simulation_migration():
    group = AbstractAgentState(
        group_id="CARAVAN",
        location=(0.0, 0.0, 0.0),
        activity="TRAVELING",
    )
    target = (1000.0, 0.0, 0.0)

    # Macro step moves 250 units along vector
    for step in range(4):
        x = group.location[0] + 250.0
        group.location = (x, group.location[1], group.location[2])

    assert group.location == (1000.0, 0.0, 0.0)


def test_background_simulation_materialization():
    group = AbstractAgentState(group_id="MINERS", population=3, location=(500.0, 500.0, 0.0))

    # Player approaches -> materialize 3 individual agents
    prof = AgentProfile(profile_id="PROF_MINER", agent_type=AgentType.NPC)
    agents = []
    for i in range(group.population):
        a = UniversalAIFabricator.spawn_agent(
            agent_id=f"{group.group_id}_{i}",
            profile=prof,
            initial_position=(group.location[0] + i * 50.0, group.location[1], 0.0),
        )
        agents.append(a)

    assert len(agents) == 3
    assert agents[0].agent_id == "MINERS_0"
    assert agents[1].agent_id == "MINERS_1"
    assert agents[2].agent_id == "MINERS_2"


def test_golden_background_simulation_scenario():
    sim = UniversalAIFabricator.build_golden_background_simulation()
    assert sim.simulation_id == "SIM_GOLDEN_BG"
    assert len(sim.agents) == 1
    assert sim.agents[0].profile.simulation_lod == 2
