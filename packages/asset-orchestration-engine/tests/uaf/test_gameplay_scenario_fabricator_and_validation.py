"""
Tests for Gameplay Scenario Fabricator, Validator, and Package.
UAF-81.20 Sections 163, 165, 180, 182.
"""

from uaf.gameplay_scenario.engine.scenario_fabricator import GameplayScenarioFabricator
from uaf.gameplay_scenario.validation.scenario_validator import GameplayScenarioValidator
from uaf.gameplay_scenario.package.scenario_package import PlayableScenarioPackage


def test_gameplay_scenario_fabrication_canonical_archetypes():
    archetypes = [
        GameplayScenarioFabricator.build_linear_mission_scenario,
        GameplayScenarioFabricator.build_combat_arena_scenario,
        GameplayScenarioFabricator.build_boss_arena_scenario,
        GameplayScenarioFabricator.build_exploration_scenario,
        GameplayScenarioFabricator.build_puzzle_scenario,
        GameplayScenarioFabricator.build_defense_scenario,
    ]

    for builder in archetypes:
        scen_def, graph, objectives, encounters, cp_count = builder()
        assert graph.has_start_and_end() is True
        assert graph.is_solvable_path_exists() is True
        assert len(objectives) > 0 or len(encounters) > 0


def test_playable_scenario_package_validation_and_serialization():
    scen_def, graph, objectives, encounters, cp_count = GameplayScenarioFabricator.build_linear_mission_scenario("Scen_PkgTest")

    report = GameplayScenarioValidator.validate_scenario(scen_def, graph, objectives, encounters, cp_count)
    assert report.is_valid is True
    assert report.review_status == "PASSED"
    assert report.quality_score.aggregate_score >= 0.85

    pkg = PlayableScenarioPackage(
        asset_id="Scen_PkgTest",
        scenario_def=scen_def,
        gameplay_graph=graph,
        objectives=objectives,
        encounters=encounters,
        checkpoints_count=cp_count,
        validation_report=report,
    )

    assert len(pkg.package_hash) == 64
    data = pkg.to_dict()
    assert data["asset_id"] == "Scen_PkgTest"
    assert data["scenario_def"]["game_mode"] == "LINEAR"
    assert data["validation_report"]["review_status"] == "PASSED"
