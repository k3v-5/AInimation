"""
Tests for Spatial Index & AI Query System (UAF-81.57 Sections 173-178, 226).
"""

import pytest
from uaf.universal_ai import (
    AIQueryType,
    AIQuery,
    AIAgent,
    AgentProfile,
    CoverPoint,
    InteractableDefinition,
    AIInteractionType,
    SimulationDefinition,
    UniversalAIFabricator,
)


def test_ai_query_types_enum():
    types = {q.value for q in AIQueryType}
    expected = {
        "NEAREST_AGENT",
        "VISIBLE_TARGETS",
        "THREATS",
        "ALLIES",
        "COVER",
        "SAFE_LOCATION",
        "PATH",
        "INTERACTABLES",
        "POPULATION",
    }
    assert types == expected


def test_solve_query_nearest_agent():
    prof = AgentProfile("P_QUERY")
    a1 = UniversalAIFabricator.spawn_agent("NEARBY", prof, (100.0, 0.0, 0.0))
    a2 = UniversalAIFabricator.spawn_agent("FAR", prof, (500.0, 0.0, 0.0))

    sim = SimulationDefinition("SIM_QUERY", agents=[a1, a2])
    query = AIQuery(query_type=AIQueryType.NEAREST_AGENT, origin=(0.0, 0.0, 0.0), radius=1000.0)

    res = UniversalAIFabricator.solve_ai_query(sim, query)
    assert len(res) == 1
    assert res[0]["agent_id"] == "NEARBY"
    assert round(res[0]["distance"], 1) == 100.0


def test_solve_query_nearest_agent_none_in_radius():
    prof = AgentProfile("P_QUERY")
    a = UniversalAIFabricator.spawn_agent("FAR_AWAY", prof, (3000.0, 0.0, 0.0))

    sim = SimulationDefinition("SIM_NO_RESULT", agents=[a])
    query = AIQuery(query_type=AIQueryType.NEAREST_AGENT, origin=(0.0, 0.0, 0.0), radius=1000.0)

    res = UniversalAIFabricator.solve_ai_query(sim, query)
    assert len(res) == 0


def test_solve_query_visible_targets():
    prof = AgentProfile("P_QUERY")
    a1 = UniversalAIFabricator.spawn_agent("T1", prof, (100.0, 0.0, 0.0))
    a2 = UniversalAIFabricator.spawn_agent("T2", prof, (200.0, 0.0, 0.0))
    a3 = UniversalAIFabricator.spawn_agent("T3", prof, (2000.0, 0.0, 0.0))

    sim = SimulationDefinition("SIM_TARGETS", agents=[a1, a2, a3])
    query = AIQuery(query_type=AIQueryType.VISIBLE_TARGETS, origin=(0.0, 0.0, 0.0), radius=500.0)

    res = UniversalAIFabricator.solve_ai_query(sim, query)
    assert len(res) == 2
    ids = {r["agent_id"] for r in res}
    assert ids == {"T1", "T2"}


def test_solve_query_cover_points():
    c1 = CoverPoint("COV_1", position=(150.0, 0.0, 0.0), normal=(0.0, 1.0, 0.0), protection_score=0.8)
    c2 = CoverPoint("COV_2", position=(250.0, 0.0, 0.0), normal=(0.0, 1.0, 0.0), is_occupied=True)
    c3 = CoverPoint("COV_3", position=(1500.0, 0.0, 0.0), normal=(0.0, 1.0, 0.0), protection_score=0.9)

    sim = SimulationDefinition("SIM_COV", cover_points=[c1, c2, c3])
    query = AIQuery(query_type=AIQueryType.COVER, origin=(0.0, 0.0, 0.0), radius=500.0)

    res = UniversalAIFabricator.solve_ai_query(sim, query)
    # Only c1 is within radius 500 and not occupied
    assert len(res) == 1
    assert res[0]["cover_id"] == "COV_1"
    assert res[0]["protection"] == 0.8


def test_solve_query_interactables():
    i1 = InteractableDefinition("BENCH", AIInteractionType.SIT, position=(100.0, 0.0, 0.0))
    i2 = InteractableDefinition("CHEST", AIInteractionType.OPEN, position=(200.0, 0.0, 0.0))
    i3 = InteractableDefinition("FAR_DOOR", AIInteractionType.USE, position=(3000.0, 0.0, 0.0))

    sim = SimulationDefinition("SIM_INTERACTABLES", interactables=[i1, i2, i3])
    query = AIQuery(query_type=AIQueryType.INTERACTABLES, origin=(0.0, 0.0, 0.0), radius=1000.0)

    res = UniversalAIFabricator.solve_ai_query(sim, query)
    assert len(res) == 2
    ids = {r["interactable_id"] for r in res}
    assert ids == {"BENCH", "CHEST"}
