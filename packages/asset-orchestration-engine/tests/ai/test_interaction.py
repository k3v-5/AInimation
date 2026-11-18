"""
Tests for Interaction & Smart Objects System (UAF-81.57 Sections 115-120, 226).
"""

import pytest
from uaf.universal_ai import (
    AIInteractionType,
    InteractableDefinition,
    AIAgent,
    AgentProfile,
    AgentState,
    SimulationDefinition,
    UniversalAIFabricator,
)


def test_interaction_type_enum():
    types = {t.value for t in AIInteractionType}
    expected = {
        "TALK",
        "OPEN",
        "CLOSE",
        "USE",
        "PICKUP",
        "DROP",
        "ACTIVATE",
        "SIT",
        "SLEEP",
        "WORK",
        "TRADE",
        "CUSTOM",
    }
    assert types == expected


def test_interactable_definition():
    obj = InteractableDefinition(
        interactable_id="CHAIR_01",
        interaction_type=AIInteractionType.SIT,
        position=(100.0, 50.0, 0.0),
        interaction_radius=150.0,
    )
    assert obj.interactable_id == "CHAIR_01"
    assert obj.interaction_type == AIInteractionType.SIT
    assert obj.position == (100.0, 50.0, 0.0)
    assert obj.interaction_radius == 150.0
    assert obj.is_reserved is False
    assert obj.reserved_by is None


def test_interactable_reservation_simulation_tick():
    prof = AgentProfile(profile_id="P_USER")
    agent = AIAgent("AGENT_SITTER", profile=prof, state=AgentState(position=(100.0, 50.0, 0.0)))

    chair = InteractableDefinition(
        interactable_id="CHAIR_ALPHA",
        interaction_type=AIInteractionType.SIT,
        position=(110.0, 50.0, 0.0),  # Distance 10.0 <= radius 200.0
        interaction_radius=200.0,
    )

    sim = SimulationDefinition(simulation_id="SIM_INTERACT")
    sim.agents = [agent]
    sim.interactables = [chair]

    UniversalAIFabricator.execute_simulation_tick(sim, dt=0.033)
    assert chair.is_reserved is True
    assert chair.reserved_by == "AGENT_SITTER"


def test_interactable_out_of_range_no_reservation():
    prof = AgentProfile(profile_id="P_USER")
    agent = AIAgent("AGENT_FAR", profile=prof, state=AgentState(position=(0.0, 0.0, 0.0)))

    workbench = InteractableDefinition(
        interactable_id="BENCH_01",
        interaction_type=AIInteractionType.WORK,
        position=(1000.0, 1000.0, 0.0),  # Far away
        interaction_radius=100.0,
    )

    sim = SimulationDefinition(simulation_id="SIM_FAR")
    sim.agents = [agent]
    sim.interactables = [workbench]

    UniversalAIFabricator.execute_simulation_tick(sim, dt=0.033)
    assert workbench.is_reserved is False
    assert workbench.reserved_by is None


def test_interactable_already_reserved_not_overwritten():
    prof = AgentProfile(profile_id="P_USER")
    a1 = AIAgent("AGENT_1", profile=prof, state=AgentState(position=(10.0, 0.0, 0.0)))
    a2 = AIAgent("AGENT_2", profile=prof, state=AgentState(position=(20.0, 0.0, 0.0)))

    chest = InteractableDefinition(
        interactable_id="CHEST_PRIZE",
        position=(0.0, 0.0, 0.0),
        interaction_radius=200.0,
        is_reserved=True,
        reserved_by="FIRST_CLAIMER",
    )

    sim = SimulationDefinition(simulation_id="SIM_CLAIMED")
    sim.agents = [a1, a2]
    sim.interactables = [chest]

    UniversalAIFabricator.execute_simulation_tick(sim, dt=0.033)
    assert chest.reserved_by == "FIRST_CLAIMER"


def test_interactable_release():
    bed = InteractableDefinition(
        interactable_id="BED_01",
        interaction_type=AIInteractionType.SLEEP,
        is_reserved=True,
        reserved_by="SLEEPER",
    )
    assert bed.is_reserved is True

    # Wake up / release
    bed.is_reserved = False
    bed.reserved_by = None

    assert bed.is_reserved is False
    assert bed.reserved_by is None


def test_multiple_interactables_selection():
    prof = AgentProfile(profile_id="P_USER")
    agent = AIAgent("AGENT_SEARCH", profile=prof, state=AgentState(position=(0.0, 0.0, 0.0)))

    o1 = InteractableDefinition("OBJ_NEAR", position=(50.0, 0.0, 0.0), interaction_radius=100.0)
    o2 = InteractableDefinition("OBJ_FAR", position=(500.0, 0.0, 0.0), interaction_radius=100.0)

    sim = SimulationDefinition(simulation_id="SIM_MULTI")
    sim.agents = [agent]
    sim.interactables = [o1, o2]

    UniversalAIFabricator.execute_simulation_tick(sim, dt=0.033)
    assert o1.is_reserved is True
    assert o1.reserved_by == "AGENT_SEARCH"
    assert o2.is_reserved is False
