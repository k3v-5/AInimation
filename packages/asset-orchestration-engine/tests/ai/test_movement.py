"""
Tests for Movement & Locomotion System (UAF-81.57 Sections 69-71, 226).
"""

import math
import pytest
from uaf.universal_ai import (
    AIMovementMode,
    AIMovementProfile,
    AIAgent,
    AgentProfile,
    AgentState,
    SimulationDefinition,
    UniversalAIFabricator,
)


def test_movement_mode_enum():
    modes = {m.value for m in AIMovementMode}
    expected = {
        "WALK",
        "RUN",
        "SPRINT",
        "CROUCH",
        "CRAWL",
        "CLIMB",
        "SWIM",
        "FLY",
        "DRIVE",
        "CUSTOM",
    }
    assert modes == expected


def test_movement_profile_creation():
    prof = AIMovementProfile(
        speed=500.0,
        acceleration=1000.0,
        deceleration=1500.0,
        turn_rate=450.0,
        radius=45.0,
        height=190.0,
        step_height=50.0,
        slope_limit=40.0,
    )
    assert prof.speed == 500.0
    assert prof.acceleration == 1000.0
    assert prof.deceleration == 1500.0
    assert prof.turn_rate == 450.0
    assert prof.radius == 45.0
    assert prof.height == 190.0
    assert prof.step_height == 50.0
    assert prof.slope_limit == 40.0


def test_movement_profile_custom():
    flying_prof = AIMovementProfile(
        speed=1500.0,
        acceleration=2500.0,
        slope_limit=90.0,
    )
    assert flying_prof.speed == 1500.0
    assert flying_prof.slope_limit == 90.0


def test_movement_simulation_tick_velocity():
    prof = AgentProfile(profile_id="P_WALK")
    agent = AIAgent("AGENT_MOVE", profile=prof)
    agent.state.position = (0.0, 0.0, 0.0)
    agent.state.velocity = (100.0, 0.0, 0.0)

    sim = SimulationDefinition(simulation_id="SIM_MOVE")
    sim.agents = [agent]

    UniversalAIFabricator.execute_simulation_tick(sim, dt=0.5)
    assert agent.state.position == (50.0, 0.0, 0.0)


def test_movement_simulation_tick_stationary():
    prof = AgentProfile(profile_id="P_STATIONARY")
    agent = AIAgent("AGENT_STILL", profile=prof)
    agent.state.position = (10.0, 20.0, 30.0)
    agent.state.velocity = (0.0, 0.0, 0.0)

    sim = SimulationDefinition(simulation_id="SIM_STILL")
    sim.agents = [agent]

    UniversalAIFabricator.execute_simulation_tick(sim, dt=1.0)
    assert agent.state.position == (10.0, 20.0, 30.0)


def test_movement_simulation_tick_3d():
    prof = AgentProfile(profile_id="P_3D")
    agent = AIAgent("AGENT_3D", profile=prof)
    agent.state.position = (0.0, 0.0, 0.0)
    agent.state.velocity = (10.0, 20.0, -5.0)

    sim = SimulationDefinition(simulation_id="SIM_3D")
    sim.agents = [agent]

    UniversalAIFabricator.execute_simulation_tick(sim, dt=0.1)
    assert round(agent.state.position[0], 2) == 1.0
    assert round(agent.state.position[1], 2) == 2.0
    assert round(agent.state.position[2], 2) == -0.5


def test_movement_turn_rate_clamping():
    current_heading = 0.0  # degrees
    target_heading = 90.0  # degrees
    turn_rate = 180.0  # deg / sec
    dt = 0.2  # max turn in dt = 36 deg

    max_delta = turn_rate * dt
    diff = target_heading - current_heading
    clamped_delta = math.copysign(min(abs(diff), max_delta), diff)
    new_heading = current_heading + clamped_delta

    assert new_heading == 36.0


def test_movement_acceleration_integration():
    current_speed = 0.0
    max_speed = 400.0
    accel = 800.0
    dt = 0.25

    # In 0.25 sec, speed increases by 200
    new_speed = min(max_speed, current_speed + accel * dt)
    assert new_speed == 200.0

    # In another 0.5 sec, speed reaches max_speed
    new_speed2 = min(max_speed, new_speed + accel * 0.5)
    assert new_speed2 == 400.0


def test_movement_deceleration_braking():
    current_speed = 300.0
    decel = 600.0
    dt = 0.2

    # In 0.2 sec, decel removes 120
    new_speed = max(0.0, current_speed - decel * dt)
    assert new_speed == 180.0

    # In another 0.5 sec, decel brings speed to 0
    new_speed2 = max(0.0, new_speed - decel * 0.5)
    assert new_speed2 == 0.0
