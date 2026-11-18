"""
Tests for Simulation Replay & Verification System (UAF-81.57 Sections 145-149, 226).
"""

import pytest
from uaf.universal_ai import (
    SimulationReplay,
    SimulationDefinition,
    UniversalAIFabricator,
)


def test_simulation_replay_creation():
    replay = SimulationReplay(
        replay_id="REPLAY_001",
        initial_seed=12345,
        total_ticks=100,
        final_hash="HASH_SAMPLE",
    )
    assert replay.replay_id == "REPLAY_001"
    assert replay.initial_seed == 12345
    assert replay.total_ticks == 100
    assert replay.final_hash == "HASH_SAMPLE"
    assert len(replay.inputs) == 0
    assert len(replay.recorded_events) == 0


def test_simulation_replay_recording_inputs():
    replay = SimulationReplay(replay_id="R_INP", initial_seed=999)
    replay.inputs.append({"tick": 1, "agent": "A1", "action": "MOVE"})
    replay.inputs.append({"tick": 2, "agent": "A2", "action": "ATTACK"})

    assert len(replay.inputs) == 2
    assert replay.inputs[0]["action"] == "MOVE"
    assert replay.inputs[1]["action"] == "ATTACK"


def test_simulation_replay_recording_events():
    replay = SimulationReplay(replay_id="R_EV", initial_seed=999)
    replay.recorded_events.append({"tick": 5, "event": "DAMAGE", "target": "A1", "amount": 20})

    assert len(replay.recorded_events) == 1
    assert replay.recorded_events[0]["event"] == "DAMAGE"


def test_simulation_replay_determinism():
    seed = 88888
    ticks = 10

    # Run 1
    sim1 = UniversalAIFabricator.create_golden_scenario(UniversalAIFabricator.GOLDEN_PATROL, seed=seed)
    for _ in range(ticks):
        UniversalAIFabricator.execute_simulation_tick(sim1, dt=0.033)
    hash1 = sim1.simulation_hash

    # Run 2
    sim2 = UniversalAIFabricator.create_golden_scenario(UniversalAIFabricator.GOLDEN_PATROL, seed=seed)
    for _ in range(ticks):
        UniversalAIFabricator.execute_simulation_tick(sim2, dt=0.033)
    hash2 = sim2.simulation_hash

    assert hash1 == hash2

    replay = SimulationReplay(
        replay_id="REPLAY_PATROL",
        initial_seed=seed,
        total_ticks=ticks,
        final_hash=hash1,
    )
    assert replay.final_hash == hash2


def test_simulation_replay_divergence_detection():
    # Run with different seeds
    sim1 = UniversalAIFabricator.create_golden_scenario(UniversalAIFabricator.GOLDEN_COMBAT, seed=1111)
    sim2 = UniversalAIFabricator.create_golden_scenario(UniversalAIFabricator.GOLDEN_COMBAT, seed=2222)

    for _ in range(5):
        UniversalAIFabricator.execute_simulation_tick(sim1, dt=0.033)
        UniversalAIFabricator.execute_simulation_tick(sim2, dt=0.033)

    assert sim1.simulation_hash != sim2.simulation_hash
