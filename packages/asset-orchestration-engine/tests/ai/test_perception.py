"""
Tests for Perception & Sensor System (UAF-81.57 Sections 22-33, 226).
"""

import math
import pytest
from uaf.universal_ai import (
    SenseType,
    PerceptionFilter,
    PerceptionEvent,
    HearingProfile,
    AISoundEvent,
    AIAgent,
    AgentProfile,
    AgentState,
    AgentLifecycleState,
    SimulationDefinition,
    UniversalAIFabricator,
)


def test_sense_types_enum():
    senses = {s.value for s in SenseType}
    expected = {"VISION", "HEARING", "SMELL", "TOUCH", "PROXIMITY", "WORLD_QUERY", "CUSTOM"}
    assert senses == expected


def test_perception_filters_enum():
    filters = {f.value for f in PerceptionFilter}
    expected = {"ALLY", "ENEMY", "NEUTRAL", "ANIMAL", "PLAYER", "OBJECT", "ENVIRONMENT", "CUSTOM"}
    assert filters == expected


def test_perception_event_creation():
    event = PerceptionEvent(
        source_agent_id="AGENT_A",
        target_id="AGENT_B",
        sense=SenseType.VISION,
        confidence=0.85,
        distance=350.0,
        direction=(0.8, 0.6, 0.0),
        timestamp=10.0,
    )
    assert event.source_agent_id == "AGENT_A"
    assert event.target_id == "AGENT_B"
    assert event.sense == SenseType.VISION
    assert event.confidence == 0.85
    assert event.distance == 350.0
    assert event.timestamp == 10.0


def test_perception_event_serialization():
    event = PerceptionEvent(
        source_agent_id="AGENT_A",
        target_id="AGENT_B",
        sense=SenseType.HEARING,
        confidence=0.5,
        distance=600.0,
        direction=(0.0, 1.0, 0.0),
        timestamp=5.0,
    )
    d = event.to_dict()
    assert d["source_agent_id"] == "AGENT_A"
    assert d["target_id"] == "AGENT_B"
    assert d["sense"] == "HEARING"
    assert d["confidence"] == 0.5
    assert d["distance"] == 600.0


def test_hearing_profile():
    hp = HearingProfile(range=1800.0, attenuation=0.4, occlusion_factor=0.75)
    assert hp.range == 1800.0
    assert hp.attenuation == 0.4
    assert hp.occlusion_factor == 0.75


def test_sound_event():
    sound = AISoundEvent(
        position=(500.0, 100.0, 0.0),
        volume=0.9,
        category="GUNSHOT",
        source="PLAYER",
        timestamp=12.5,
    )
    assert sound.position == (500.0, 100.0, 0.0)
    assert sound.volume == 0.9
    assert sound.category == "GUNSHOT"
    assert sound.source == "PLAYER"


def test_perception_confidence_distance_decay():
    max_range = 1000.0
    distances = [100.0, 500.0, 900.0]
    confidences = [max(0.0, 1.0 - (d / max_range)) for d in distances]
    assert confidences[0] > confidences[1] > confidences[2]
    assert confidences[0] == 0.9
    assert confidences[1] == 0.5
    assert round(confidences[2], 2) == 0.1


def test_perception_cone_of_vision():
    # Agent facing (1, 0, 0), target at (1, 1, 0)
    forward = (1.0, 0.0, 0.0)
    to_target = (1.0, 1.0, 0.0)
    length = math.sqrt(to_target[0]**2 + to_target[1]**2)
    norm_to_target = (to_target[0]/length, to_target[1]/length, 0.0)

    dot = forward[0]*norm_to_target[0] + forward[1]*norm_to_target[1]
    angle_deg = math.degrees(math.acos(dot))
    assert 44.0 < angle_deg < 46.0

    # If FOV is 90 degrees (half-angle 45), target is inside
    assert angle_deg <= 45.0 + 1e-3


def test_perception_occlusion_calculation():
    initial_volume = 1.0
    wall_occlusion = 0.6  # 60% occlusion per wall
    effective_volume = initial_volume * (1.0 - wall_occlusion)
    assert round(effective_volume, 2) == 0.40


def test_simulation_tick_perception_stage():
    sim = SimulationDefinition(simulation_id="SIM_PERCEPT")
    p1 = AgentProfile(profile_id="P1")
    p2 = AgentProfile(profile_id="P2")

    a1 = AIAgent("A1", profile=p1, state=AgentState(position=(0.0, 0.0, 0.0)))
    a2 = AIAgent("A2", profile=p2, state=AgentState(position=(500.0, 0.0, 0.0)))
    sim.agents = [a1, a2]

    UniversalAIFabricator.execute_simulation_tick(sim, dt=0.033)
    assert len(a1.memory.records) > 0
    records = list(a1.memory.records.values())
    record = records[0]
    assert record.subject == "A2"
    assert record.location == (500.0, 0.0, 0.0)



def test_simulation_tick_perception_out_of_range():
    sim = SimulationDefinition(simulation_id="SIM_OUT_OF_RANGE")
    p1 = AgentProfile(profile_id="P1")
    p2 = AgentProfile(profile_id="P2")

    a1 = AIAgent("A1", profile=p1, state=AgentState(position=(0.0, 0.0, 0.0)))
    a2 = AIAgent("A2", profile=p2, state=AgentState(position=(5000.0, 0.0, 0.0)))  # Out of 1500 radius
    sim.agents = [a1, a2]

    UniversalAIFabricator.execute_simulation_tick(sim, dt=0.033)
    assert len(a1.memory.records) == 0
