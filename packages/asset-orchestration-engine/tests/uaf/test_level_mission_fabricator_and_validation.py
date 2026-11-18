"""
Tests for Level Mission Fabricator, Validator, and Package.
UAF-81.41 Sections 142, 143, 166.
"""

from uaf.level_mission.engine.level_mission_fabricator import LevelMissionFabricationPlatform
from uaf.level_mission.validation.level_mission_validator import LevelMissionValidator
from uaf.level_mission.package.level_mission_package import LevelMissionPackage


def test_level_mission_fabrication_all_eight_golden_levels():
    builders = [
        LevelMissionFabricationPlatform.build_golden_linear_mission,
        LevelMissionFabricationPlatform.build_golden_open_exploration,
        LevelMissionFabricationPlatform.build_golden_combat_mission,
        LevelMissionFabricationPlatform.build_golden_stealth_mission,
        LevelMissionFabricationPlatform.build_golden_boss_mission,
        LevelMissionFabricationPlatform.build_golden_branching_mission,
        LevelMissionFabricationPlatform.build_golden_defense_mission,
        LevelMissionFabricationPlatform.build_golden_extraction_mission,
    ]

    for builder in builders:
        spec, mg_path, gp_path = builder()
        assert spec.is_valid_mission is True
        assert mg_path.startswith("/Game/Missions/Graphs/")
        assert gp_path.startswith("/Game/Missions/Packages/")


def test_level_mission_package_validation_and_serialization():
    spec, mg_path, gp_path = LevelMissionFabricationPlatform.build_golden_linear_mission("Level_PkgLinear")

    report = LevelMissionValidator.validate_playable_level(spec, mg_path, gp_path)
    assert report.is_valid is True
    assert report.review_status == "PASSED"
    assert report.quality_score.aggregate_score >= 0.85

    pkg = LevelMissionPackage(
        level_id="Level_PkgLinear",
        spec=spec,
        mission_graph_path=mg_path,
        gameplay_package_path=gp_path,
        validation_report=report,
    )

    assert len(pkg.package_hash) == 64
    data = pkg.to_dict()
    assert data["level_id"] == "Level_PkgLinear"
    assert data["spec"]["mission_type"] == "OBJECTIVE"
    assert data["validation_report"]["review_status"] == "PASSED"
