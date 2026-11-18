"""
Tests for Level Mission Models, Objectives, and Flow Metrics.
UAF-81.41 Sections 8, 9, 12, 13, 22, 26, 30, 31, 142.
"""

from uaf.level_mission.models.definition import (
    MissionNodeType41,
    ObjectiveType41,
    GameplayState41,
    CheckpointType41,
    TriggerType41,
    MissionFlowMetrics41,
    PlayableLevelSpecification,
)


def test_mission_flow_metrics_and_validity():
    metrics_ok = MissionFlowMetrics41(primary_objective_count=2, encounter_count=2, checkpoint_count=2, has_valid_player_start=True, has_extraction_or_end=True)
    assert metrics_ok.is_valid is True

    metrics_zero_obj = MissionFlowMetrics41(primary_objective_count=0)
    assert metrics_zero_obj.is_valid is False

    metrics_no_start = MissionFlowMetrics41(has_valid_player_start=False)
    assert metrics_no_start.is_valid is False

    metrics_no_end = MissionFlowMetrics41(has_extraction_or_end=False)
    assert metrics_no_end.is_valid is False


def test_playable_level_specification_and_hashing():
    spec = PlayableLevelSpecification(
        level_id="Level_Test_Raid",
        world_id="World_Test_Combat",
        mission_type=MissionNodeType41.COMBAT,
        metrics=MissionFlowMetrics41(primary_objective_count=3, encounter_count=4, checkpoint_count=3),
        ai_spaces_count=4,
        seed=654321,
    )

    assert spec.is_valid_mission is True
    assert len(spec.definition_hash) == 64
    data = spec.to_dict()
    assert data["mission_type"] == "COMBAT"
    assert data["ai_spaces_count"] == 4

    bad_spec_spaces = PlayableLevelSpecification(
        level_id="Level_NoAISpaces",
        world_id="World_Test_Combat",
        mission_type=MissionNodeType41.COMBAT,
        ai_spaces_count=0,
    )
    assert bad_spec_spaces.is_valid_mission is False
