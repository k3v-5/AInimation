"""
GameplayScenarioFabricator manufactures playable scenarios, gameplay graphs, objectives, and encounters.
UAF-81.20 Sections 165, 179, 180, 182.
"""

from typing import Tuple, List, Dict, Any
from ..models.scenario_def import PlayableScenarioDefinition, GameModeType
from ..models.graph import GameplayGraph, GameplayNode, GameplayNodeType, GameplayEdge
from ..models.elements import ScenarioObjective, ObjectiveType, ScenarioEncounter, EncounterType


class GameplayScenarioFabricator:
    """
    Synthesizes complete playable scenario packages across canonical archetypes (Section 165).
    """

    @classmethod
    def build_linear_mission_scenario(
        cls,
        scenario_id: str = "Scen_LinearMission",
        world_id: str = "World_Canonical",
        seed: int = 101,
    ) -> Tuple[PlayableScenarioDefinition, GameplayGraph, List[ScenarioObjective], List[ScenarioEncounter], int]:
        """1. Linear Mission (Start -> Breach -> Encounter -> Hack -> Extraction)."""
        scen_def = PlayableScenarioDefinition(scenario_id, world_id, GameModeType.LINEAR, "NORMAL", seed)
        graph = GameplayGraph()
        graph.add_node(GameplayNode("Node_Start", GameplayNodeType.START, "Infiltration point"))
        graph.add_node(GameplayNode("Node_Obj1", GameplayNodeType.OBJECTIVE, "Infiltrate complex"))
        graph.add_node(GameplayNode("Node_Enc1", GameplayNodeType.ENCOUNTER, "Patrol squad ambush"))
        graph.add_node(GameplayNode("Node_CP1", GameplayNodeType.CHECKPOINT, "Mid-mission save point"))
        graph.add_node(GameplayNode("Node_Obj2", GameplayNodeType.OBJECTIVE, "Hack primary terminal"))
        graph.add_node(GameplayNode("Node_End", GameplayNodeType.END, "Extraction helicopter"))

        graph.add_edge("Node_Start", "Node_Obj1")
        graph.add_edge("Node_Obj1", "Node_Enc1")
        graph.add_edge("Node_Enc1", "Node_CP1")
        graph.add_edge("Node_CP1", "Node_Obj2")
        graph.add_edge("Node_Obj2", "Node_End")

        objectives = [
            ScenarioObjective("Obj_Infiltrate", ObjectiveType.REACH, "Gate_Alpha", is_primary=True, is_reachable=True),
            ScenarioObjective("Obj_HackTerminal", ObjectiveType.HACK, "Terminal_Main", is_primary=True, is_reachable=True),
        ]
        encounters = [
            ScenarioEncounter("Enc_PatrolAmbush", EncounterType.AMBUSH, enemy_count=6, is_solvable=True),
        ]
        return scen_def, graph, objectives, encounters, 1

    @classmethod
    def build_combat_arena_scenario(
        cls,
        scenario_id: str = "Scen_CombatArena",
        world_id: str = "World_Arena",
        seed: int = 202,
    ) -> Tuple[PlayableScenarioDefinition, GameplayGraph, List[ScenarioObjective], List[ScenarioEncounter], int]:
        """2. Combat Arena (Wave combat with survival objective)."""
        scen_def = PlayableScenarioDefinition(scenario_id, world_id, GameModeType.ARENA, "HARD", seed)
        graph = GameplayGraph()
        graph.add_node(GameplayNode("Node_Start", GameplayNodeType.START, "Arena entry gate"))
        graph.add_node(GameplayNode("Node_Wave1", GameplayNodeType.ENCOUNTER, "Wave 1 - Grunts"))
        graph.add_node(GameplayNode("Node_Wave2", GameplayNodeType.ENCOUNTER, "Wave 2 - Elites"))
        graph.add_node(GameplayNode("Node_End", GameplayNodeType.END, "Victory podium"))

        graph.add_edge("Node_Start", "Node_Wave1")
        graph.add_edge("Node_Wave1", "Node_Wave2")
        graph.add_edge("Node_Wave2", "Node_End")

        objectives = [
            ScenarioObjective("Obj_SurviveArena", ObjectiveType.SURVIVE, "Arena_Floor", is_primary=True, is_reachable=True),
        ]
        encounters = [
            ScenarioEncounter("Enc_Wave1", EncounterType.WAVE, enemy_count=8, is_solvable=True),
            ScenarioEncounter("Enc_Wave2", EncounterType.WAVE, enemy_count=12, is_solvable=True),
        ]
        return scen_def, graph, objectives, encounters, 1

    @classmethod
    def build_boss_arena_scenario(
        cls,
        scenario_id: str = "Scen_BossArena",
        world_id: str = "World_Dungeon",
        seed: int = 303,
    ) -> Tuple[PlayableScenarioDefinition, GameplayGraph, List[ScenarioObjective], List[ScenarioEncounter], int]:
        """3. Boss Arena (Pre-boss checkpoint -> Cinematic -> Boss battle -> Exit)."""
        scen_def = PlayableScenarioDefinition(scenario_id, world_id, GameModeType.BOSS, "NIGHTMARE", seed)
        graph = GameplayGraph()
        graph.add_node(GameplayNode("Node_Start", GameplayNodeType.START, "Throne room foyer"))
        graph.add_node(GameplayNode("Node_CP", GameplayNodeType.CHECKPOINT, "Pre-boss sanctuary"))
        graph.add_node(GameplayNode("Node_BossBattle", GameplayNodeType.BOSS, "Titan Golem Encounter"))
        graph.add_node(GameplayNode("Node_End", GameplayNodeType.END, "Treasure vault"))

        graph.add_edge("Node_Start", "Node_CP")
        graph.add_edge("Node_CP", "Node_BossBattle")
        graph.add_edge("Node_BossBattle", "Node_End")

        objectives = [
            ScenarioObjective("Obj_DefeatTitan", ObjectiveType.BOSS, "Boss_Titan_Golem", is_primary=True, is_reachable=True),
        ]
        encounters = [
            ScenarioEncounter("Enc_TitanBattle", EncounterType.BOSS, enemy_count=1, is_solvable=True),
        ]
        return scen_def, graph, objectives, encounters, 1

    @classmethod
    def build_exploration_scenario(
        cls,
        scenario_id: str = "Scen_Exploration",
        world_id: str = "World_OpenForest",
        seed: int = 404,
    ) -> Tuple[PlayableScenarioDefinition, GameplayGraph, List[ScenarioObjective], List[ScenarioEncounter], int]:
        """4. Exploration (Discover landmarks and retrieve artifacts)."""
        scen_def = PlayableScenarioDefinition(scenario_id, world_id, GameModeType.EXPLORATION, "NORMAL", seed)
        graph = GameplayGraph()
        graph.add_node(GameplayNode("Node_Start", GameplayNodeType.START, "Valley trailhead"))
        graph.add_node(GameplayNode("Node_ObjFind", GameplayNodeType.OBJECTIVE, "Locate ancient ruins"))
        graph.add_node(GameplayNode("Node_ObjCollect", GameplayNodeType.OBJECTIVE, "Collect relic"))
        graph.add_node(GameplayNode("Node_End", GameplayNodeType.END, "Research outpost"))

        graph.add_edge("Node_Start", "Node_ObjFind")
        graph.add_edge("Node_ObjFind", "Node_ObjCollect")
        graph.add_edge("Node_ObjCollect", "Node_End")

        objectives = [
            ScenarioObjective("Obj_FindRuins", ObjectiveType.REACH, "Ruins_Site", is_primary=True, is_reachable=True),
            ScenarioObjective("Obj_CollectRelic", ObjectiveType.COLLECT, "Relic_Stone", is_primary=True, is_reachable=True),
        ]
        encounters = [
            ScenarioEncounter("Enc_WildPredators", EncounterType.PATROL, enemy_count=3, is_solvable=True),
        ]
        return scen_def, graph, objectives, encounters, 2

    @classmethod
    def build_puzzle_scenario(
        cls,
        scenario_id: str = "Scen_PuzzleChamber",
        world_id: str = "World_Temple",
        seed: int = 505,
    ) -> Tuple[PlayableScenarioDefinition, GameplayGraph, List[ScenarioObjective], List[ScenarioEncounter], int]:
        """5. Puzzle Chamber (Activate runes in sequence to open portal)."""
        scen_def = PlayableScenarioDefinition(scenario_id, world_id, GameModeType.PUZZLE, "NORMAL", seed)
        graph = GameplayGraph()
        graph.add_node(GameplayNode("Node_Start", GameplayNodeType.START, "Chamber entrance"))
        graph.add_node(GameplayNode("Node_ActivateRune", GameplayNodeType.OBJECTIVE, "Activate 3 elemental runes"))
        graph.add_node(GameplayNode("Node_End", GameplayNodeType.END, "Ascension portal"))

        graph.add_edge("Node_Start", "Node_ActivateRune")
        graph.add_edge("Node_ActivateRune", "Node_End")

        objectives = [
            ScenarioObjective("Obj_ActivateRunes", ObjectiveType.ACTIVATE, "Rune_Pillar", is_primary=True, is_reachable=True),
        ]
        encounters = []
        return scen_def, graph, objectives, encounters, 1

    @classmethod
    def build_defense_scenario(
        cls,
        scenario_id: str = "Scen_BunkerDefense",
        world_id: str = "World_MilitaryBunker",
        seed: int = 606,
    ) -> Tuple[PlayableScenarioDefinition, GameplayGraph, List[ScenarioObjective], List[ScenarioEncounter], int]:
        """6. Defense Scenario (Protect command core against enemy waves)."""
        scen_def = PlayableScenarioDefinition(scenario_id, world_id, GameModeType.DEFENSE, "HARD", seed)
        graph = GameplayGraph()
        graph.add_node(GameplayNode("Node_Start", GameplayNodeType.START, "Command center interior"))
        graph.add_node(GameplayNode("Node_Holdout", GameplayNodeType.ENCOUNTER, "Siege wave holdout"))
        graph.add_node(GameplayNode("Node_End", GameplayNodeType.END, "Evacuation shuttle"))

        graph.add_edge("Node_Start", "Node_Holdout")
        graph.add_edge("Node_Holdout", "Node_End")

        objectives = [
            ScenarioObjective("Obj_ProtectCore", ObjectiveType.DEFEND, "Core_Reactor", is_primary=True, is_reachable=True),
        ]
        encounters = [
            ScenarioEncounter("Enc_SiegeForces", EncounterType.DEFENSE, enemy_count=16, is_solvable=True),
        ]
        return scen_def, graph, objectives, encounters, 1
