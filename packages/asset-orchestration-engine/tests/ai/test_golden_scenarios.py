"""
Tests for 13 Canonical Golden AI Scenarios (UAF-81.57 Sections 223, 226).
"""

import pytest
from uaf.universal_ai import (
    UniversalAIFabricator,
    UniversalAIValidator,
    AgentLifecycleState,
)


def test_golden_01_idle_npc():
    sim = UniversalAIFabricator.create_golden_scenario(UniversalAIFabricator.GOLDEN_IDLE_NPC)
    assert sim.simulation_id == "SIM_GOLDEN_IDLE_NPC"
    assert len(sim.agents) == 1
    assert sim.agents[0].agent_id == "GOLDEN_IDLE_NPC"

    report = UniversalAIValidator.validate_simulation(sim, export_path="/Game/AI/IdleNPC.uasset")
    assert report.is_valid is True
    assert report.quality_score == 100.0

    UniversalAIFabricator.execute_simulation_tick(sim)
    assert sim.current_tick == 1


def test_golden_02_daily_routine():
    sim = UniversalAIFabricator.create_golden_scenario(UniversalAIFabricator.GOLDEN_DAILY_ROUTINE)
    assert sim.simulation_id == "SIM_GOLDEN_DAILY_ROUTINE"
    assert sim.agents[0].schedule is not None
    assert len(sim.agents[0].schedule.entries) == 5

    report = UniversalAIValidator.validate_simulation(sim, export_path="/Game/AI/RoutineNPC.uasset")
    assert report.is_valid is True
    assert report.quality_score == 100.0

    UniversalAIFabricator.execute_simulation_tick(sim)
    assert sim.current_tick == 1


def test_golden_03_patrol():
    sim = UniversalAIFabricator.create_golden_scenario(UniversalAIFabricator.GOLDEN_PATROL)
    assert sim.simulation_id == "SIM_GOLDEN_PATROL"
    assert sim.agents[0].fsm is not None
    assert sim.agents[0].current_fsm_state == "PATROL"

    report = UniversalAIValidator.validate_simulation(sim, export_path="/Game/AI/PatrolNPC.uasset")
    assert report.is_valid is True
    assert report.quality_score == 100.0

    UniversalAIFabricator.execute_simulation_tick(sim)
    assert sim.current_tick == 1


def test_golden_04_flee():
    sim = UniversalAIFabricator.create_golden_scenario(UniversalAIFabricator.GOLDEN_FLEE)
    assert sim.simulation_id == "SIM_GOLDEN_FLEE"
    assert len(sim.agents) == 2

    report = UniversalAIValidator.validate_simulation(sim, export_path="/Game/AI/FleeSim.uasset")
    assert report.is_valid is True
    assert report.quality_score == 100.0

    UniversalAIFabricator.execute_simulation_tick(sim)
    assert sim.current_tick == 1


def test_golden_05_combat():
    sim = UniversalAIFabricator.create_golden_scenario(UniversalAIFabricator.GOLDEN_COMBAT)
    assert sim.simulation_id == "SIM_GOLDEN_COMBAT"
    assert len(sim.agents) == 2
    assert len(sim.cover_points) == 1

    report = UniversalAIValidator.validate_simulation(sim, export_path="/Game/AI/CombatSim.uasset")
    assert report.is_valid is True
    assert report.quality_score == 100.0

    UniversalAIFabricator.execute_simulation_tick(sim)
    assert sim.current_tick == 1


def test_golden_06_squad():
    sim = UniversalAIFabricator.create_golden_scenario(UniversalAIFabricator.GOLDEN_SQUAD)
    assert sim.simulation_id == "SIM_GOLDEN_SQUAD"
    assert len(sim.agents) == 3
    assert len(sim.squads) == 1
    assert sim.squads[0].leader_id == "SQUAD_LEADER"

    report = UniversalAIValidator.validate_simulation(sim, export_path="/Game/AI/SquadSim.uasset")
    assert report.is_valid is True
    assert report.quality_score == 100.0

    UniversalAIFabricator.execute_simulation_tick(sim)
    assert sim.current_tick == 1


