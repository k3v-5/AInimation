"""
Tests for Universal Gameplay Mission and Checkpoint System.
"""
import pytest
from src.uaf.universal_gameplay.models.definition import (
    MissionDefinition,
    MissionPhase,
    MissionCheckpoint,
    MissionState,
    QuestObjective,
    ObjectiveType,
    ObjectiveState,
    GameplayCommand,
    GameplayCommandType,
    CommandFailureCode,
    GameplayState,
)
from src.uaf.universal_gameplay.engine.universal_gameplay_fabricator import (
    UniversalGameplayFabricator,
)


def test_mission_initialization():
    m = MissionDefinition(
        mission_id="mis_siege_01",
        title="Siege of Castle",
        phases=[
            MissionPhase("p1", "Breach the Gates"),
            MissionPhase("p2", "Defeat the Warlord"),
        ],
        checkpoints=[
            MissionCheckpoint("cp_gate", (100.0, 200.0, 0.0)),
            MissionCheckpoint("cp_throne", (500.0, 200.0, 50.0)),
        ]
    )
    assert m.mission_id == "mis_siege_01"
    assert len(m.phases) == 2
    assert len(m.checkpoints) == 2
    assert m.state == MissionState.NOT_STARTED
    assert m.current_phase_index == 0


def test_mission_state_transitions():
    m = MissionDefinition(mission_id="m1", title="Test Mission")
    assert m.state == MissionState.NOT_STARTED
    m.state = MissionState.IN_PROGRESS
    assert m.state == MissionState.IN_PROGRESS
    m.state = MissionState.COMPLETED
    assert m.state == MissionState.COMPLETED
    m.state = MissionState.FAILED
    assert m.state == MissionState.FAILED


def test_mission_phases_and_objectives():
    obj1 = QuestObjective("o1", "Plant explosives", ObjectiveType.INTERACT, "GATE", target_count=1)
    phase1 = MissionPhase(phase_id="p1", title="Sabotage", objectives=[obj1])
    assert not phase1.is_completed
    obj1.state = ObjectiveState.COMPLETED
    obj1.current_count = 1
    phase1.is_completed = True
    assert phase1.is_completed


def test_mission_checkpoints_tracking():
    cp = MissionCheckpoint("cp_alpha", (10.0, 20.0, 30.0), is_reached=False)
    assert not cp.is_reached
    assert cp.location == (10.0, 20.0, 30.0)
    cp.is_reached = True
    cp.timestamp = 42.5
    assert cp.is_reached
    assert cp.timestamp == 42.5


def test_start_mission_command():
    state = GameplayState("SIM_MISSION")
    mission = MissionDefinition(mission_id="m_escort", title="Escort Caravan")
    state.missions[mission.mission_id] = mission

    cmd = GameplayCommand(
        command_id="cmd_m1",
        source="player_1",
        target=mission.mission_id,
        command_type=GameplayCommandType.START_MISSION,
        payload={"mission_id": mission.mission_id},
    )
    res = UniversalGameplayFabricator.execute_command(state, cmd)
    assert res.success
    assert mission.state == MissionState.IN_PROGRESS


def test_complete_mission_command():
    state = GameplayState("SIM_MISSION")
    mission = MissionDefinition(
        mission_id="m_patrol",
        title="Patrol Valley",
        state=MissionState.IN_PROGRESS,
    )
    state.missions[mission.mission_id] = mission

    cmd = GameplayCommand(
        command_id="cmd_m2",
        source="player_1",
        target=mission.mission_id,
        command_type=GameplayCommandType.COMPLETE_MISSION,
        payload={"mission_id": mission.mission_id},
    )
    res = UniversalGameplayFabricator.execute_command(state, cmd)
    assert res.success
    assert mission.state == MissionState.COMPLETED


def test_mission_command_invalid_target():
    state = GameplayState("SIM_MISSION")
    cmd = GameplayCommand(
        command_id="cmd_fail",
        source="player_1",
        target="non_existent",
        command_type=GameplayCommandType.START_MISSION,
        payload={"mission_id": "non_existent"},
    )
    res = UniversalGameplayFabricator.execute_command(state, cmd)
    assert not res.success
    assert res.failure_code == CommandFailureCode.INVALID_TARGET


def test_mission_to_dict_and_from_dict():
    m = MissionDefinition(
        mission_id="m_recon",
        title="Recon Outpost",
        phases=[MissionPhase("p1", "Survey Perimeter")],
        checkpoints=[MissionCheckpoint("cp1", (0.0, 0.0, 0.0), is_reached=True, timestamp=10.0)],
        current_phase_index=0,
        state=MissionState.IN_PROGRESS,
    )
    d = {
        "mission_id": m.mission_id,
        "title": m.title,
        "state": m.state.value,
        "current_phase_index": m.current_phase_index,
        "phases": [{"phase_id": p.phase_id, "title": p.title, "is_completed": p.is_completed} for p in m.phases],
        "checkpoints": [{"checkpoint_id": c.checkpoint_id, "location": c.location, "is_reached": c.is_reached} for c in m.checkpoints]
    }
    assert d["mission_id"] == "m_recon"
    assert d["state"] == "IN_PROGRESS"
    assert len(d["phases"]) == 1
    assert len(d["checkpoints"]) == 1
