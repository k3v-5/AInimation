"""
Tests for Agent and Lifecycle System (UAF-81.57 Sections 3-10, 226).
"""

import pytest
from uaf.universal_ai import (
    AgentType,
    AgentLifecycleState,
    AgentState,
    AIAgent,
    AgentProfile,
    AIRandomStream,
)


def test_agent_creation_defaults():
    prof = AgentProfile(profile_id="PROF_NPC", agent_type=AgentType.NPC)
    agent = AIAgent(agent_id="NPC_001", profile=prof)
    assert agent.agent_id == "NPC_001"
    assert agent.profile.profile_id == "PROF_NPC"
    assert agent.profile.agent_type == AgentType.NPC
    assert agent.lifecycle == AgentLifecycleState.ACTIVE
    assert agent.state.health == 100.0


def test_agent_lifecycle_transitions():
    prof = AgentProfile(profile_id="PROF_LIFECYCLE")
    agent = AIAgent("NPC_LIFECYCLE", profile=prof, lifecycle=AgentLifecycleState.SPAWNING)
    assert agent.lifecycle == AgentLifecycleState.SPAWNING

    agent.lifecycle = AgentLifecycleState.ACTIVE
    assert agent.lifecycle == AgentLifecycleState.ACTIVE

    agent.lifecycle = AgentLifecycleState.PAUSED
    assert agent.lifecycle == AgentLifecycleState.PAUSED

    agent.lifecycle = AgentLifecycleState.SUSPENDED
    assert agent.lifecycle == AgentLifecycleState.SUSPENDED

    agent.lifecycle = AgentLifecycleState.DESPAWNING
    assert agent.lifecycle == AgentLifecycleState.DESPAWNING

    agent.lifecycle = AgentLifecycleState.DEAD
    assert agent.lifecycle == AgentLifecycleState.DEAD

    agent.lifecycle = AgentLifecycleState.PERSISTED
    assert agent.lifecycle == AgentLifecycleState.PERSISTED


def test_agent_profile_configuration():
    profile = AgentProfile(
        profile_id="PROF_GUARD",
        agent_type=AgentType.ENEMY,
        movement_speed=450.0,
        senses=["VISION", "HEARING", "PROXIMITY"],
        intelligence_model="GOAP",
        combat_profile="AGGRESSIVE",
        interaction_profile="HOSTILE",
        needs_enabled=False,
        social_enabled=True,
        schedule_enabled=False,
        simulation_lod=1,
    )
    assert profile.profile_id == "PROF_GUARD"
    assert profile.agent_type == AgentType.ENEMY
    assert profile.movement_speed == 450.0
    assert profile.senses == ["VISION", "HEARING", "PROXIMITY"]
    assert profile.intelligence_model == "GOAP"
    assert profile.combat_profile == "AGGRESSIVE"
    assert profile.needs_enabled is False


def test_agent_state_update():
    state = AgentState(
        position=(100.0, 200.0, 0.0),
        rotation=(0.0, 0.0, 90.0),
        velocity=(50.0, 0.0, 0.0),
        acceleration=(10.0, 0.0, 0.0),
        health=80.0,
        max_health=100.0,
        stamina=60.0,
        current_action="PATROL",
        current_goal="SECURE_AREA",
        alert_level=0.5,
    )
    assert state.position == (100.0, 200.0, 0.0)
    assert state.velocity == (50.0, 0.0, 0.0)
    assert state.health == 80.0
    assert state.stamina == 60.0
    assert state.current_action == "PATROL"
    assert state.alert_level == 0.5


def test_agent_serialization_roundtrip():
    prof = AgentProfile(profile_id="PROF_MERCHANT", agent_type=AgentType.NPC, movement_speed=300.0)
    agent = AIAgent("NPC_SERIAL", profile=prof, faction="MERCHANTS")
    agent.state.position = (10.0, 20.0, 30.0)
    agent.state.health = 95.0

    data = agent.to_dict()
    assert data["agent_id"] == "NPC_SERIAL"
    assert data["profile"]["agent_type"] == "NPC"
    assert data["state"]["health"] == 95.0
    assert data["faction"] == "MERCHANTS"

    restored = AIAgent.from_dict(data)
    assert restored.agent_id == agent.agent_id
    assert restored.profile.agent_type == AgentType.NPC
    assert restored.state.position == (10.0, 20.0, 30.0)
    assert restored.state.health == 95.0
    assert restored.faction == "MERCHANTS"


def test_agent_random_stream():
    stream1 = AIRandomStream(seed=12345)
    vals1 = [stream1.next_float() for _ in range(5)]

    stream2 = AIRandomStream(seed=12345)
    vals2 = [stream2.next_float() for _ in range(5)]

    assert vals1 == vals2
    assert all(0.0 <= v <= 1.0 for v in vals1)


def test_agent_random_range():
    stream = AIRandomStream(seed=999)
    ints = [stream.next_int(10, 50) for _ in range(20)]
    assert all(10 <= i <= 50 for i in ints)

    floats = [stream.next_range(-5.0, 5.0) for _ in range(20)]
    assert all(-5.0 <= f <= 5.0 for f in floats)


def test_agent_damage_and_death():
    prof = AgentProfile(profile_id="PROF_TARGET")
    agent = AIAgent("NPC_TARGET", profile=prof)
    assert agent.is_alive() is True

    agent.apply_damage(40.0)
    assert agent.state.health == 60.0
    assert agent.is_alive() is True

    agent.apply_damage(70.0)
    assert agent.state.health == 0.0
    assert agent.is_alive() is False
    assert agent.lifecycle == AgentLifecycleState.DEAD
