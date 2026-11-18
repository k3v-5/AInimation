"""
Tests for Combat, Cover & Tactical System (UAF-81.57 Sections 105-114, 226).
"""

import math
import pytest
from uaf.universal_ai import (
    AICombatState,
    CombatRangeType,
    CoverPoint,
    AIAgent,
    AgentProfile,
    AgentState,
    SimulationDefinition,
    UniversalAIFabricator,
)


def test_combat_state_enum():
    states = {s.value for s in AICombatState}
    expected = {"IDLE", "ALERT", "SEARCHING", "ENGAGING", "DEFENDING", "RETREATING", "DEAD"}
    assert states == expected


def test_combat_range_type_enum():
    ranges = {r.value for r in CombatRangeType}
    expected = {"MELEE", "SHORT", "MEDIUM", "LONG"}
    assert ranges == expected


def test_cover_point_creation():
    cp = CoverPoint(
        cover_id="CP_01",
        position=(100.0, 200.0, 0.0),
        normal=(0.0, 1.0, 0.0),
        height=140.0,
        protection_score=0.9,
        is_occupied=False,
    )
    assert cp.cover_id == "CP_01"
    assert cp.position == (100.0, 200.0, 0.0)
    assert cp.normal == (0.0, 1.0, 0.0)
    assert cp.height == 140.0
    assert cp.protection_score == 0.9
    assert cp.is_occupied is False


def test_find_best_cover_selection():
    agent_pos = (0.0, 0.0, 0.0)
    threat_pos = (500.0, 0.0, 0.0)
    c1 = CoverPoint("C1", position=(100.0, 0.0, 0.0), normal=(-1.0, 0.0, 0.0), protection_score=0.5)
    c2 = CoverPoint("C2", position=(100.0, 50.0, 0.0), normal=(-1.0, 0.0, 0.0), protection_score=0.95)

    best = UniversalAIFabricator.find_best_cover(agent_pos, threat_pos, [c1, c2])
    assert best is not None
    assert best.cover_id == "C2"


def test_find_best_cover_ignores_occupied():
    agent_pos = (0.0, 0.0, 0.0)
    threat_pos = (500.0, 0.0, 0.0)
    c_occupied = CoverPoint("C_OCC", position=(50.0, 0.0, 0.0), normal=(-1.0, 0.0, 0.0), protection_score=1.0, is_occupied=True)
    c_free = CoverPoint("C_FREE", position=(150.0, 0.0, 0.0), normal=(-1.0, 0.0, 0.0), protection_score=0.7, is_occupied=False)

    best = UniversalAIFabricator.find_best_cover(agent_pos, threat_pos, [c_occupied, c_free])
    assert best is not None
    assert best.cover_id == "C_FREE"


def test_find_best_cover_no_available():
    agent_pos = (0.0, 0.0, 0.0)
    threat_pos = (500.0, 0.0, 0.0)
    c_occ = CoverPoint("C1", position=(50.0, 0.0, 0.0), normal=(-1.0, 0.0, 0.0), is_occupied=True)

    best = UniversalAIFabricator.find_best_cover(agent_pos, threat_pos, [c_occ])
    assert best is None


def test_compute_flee_direction_away():
    agent_pos = (100.0, 0.0, 0.0)
    threat_pos = (0.0, 0.0, 0.0)

    flee_dir = UniversalAIFabricator.compute_flee_direction(agent_pos, threat_pos)
    # Agent should flee towards positive X: (1, 0, 0)
    assert round(flee_dir[0], 2) == 1.0
    assert round(flee_dir[1], 2) == 0.0


def test_compute_flee_direction_colocated():
    agent_pos = (50.0, 50.0, 0.0)
    threat_pos = (50.0, 50.0, 0.0)

    flee_dir = UniversalAIFabricator.compute_flee_direction(agent_pos, threat_pos)
    assert flee_dir == (1.0, 0.0, 0.0)


def test_combat_state_simulation_tick_alert_increase():
    prof = AgentProfile(profile_id="P_COMBAT")
    agent = AIAgent("AGENT_COMBAT", profile=prof)
    agent.state.current_target = "ENEMY_1"
    agent.state.alert_level = 0.2

    sim = SimulationDefinition(simulation_id="SIM_COMBAT")
    sim.agents = [agent]

    UniversalAIFabricator.execute_simulation_tick(sim, dt=0.033)
    assert round(agent.state.alert_level, 2) == 0.30
