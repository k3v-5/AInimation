"""
Tests for Gameplay Scenario Models, Gameplay Graph, and Elements.
UAF-81.20 Sections 3, 4, 6, 7, 8, 9, 11, 12, 21, 22.
"""

from uaf.gameplay_scenario.models.scenario_def import (
    GameModeType,
    ScenarioLevelState,
    PlayableScenarioDefinition,
)
from uaf.gameplay_scenario.models.graph import (
    GameplayNodeType,
    GameplayNode,
    GameplayEdge,
    GameplayGraph,
)
from uaf.gameplay_scenario.models.elements import (
    ObjectiveType,
    ScenarioObjective,
    EncounterType,
    ScenarioEncounter,
)


def test_scenario_definition_and_hashing():
    scen = PlayableScenarioDefinition("Scen_StealthInfil", "World_Urban", GameModeType.MISSION, "HARD", seed=445566)
    assert scen.game_mode == "MISSION"
    assert scen.difficulty_tier == "HARD"
    assert len(scen.definition_hash) == 64
    data = scen.to_dict()
    assert data["game_mode"] == "MISSION"


def test_gameplay_graph_path_solvability():
    graph = GameplayGraph()
    graph.add_node(GameplayNode("Start", GameplayNodeType.START))
    graph.add_node(GameplayNode("Obj1", GameplayNodeType.OBJECTIVE))
    graph.add_node(GameplayNode("End", GameplayNodeType.END))

    # Missing edges: not solvable
    assert graph.has_start_and_end() is True
    assert graph.is_solvable_path_exists() is False

    # Connect Start -> Obj1 -> End
    graph.add_edge("Start", "Obj1")
    graph.add_edge("Obj1", "End")
    assert graph.is_solvable_path_exists() is True
