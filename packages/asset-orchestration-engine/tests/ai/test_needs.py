"""
Tests for Needs & Drives System (UAF-81.57 Sections 121-125, 226).
"""

import pytest
from uaf.universal_ai import (
    NeedType,
    NeedsProfile,
    AIAgent,
    AgentProfile,
    SimulationDefinition,
    UniversalAIFabricator,
)


def test_need_types_enum():
    types = {t.value for t in NeedType}
    expected = {
        "HUNGER",
        "THIRST",
        "ENERGY",
        "SAFETY",
        "SOCIAL",
        "COMFORT",
        "CURIOSITY",
        "CUSTOM",
    }
    assert types == expected


def test_needs_profile_defaults():
    np = NeedsProfile()
    assert np.hunger == 0.0
    assert np.thirst == 0.0
    assert np.energy == 1.0
    assert np.safety == 1.0
    assert np.social == 0.5


def test_needs_profile_decay():
    np = NeedsProfile()
    np.update_decay(dt=10.0)

    # hunger: 0.005 * 10 = 0.05
    assert round(np.hunger, 3) == 0.05
    # thirst: 0.01 * 10 = 0.10
    assert round(np.thirst, 3) == 0.10
    # energy: 1.0 - (0.002 * 10) = 0.98
    assert round(np.energy, 3) == 0.98


def test_needs_clamping_upper_limit():
    np = NeedsProfile(hunger=0.95, thirst=0.95)
    np.update_decay(dt=100.0)  # Large delta
    assert np.hunger == 1.0
    assert np.thirst == 1.0


def test_needs_clamping_lower_limit():
    np = NeedsProfile(energy=0.01)
    np.update_decay(dt=100.0)  # Large delta
    assert np.energy == 0.0


def test_needs_satisfaction():
    np = NeedsProfile(hunger=0.8, thirst=0.9, energy=0.2)

    # Satisfy hunger and thirst
    np.hunger = max(0.0, np.hunger - 0.7)
    np.thirst = max(0.0, np.thirst - 0.9)
    # Sleep / restore energy
    np.energy = min(1.0, np.energy + 0.6)

    assert round(np.hunger, 2) == 0.10
    assert round(np.thirst, 2) == 0.0
    assert round(np.energy, 2) == 0.80


def test_needs_simulation_tick_integration():
    prof = AgentProfile(profile_id="P_NEEDS")
    agent = AIAgent("AGENT_HUNGRY", profile=prof)
    agent.needs.hunger = 0.1

    sim = SimulationDefinition(simulation_id="SIM_NEEDS")
    sim.agents = [agent]

    UniversalAIFabricator.execute_simulation_tick(sim, dt=20.0)
    # Hunger should have increased: 0.1 + (0.005 * 20) = 0.2
    assert round(agent.needs.hunger, 2) == 0.20
