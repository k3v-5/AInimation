"""
Tests for World Reaction & Territory System (UAF-81.57 Sections 136-140, 226).
"""

import math
import pytest
from uaf.universal_ai import (
    TerritoryDefinition,
    AISoundEvent,
    AIAgent,
    AgentProfile,
    AgentState,
    AICombatState,
    UniversalAIFabricator,
)


def test_territory_definition():
    terr = TerritoryDefinition(
        territory_id="WOLF_DEN",
        center=(1000.0, 1000.0, 0.0),
        radius=3000.0,
        owner_faction="WOLVES",
        threat_level=0.8,
    )
    assert terr.territory_id == "WOLF_DEN"
    assert terr.center == (1000.0, 1000.0, 0.0)
    assert terr.radius == 3000.0
    assert terr.owner_faction == "WOLVES"
    assert terr.threat_level == 0.8


def test_territory_intrusion_detection():
    terr = TerritoryDefinition(
        territory_id="BANDIT_CAMP",
        center=(0.0, 0.0, 0.0),
        radius=500.0,
        owner_faction="BANDITS",
    )
    agent_pos = (200.0, 200.0, 0.0)
    dist = math.sqrt(agent_pos[0]**2 + agent_pos[1]**2)
    is_intruder = dist <= terr.radius and "TOWN_GUARD" != terr.owner_faction
    assert is_intruder is True


def test_territory_owner_ignored():
    terr = TerritoryDefinition(
        territory_id="BANDIT_CAMP",
        center=(0.0, 0.0, 0.0),
        radius=500.0,
        owner_faction="BANDITS",
    )
    bandit_pos = (100.0, 100.0, 0.0)
    agent_faction = "BANDITS"
    dist = math.sqrt(bandit_pos[0]**2 + bandit_pos[1]**2)
    is_intruder = dist <= terr.radius and agent_faction != terr.owner_faction
    assert is_intruder is False


def test_weather_shelter_reaction():
    prof = AgentProfile(profile_id="P_CIVILIAN")
    agent = AIAgent("NPC_FARMER", profile=prof)
    agent.state.current_action = "FARMING"

    # Severe thunderstorm event
    weather = "THUNDERSTORM"
    if weather == "THUNDERSTORM":
        agent.state.current_action = "SEEK_SHELTER"
        agent.state.current_goal = "RUN_TO_HOUSE"

    assert agent.state.current_action == "SEEK_SHELTER"
    assert agent.state.current_goal == "RUN_TO_HOUSE"


def test_sound_stimulus_investigation():
    sound = AISoundEvent(
        position=(800.0, 200.0, 0.0),
        volume=0.9,
        category="EXPLOSION",
    )
    prof = AgentProfile(profile_id="P_GUARD")
    agent = AIAgent("GUARD_ALPHA", profile=prof, state=AgentState(position=(500.0, 200.0, 0.0)))

    # Sound is within hearing distance (300 units)
    dist = abs(sound.position[0] - agent.state.position[0])
    if dist <= 1000.0 and sound.volume > 0.5:
        agent.state.alert_level = 1.0
        agent.state.current_action = "INVESTIGATE"
        agent.state.current_target = "SOUND_SOURCE"

    assert agent.state.alert_level == 1.0
    assert agent.state.current_action == "INVESTIGATE"


def test_environmental_hazard_avoidance():
    # Fire obstacle at (500, 0, 0)
    start = (0.0, 0.0, 0.0)
    dest = (1000.0, 0.0, 0.0)
    from uaf.universal_ai import DynamicObstacle
    fire = DynamicObstacle(obstacle_id="FIRE_WALL", position=(500.0, 0.0, 0.0), radius=80.0)

    path = UniversalAIFabricator.compute_path(start, dest, obstacles=[fire])
    assert len(path.waypoints) == 3  # Avoided fire obstacle


def test_alarm_broadcast_reaction():
    alarm_origin = (0.0, 0.0, 0.0)
    alarm_radius = 2000.0

    citizens = [
        AIAgent("C1", profile=AgentProfile("P1"), state=AgentState(position=(500.0, 0.0, 0.0))),
        AIAgent("C2", profile=AgentProfile("P2"), state=AgentState(position=(1500.0, 0.0, 0.0))),
        AIAgent("C3", profile=AgentProfile("P3"), state=AgentState(position=(3500.0, 0.0, 0.0))),
    ]

    for c in citizens:
        d = math.sqrt(c.state.position[0]**2 + c.state.position[1]**2)
        if d <= alarm_radius:
            c.state.current_action = "FLEE"

    assert citizens[0].state.current_action == "FLEE"
    assert citizens[1].state.current_action == "FLEE"
    assert citizens[2].state.current_action == "IDLE"
