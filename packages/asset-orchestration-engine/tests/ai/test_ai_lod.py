"""
Tests for AI Simulation LOD System (UAF-81.57 Sections 150-156, 226).
"""

import pytest
from uaf.universal_ai import (
    AISimulationLOD,
    AbstractAgentState,
)


def test_ai_lod_enum():
    lods = {lod.value for lod in AISimulationLOD}
    expected = {
        "LOD0_FULL",
        "LOD1_REDUCED",
        "LOD2_BACKGROUND",
        "LOD3_ABSTRACT",
        "LOD4_FROZEN",
    }
    assert lods == expected


def test_abstract_agent_state_creation():
    state = AbstractAgentState(
        group_id="CARAVAN_01",
        population=45,
        location=(5000.0, 10000.0, 0.0),
        activity="TRAVELING",
        resource_level=0.85,
    )
    assert state.group_id == "CARAVAN_01"
    assert state.population == 45
    assert state.location == (5000.0, 10000.0, 0.0)
    assert state.activity == "TRAVELING"
    assert state.resource_level == 0.85


def determine_simulation_lod(distance: float) -> AISimulationLOD:
    if distance < 2000.0:
        return AISimulationLOD.LOD0_FULL
    elif distance < 5000.0:
        return AISimulationLOD.LOD1_REDUCED
    elif distance < 15000.0:
        return AISimulationLOD.LOD2_BACKGROUND
    elif distance < 50000.0:
        return AISimulationLOD.LOD3_ABSTRACT
    else:
        return AISimulationLOD.LOD4_FROZEN


def test_lod_selection_by_distance_lod0():
    lod = determine_simulation_lod(500.0)
    assert lod == AISimulationLOD.LOD0_FULL


def test_lod_selection_by_distance_lod1():
    lod = determine_simulation_lod(3500.0)
    assert lod == AISimulationLOD.LOD1_REDUCED


def test_lod_selection_by_distance_lod2():
    lod = determine_simulation_lod(8000.0)
    assert lod == AISimulationLOD.LOD2_BACKGROUND


def test_lod_selection_by_distance_lod3():
    lod = determine_simulation_lod(25000.0)
    assert lod == AISimulationLOD.LOD3_ABSTRACT


def test_lod_selection_by_distance_lod4():
    lod = determine_simulation_lod(75000.0)
    assert lod == AISimulationLOD.LOD4_FROZEN
