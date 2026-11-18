"""
Tests for Crowd Simulation & Flocking System (UAF-81.57 Sections 79-85, 226).
"""

import pytest
from uaf.universal_ai import (
    CrowdGroupType,
    CrowdAgent,
    UniversalAIFabricator,
)


def test_crowd_group_type_enum():
    groups = {g.value for g in CrowdGroupType}
    expected = {"PEDESTRIAN", "CIVILIAN", "MILITARY", "ANIMAL", "EMERGENCY", "CUSTOM"}
    assert groups == expected


def test_crowd_agent_creation():
    agent = CrowdAgent(
        agent_id="PED_01",
        position=(100.0, 100.0, 0.0),
        desired_velocity=(100.0, 0.0, 0.0),
        radius=40.0,
        group_type=CrowdGroupType.PEDESTRIAN,
    )
    assert agent.agent_id == "PED_01"
    assert agent.position == (100.0, 100.0, 0.0)
    assert agent.desired_velocity == (100.0, 0.0, 0.0)
    assert agent.radius == 40.0
    assert agent.group_type == CrowdGroupType.PEDESTRIAN


def test_crowd_simulation_free_flow():
    # Two agents far apart (dist 500 > sum of radii 80)
    a1 = CrowdAgent("A1", position=(0.0, 0.0, 0.0), desired_velocity=(100.0, 0.0, 0.0), radius=40.0)
    a2 = CrowdAgent("A2", position=(500.0, 0.0, 0.0), desired_velocity=(0.0, 100.0, 0.0), radius=40.0)

    UniversalAIFabricator.simulate_crowd([a1, a2], dt=0.1)

    # a1 moved 10 units in X
    assert round(a1.position[0], 2) == 10.0
    assert round(a1.position[1], 2) == 0.0

    # a2 moved 10 units in Y
    assert round(a2.position[0], 2) == 500.0
    assert round(a2.position[1], 2) == 10.0


def test_crowd_repulsion_collision_avoidance():
    # Two overlapping agents (distance 20 < 40 + 40)
    a1 = CrowdAgent("A1", position=(0.0, 0.0, 0.0), desired_velocity=(0.0, 0.0, 0.0), radius=40.0)
    a2 = CrowdAgent("A2", position=(20.0, 0.0, 0.0), desired_velocity=(0.0, 0.0, 0.0), radius=40.0)

    UniversalAIFabricator.simulate_crowd([a1, a2], dt=0.033)

    # a1 should be pushed left (negative X)
    # a2 should be pushed right (positive X)
    assert a1.velocity[0] < 0.0
    assert a2.velocity[0] > 0.0


def test_crowd_deadlock_detection_positive():
    agent = CrowdAgent(
        agent_id="BLOCKED_01",
        position=(0.0, 0.0, 0.0),
        velocity=(1.0, 0.0, 0.0),  # Slow / trapped (< 5.0)
        desired_velocity=(200.0, 0.0, 0.0),  # Wants to move fast (> 50.0)
    )
    deadlocks = UniversalAIFabricator.detect_crowd_deadlocks([agent])
    assert "BLOCKED_01" in deadlocks


def test_crowd_deadlock_detection_negative():
    agent = CrowdAgent(
        agent_id="FREE_01",
        position=(0.0, 0.0, 0.0),
        velocity=(150.0, 0.0, 0.0),  # Moving well
        desired_velocity=(150.0, 0.0, 0.0),
    )
    deadlocks = UniversalAIFabricator.detect_crowd_deadlocks([agent])
    assert len(deadlocks) == 0


def test_crowd_group_diversity():
    a1 = CrowdAgent("P1", position=(0.0, 0.0, 0.0), group_type=CrowdGroupType.PEDESTRIAN)
    a2 = CrowdAgent("C1", position=(100.0, 0.0, 0.0), group_type=CrowdGroupType.CIVILIAN)
    a3 = CrowdAgent("M1", position=(200.0, 0.0, 0.0), group_type=CrowdGroupType.MILITARY)

    crowd = [a1, a2, a3]
    types = {a.group_type for a in crowd}
    assert len(types) == 3


def test_crowd_simulation_zero_dt():
    a = CrowdAgent("A", position=(50.0, 50.0, 0.0), desired_velocity=(100.0, 100.0, 0.0))
    UniversalAIFabricator.simulate_crowd([a], dt=0.0)
    assert a.position == (50.0, 50.0, 0.0)
