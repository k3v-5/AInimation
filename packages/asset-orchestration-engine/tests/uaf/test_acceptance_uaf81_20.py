"""
UAF-81.20 Acceptance Tests (Sections 165, 18, 19, 153, 155, 180).
Verifies:
- Section 165: Final Acceptance Criteria (Generates and validates all canonical golden scenarios:
  Linear Mission, Combat Arena, Boss Arena, Exploration, Puzzle, Defense).
- Sections 18, 19, 153, 155: Non-Negotiable Requirements Test (Zero tolerance for graph hardlocks,
  unreachable primary objectives [softlocks], or unwinnable encounters; violations strictly flag MANUAL_REVIEW_REQUIRED).
"""

from uaf.gameplay_scenario.engine.scenario_fabricator import GameplayScenarioFabricator
from uaf.gameplay_scenario.validation.scenario_validator import GameplayScenarioValidator
from uaf.gameplay_scenario.models.graph import GameplayGraph, GameplayNode, GameplayNodeType
from uaf.gameplay_scenario.models.elements import ScenarioObjective, ObjectiveType, ScenarioEncounter, EncounterType
from uaf.gameplay_scenario.package.scenario_package import PlayableScenarioPackage


def test_final_gameplay_scenario_acceptance_section_165():
    """
    Acceptance Test Section 165:
    Synthesizes and validates all canonical golden scenarios.
    """
    builders = [
        ("Scen_Golden_Linear", GameplayScenarioFabricator.build_linear_mission_scenario),
        ("Scen_Golden_Arena", GameplayScenarioFabricator.build_combat_arena_scenario),
        ("Scen_Golden_Boss", GameplayScenarioFabricator.build_boss_arena_scenario),
        ("Scen_Golden_Exploration", GameplayScenarioFabricator.build_exploration_scenario),
        ("Scen_Golden_Puzzle", GameplayScenarioFabricator.build_puzzle_scenario),
        ("Scen_Golden_Defense", GameplayScenarioFabricator.build_defense_scenario),
    ]

    for asset_id, builder_fn in builders:
        scen_def, graph, objectives, encounters, cp_count = builder_fn(asset_id)
        assert graph.has_start_and_end() is True
        assert graph.is_solvable_path_exists() is True

        report = GameplayScenarioValidator.validate_scenario(scen_def, graph, objectives, encounters, cp_count)
        assert report.is_valid is True, f"Failed for {asset_id}: {report.issues}"
        assert report.review_status == "PASSED"
        assert report.quality_score.aggregate_score >= 0.85

        pkg = PlayableScenarioPackage(
            asset_id=asset_id,
            scenario_def=scen_def,
            gameplay_graph=graph,
            objectives=objectives,
            encounters=encounters,
            checkpoints_count=cp_count,
            validation_report=report,
        )
        assert len(pkg.package_hash) == 64
        assert pkg.to_dict()["asset_id"] == asset_id


def test_non_negotiable_requirements_section_18_19_153_155():
    """
    Acceptance Test Sections 18, 19, 153, 155:
    Non-negotiable requirements:
    1. Section 153 & 157: Graph without reachable path to END (hardlock) strictly fails.
    2. Section 18 & 19: Unreachable primary objective (softlock) strictly fails.
    3. Section 155: Encounter marked unwinnable strictly fails.
    Any violation strictly triggers review_status = MANUAL_REVIEW_REQUIRED.
    """
    scen_def, graph, objectives, encounters, cp_count = GameplayScenarioFabricator.build_linear_mission_scenario("Scen_Fault_Test")

    # 1. Section 153 & 157 violation: Hardlock - broken graph edge to END
    bad_graph_hardlock = GameplayGraph()
    bad_graph_hardlock.add_node(GameplayNode("Start", GameplayNodeType.START))
    bad_graph_hardlock.add_node(GameplayNode("Middle", GameplayNodeType.OBJECTIVE))
    bad_graph_hardlock.add_node(GameplayNode("End", GameplayNodeType.END))
    bad_graph_hardlock.add_edge("Start", "Middle")
    # Missing edge from Middle to End -> No path to END!
    rep_hardlock = GameplayScenarioValidator.validate_scenario(scen_def, bad_graph_hardlock, objectives, encounters, cp_count)
    assert rep_hardlock.is_valid is False
    assert rep_hardlock.review_status == "MANUAL_REVIEW_REQUIRED"
    assert any("hardlock detected" in iss for iss in rep_hardlock.issues)

    # 2. Section 18 & 19 violation: Softlock - unreachable primary objective
    bad_objectives_softlock = [
        ScenarioObjective("Obj_Critical", ObjectiveType.HACK, "Server_01", is_primary=True, is_reachable=False),
    ]
    rep_softlock = GameplayScenarioValidator.validate_scenario(scen_def, graph, bad_objectives_softlock, encounters, cp_count)
    assert rep_softlock.is_valid is False
    assert rep_softlock.review_status == "MANUAL_REVIEW_REQUIRED"
    assert any("softlock detected" in iss for iss in rep_softlock.issues)

    # 3. Section 155 violation: Unwinnable encounter
    bad_encounters_unwinnable = [
        ScenarioEncounter("Enc_ImpossibleBoss", EncounterType.BOSS, enemy_count=1, is_solvable=False),
    ]
    rep_unwinnable = GameplayScenarioValidator.validate_scenario(scen_def, graph, objectives, bad_encounters_unwinnable, cp_count)
    assert rep_unwinnable.is_valid is False
    assert rep_unwinnable.review_status == "MANUAL_REVIEW_REQUIRED"
    assert any("unwinnable/unsolvable" in iss for iss in rep_unwinnable.issues)