def test_golden_07_crowd():
    sim = UniversalAIFabricator.create_golden_scenario(UniversalAIFabricator.GOLDEN_CROWD)
    assert sim.simulation_id == "SIM_GOLDEN_CROWD"
    assert len(sim.agents) == 20

    report = UniversalAIValidator.validate_simulation(sim, export_path="/Game/AI/CrowdSim.uasset")
    assert report.is_valid is True
    assert report.quality_score == 100.0

    UniversalAIFabricator.execute_simulation_tick(sim)
    assert sim.current_tick == 1


def test_golden_08_animal():
    sim = UniversalAIFabricator.create_golden_scenario(UniversalAIFabricator.GOLDEN_ANIMAL)
    assert sim.simulation_id == "SIM_GOLDEN_ANIMAL"
    assert len(sim.territories) == 1

    report = UniversalAIValidator.validate_simulation(sim, export_path="/Game/AI/AnimalSim.uasset")
    assert report.is_valid is True
    assert report.quality_score == 100.0

    UniversalAIFabricator.execute_simulation_tick(sim)
    assert sim.current_tick == 1


def test_golden_09_city_population():
    sim = UniversalAIFabricator.create_golden_scenario(UniversalAIFabricator.GOLDEN_CITY_POPULATION)
    assert sim.simulation_id == "SIM_GOLDEN_CITY"
    assert len(sim.agents) == 10
    assert len(sim.interactables) == 1

    report = UniversalAIValidator.validate_simulation(sim, export_path="/Game/AI/CitySim.uasset")
    assert report.is_valid is True
    assert report.quality_score == 100.0

    UniversalAIFabricator.execute_simulation_tick(sim)
    assert sim.current_tick == 1


def test_golden_10_world_reaction():
    sim = UniversalAIFabricator.create_golden_scenario(UniversalAIFabricator.GOLDEN_WORLD_REACTION)
    assert sim.simulation_id == "SIM_GOLDEN_REACTION"

    report = UniversalAIValidator.validate_simulation(sim, export_path="/Game/AI/ReactionSim.uasset")
    assert report.is_valid is True
    assert report.quality_score == 100.0

    UniversalAIFabricator.execute_simulation_tick(sim)
    assert sim.current_tick == 1


def test_golden_11_background_simulation():
    sim = UniversalAIFabricator.create_golden_scenario(UniversalAIFabricator.GOLDEN_BACKGROUND_SIMULATION)
    assert sim.simulation_id == "SIM_GOLDEN_BG"
    assert sim.agents[0].profile.simulation_lod == 2

    report = UniversalAIValidator.validate_simulation(sim, export_path="/Game/AI/BgSim.uasset")
    assert report.is_valid is True
    assert report.quality_score == 100.0

    UniversalAIFabricator.execute_simulation_tick(sim)
    assert sim.current_tick == 1


def test_golden_12_save_load():
    sim = UniversalAIFabricator.create_golden_scenario(UniversalAIFabricator.GOLDEN_SAVE_LOAD)
    assert sim.simulation_id == "SIM_GOLDEN_SAVELOAD"

    report = UniversalAIValidator.validate_simulation(sim, export_path="/Game/AI/SaveLoadSim.uasset")
    assert report.is_valid is True
    assert report.quality_score == 100.0

    agent = sim.agents[0]
    saved = UniversalAIFabricator.save_agent(agent)
    agent.state.health = 10.0
    UniversalAIFabricator.load_agent(agent, saved)
    assert agent.state.health == 75.0


def test_golden_13_replay():
    sim = UniversalAIFabricator.create_golden_scenario(UniversalAIFabricator.GOLDEN_REPLAY)
    assert sim.simulation_id == "SIM_GOLDEN_REPLAY"

    report = UniversalAIValidator.validate_simulation(sim, export_path="/Game/AI/ReplaySim.uasset")
    assert report.is_valid is True
    assert report.quality_score == 100.0

    UniversalAIFabricator.execute_simulation_tick(sim)
    assert sim.current_tick == 1
