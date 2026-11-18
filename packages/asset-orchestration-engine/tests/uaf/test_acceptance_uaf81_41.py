"""
UAF-81.41 Acceptance Tests (Sections 142, 11, 19, 137, 155, 157, 158, 143, 166).
Verifies:
- Section 142: Final Acceptance Criteria (Generates and validates all 8 Golden Levels:
  Linear Mission, Open Exploration, Combat Mission, Stealth Mission, Boss Mission, Branching Mission, Defense Mission, Extraction Mission).
- Sections 11, 155, 158: Hard Fail Conditions Test (Zero tolerance for invalid mission flow, dead ends,
  missing player starts, zero checkpoints, or absolute machine-dependent paths; violations strictly flag MANUAL_REVIEW_REQUIRED).
"""

from uaf.level_mission.engine.level_mission_fabricator import LevelMissionFabricationPlatform
from uaf.level_mission.validation.level_mission_validator import LevelMissionValidator
from uaf.level_mission.models.definition import (
    PlayableLevelSpecification,
    MissionNodeType41,
    MissionFlowMetrics41,
)
from uaf.level_mission.package.level_mission_package import LevelMissionPackage


def test_final_level_mission_acceptance_section_142():
    """
    Acceptance Test Section 142:
    Synthesizes and validates all 8 Golden Levels.
    """
    builders = [
        ("Level_Gold_Linear", LevelMissionFabricationPlatform.build_golden_linear_mission),
        ("Level_Gold_OpenExploration", LevelMissionFabricationPlatform.build_golden_open_exploration),
        ("Level_Gold_Combat", LevelMissionFabricationPlatform.build_golden_combat_mission),
        ("Level_Gold_Stealth", LevelMissionFabricationPlatform.build_golden_stealth_mission),
        ("Level_Gold_Boss", LevelMissionFabricationPlatform.build_golden_boss_mission),
        ("Level_Gold_Branching", LevelMissionFabricationPlatform.build_golden_branching_mission),
        ("Level_Gold_Defense", LevelMissionFabricationPlatform.build_golden_defense_mission),
        ("Level_Gold_Extraction", LevelMissionFabricationPlatform.build_golden_extraction_mission),
    ]

    for level_id, builder_fn in builders:
        spec, mg_path, gp_path = builder_fn(level_id)
        assert spec.is_valid_mission is True

        report = LevelMissionValidator.validate_playable_level(spec, mg_path, gp_path)
        assert report.is_valid is True, f"Failed for {level_id}: {report.issues}"
        assert report.review_status == "PASSED"
        assert report.quality_score.aggregate_score >= 0.85

        pkg = LevelMissionPackage(
            level_id=level_id,
            spec=spec,
            mission_graph_path=mg_path,
            gameplay_package_path=gp_path,
            validation_report=report,
        )
        assert len(pkg.package_hash) == 64
        assert pkg.to_dict()["level_id"] == level_id


def test_hard_fail_conditions_section_11_155_158():
    """
    Acceptance Test Sections 11, 155, 158:
    Hard fail conditions:
    1. INVALID_MISSION_FLOW: Zero primary objectives or missing extraction/end.
    2. INVALID_PLAYER_START: has_valid_player_start is False.
    3. ZERO_CHECKPOINTS: checkpoint_count < 1 (softlock risk).
    4. Path purity: Absolute machine-dependent reference paths.
    Any violation strictly triggers review_status = MANUAL_REVIEW_REQUIRED.
    """
    spec, mg_path, gp_path = LevelMissionFabricationPlatform.build_golden_linear_mission("Level_Fault_Test")

    # 1. Flow violation: Zero objectives
    bad_metrics_obj = MissionFlowMetrics41(primary_objective_count=0)
    bad_spec_obj = PlayableLevelSpecification(
        "Level_ZeroObj",
        "World_Test",
        MissionNodeType41.OBJECTIVE,
        metrics=bad_metrics_obj,
    )
    rep_obj = LevelMissionValidator.validate_playable_level(bad_spec_obj, mg_path, gp_path)
    assert rep_obj.is_valid is False
    assert rep_obj.review_status == "MANUAL_REVIEW_REQUIRED"
    assert any("INVALID_MISSION_FLOW" in iss for iss in rep_obj.issues)

    # 2. Player start violation
    bad_metrics_start = MissionFlowMetrics41(has_valid_player_start=False)
    bad_spec_start = PlayableLevelSpecification(
        "Level_NoStart",
        "World_Test",
        MissionNodeType41.OBJECTIVE,
        metrics=bad_metrics_start,
    )
    rep_start = LevelMissionValidator.validate_playable_level(bad_spec_start, mg_path, gp_path)
    assert rep_start.is_valid is False
    assert rep_start.review_status == "MANUAL_REVIEW_REQUIRED"
    assert any("INVALID_PLAYER_START" in iss for iss in rep_start.issues)

    # 3. Checkpoint violation: 0 checkpoints (softlock)
    bad_metrics_cp = MissionFlowMetrics41(checkpoint_count=0)
    bad_spec_cp = PlayableLevelSpecification(
        "Level_ZeroCP",
        "World_Test",
        MissionNodeType41.OBJECTIVE,
        metrics=bad_metrics_cp,
    )
    rep_cp = LevelMissionValidator.validate_playable_level(bad_spec_cp, mg_path, gp_path)
    assert rep_cp.is_valid is False
    assert rep_cp.review_status == "MANUAL_REVIEW_REQUIRED"
    assert any("ZERO_CHECKPOINTS" in iss for iss in rep_cp.issues)

    # 4. Path purity violation: Absolute machine path
    bad_mg_path = "D:\\UnrealProjects\\Missions\\MG_Linear.uasset"
    rep_path = LevelMissionValidator.validate_playable_level(spec, bad_mg_path, gp_path)
    assert rep_path.is_valid is False
    assert rep_path.review_status == "MANUAL_REVIEW_REQUIRED"
    assert any("Absolute machine-dependent path" in iss for iss in rep_path.issues)
