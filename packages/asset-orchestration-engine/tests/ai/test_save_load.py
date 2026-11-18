"""
Tests for Save & Load System (UAF-81.57 Sections 145-149, 226).
"""

import pytest
from uaf.universal_ai import (
    AISaveState,
    AIAgent,
    AgentProfile,
    AgentState,
    NeedsProfile,
    UniversalAIFabricator,
)


def test_save_state_creation():
    st = AgentState(position=(100.0, 200.0, 50.0), health=75.0)
    np = NeedsProfile(hunger=0.3, thirst=0.4)
    save = AISaveState(
        agent_id="NPC_SAVED",
        transform=(100.0, 200.0, 50.0),
        state=st,
        needs=np,
        timestamp=100.5,
    )
    assert save.agent_id == "NPC_SAVED"
    assert save.transform == (100.0, 200.0, 50.0)
    assert save.state.health == 75.0
    assert save.needs.hunger == 0.3
    assert save.schema_version == "1.0.0"


def test_fabricator_save_agent():
    prof = AgentProfile(profile_id="P_SAVE")
    agent = AIAgent("AGENT_S", profile=prof)
    agent.state.position = (300.0, 400.0, 10.0)
    agent.needs.hunger = 0.65

    save_state = UniversalAIFabricator.save_agent(agent)
    assert save_state.agent_id == "AGENT_S"
    assert save_state.transform == (300.0, 400.0, 10.0)
    assert save_state.needs.hunger == 0.65


def test_fabricator_load_agent():
    prof = AgentProfile(profile_id="P_LOAD")
    agent = AIAgent("AGENT_L", profile=prof)

    saved_state = AgentState(position=(50.0, 50.0, 0.0), health=85.0)
    saved_needs = NeedsProfile(hunger=0.2, energy=0.9)
    save = AISaveState(agent_id="AGENT_L", transform=(50.0, 50.0, 0.0), state=saved_state, needs=saved_needs)

    UniversalAIFabricator.load_agent(agent, save)
    assert agent.state.position == (50.0, 50.0, 0.0)
    assert agent.state.health == 85.0
    assert agent.needs.hunger == 0.2
    assert agent.needs.energy == 0.9


def test_save_load_position_restoration():
    prof = AgentProfile(profile_id="P_POS")
    agent = AIAgent("AGENT_P", profile=prof)
    agent.state.position = (999.0, -888.0, 777.0)

    save = UniversalAIFabricator.save_agent(agent)

    # Mutate agent position
    agent.state.position = (0.0, 0.0, 0.0)
    assert agent.state.position == (0.0, 0.0, 0.0)

    # Restore
    UniversalAIFabricator.load_agent(agent, save)
    assert agent.state.position == (999.0, -888.0, 777.0)


def test_save_load_needs_restoration():
    prof = AgentProfile(profile_id="P_N")
    agent = AIAgent("AGENT_N", profile=prof)
    agent.needs.hunger = 0.85
    agent.needs.thirst = 0.70

    save = UniversalAIFabricator.save_agent(agent)

    # Reset needs
    agent.needs = NeedsProfile()
    assert agent.needs.hunger == 0.0

    # Restore
    UniversalAIFabricator.load_agent(agent, save)
    assert agent.needs.hunger == 0.85
    assert agent.needs.thirst == 0.70


def test_save_load_roundtrip_equality():
    prof = AgentProfile(profile_id="P_EQ")
    agent = AIAgent("AGENT_EQ", profile=prof)
    agent.state.position = (123.0, 456.0, 789.0)
    agent.state.velocity = (10.0, 0.0, 0.0)
    agent.state.health = 92.5

    save = UniversalAIFabricator.save_agent(agent)
    fresh_agent = AIAgent("AGENT_EQ", profile=prof)
    UniversalAIFabricator.load_agent(fresh_agent, save)

    assert fresh_agent.state.position == agent.state.position
    assert fresh_agent.state.velocity == agent.state.velocity
    assert fresh_agent.state.health == agent.state.health


def test_save_state_versioning():
    save = AISaveState(
        agent_id="A_V",
        transform=(0.0, 0.0, 0.0),
        state=AgentState(),
        needs=NeedsProfile(),
    )
    assert save.schema_version == "1.0.0"
