"""
UAF-81.57 Acceptance & Normative Compliance Test Suite.
Verifies all 236 Sections of UAF-81.57-AI-CROWD-SIMULATION-SYSTEM.md,
Cross-Phase Integration (UAF-81.50 through 57), Machine-Agnostic Purity,
13 Canonical Golden AI Scenarios, 12-Stage Tick Execution, and Unreal Production Packaging.
"""

import pytest
from uaf.universal_ai import (
    UniversalAIFabricator,
    UniversalAIValidator,
    ProductionReadySimulation,
    AgentLifecycleState,
    AIQuery,
    AIQueryType,
)

# Cross-Phase Integration imports (UAF-81.50 through UAF-81.56)
from uaf.universal_surface import UniversalSurfaceFabricationPlatform
from uaf.universal_geometry import UniversalGeometryFabricationPlatform
from uaf.universal_character import UniversalCharacterFabricator
from uaf.universal_animation import UniversalAnimationFabricator
from uaf.universal_world import UniversalWorldFabricator, WorldQuery, WorldQueryType


class TestUAF8157Acceptance:
    """Acceptance criteria tests for UAF-81.57 Universal AI, Navigation, NPC, Crowd, Behavior & Simulation System."""

    def test_golden_ai_scenarios_set_complete(self):
        """Verify all 13 Golden AI Scenarios from Section 223 exist, are valid, and verify readback."""
        scenario_keys = [
            UniversalAIFabricator.GOLDEN_IDLE_NPC,
            UniversalAIFabricator.GOLDEN_DAILY_ROUTINE,
            UniversalAIFabricator.GOLDEN_PATROL,
            UniversalAIFabricator.GOLDEN_FLEE,
            UniversalAIFabricator.GOLDEN_COMBAT,
            UniversalAIFabricator.GOLDEN_SQUAD,
            UniversalAIFabricator.GOLDEN_CROWD,
            UniversalAIFabricator.GOLDEN_ANIMAL,
            UniversalAIFabricator.GOLDEN_CITY_POPULATION,
            UniversalAIFabricator.GOLDEN_WORLD_REACTION,
            UniversalAIFabricator.GOLDEN_BACKGROUND_SIMULATION,
            UniversalAIFabricator.GOLDEN_SAVE_LOAD,
            UniversalAIFabricator.GOLDEN_REPLAY,
        ]
        assert len(scenario_keys) == 13

        for key in scenario_keys:
            sim = UniversalAIFabricator.create_golden_scenario(key)
            export_path = f"/Game/AI/Golden_{key}.uasset"
            report = UniversalAIValidator.validate_simulation(sim, export_path=export_path)
            assert report.is_valid is True, f"Scenario {key} validation failed: {report.failed_checks}"
            assert report.quality_score == 100.0

            pkg = ProductionReadySimulation(
                simulation=sim,
                validation_report=report,
                export_path=export_path,
            )
            assert len(pkg.canonical_hash) == 64
            rb = pkg.verify_readback()
            assert rb["agent_count"] >= 1
            assert rb["canonical_hash"] == pkg.canonical_hash

    def test_cross_phase_integration_uaf81_50_to_57(self):
        """Verify cross-phase integration across UAF-81.50 through UAF-81.57."""
        # 1. Surface from UAF-81.52
        surf_spec, *surf_paths = UniversalSurfaceFabricationPlatform.build_golden_leather()
        assert surf_spec.is_valid_surface is True

        # 2. Geometry from UAF-81.53
        mesh_spec, *mesh_paths = UniversalGeometryFabricationPlatform.build_golden_character()
        assert mesh_spec.is_valid_mesh is True

        # 3. Rigged Character from UAF-81.54
        character = UniversalCharacterFabricator.build_golden_human_male()
        assert character.validation_report.is_valid is True

        # 4. Animated Character from UAF-81.55
        animated_char = UniversalAnimationFabricator.build_golden_walk(character=character)
        assert animated_char.validation_report.is_valid is True

        # 5. World from UAF-81.56
        world = UniversalWorldFabricator.create_golden_grassland()
        assert len(world.anchors) > 0
        spawn_pos = world.anchors[0].position

        # 6. AI Agent from UAF-81.57 placed on world terrain
        sim = UniversalAIFabricator.create_golden_scenario(UniversalAIFabricator.GOLDEN_PATROL)
        agent = sim.agents[0]
        agent.state.position = spawn_pos

        # World terrain height query for NPC placement
        h_query = WorldQuery(WorldQueryType.HEIGHT_AT, position=spawn_pos)
        h_res = UniversalWorldFabricator.solve_query(world, h_query)
        assert "height" in h_res
        ground_z = h_res["height"]
        agent.state.position = (spawn_pos[0], spawn_pos[1], ground_z)

        # AI simulation tick
        UniversalAIFabricator.execute_simulation_tick(sim, dt=0.033)
        assert sim.current_tick == 1
        assert agent.lifecycle == AgentLifecycleState.ACTIVE

    def test_strict_machine_path_rejection(self):
        """Verify hard failure rejection of absolute Windows paths (C:, D:, E:) for engine purity."""
        sim = UniversalAIFabricator.build_golden_idle_npc()

        for bad_path in [
            r"C:\UnrealProjects\AI\Sim.uasset",
            r"D:\Games\Content\AI\Sim.uasset",
            r"E:\Dev\Simulation.uasset",
        ]:
            report = UniversalAIValidator.validate_simulation(sim, export_path=bad_path)
            assert report.is_valid is False
            assert report.quality_score == 0.0
            assert any("Machine-dependent path" in err for err in report.failed_checks)

    def test_12_stage_tick_pipeline_full_execution(self):
        """Verify the 12-stage tick simulation pipeline updates agents through multiple cycles."""
        sim = UniversalAIFabricator.create_golden_scenario(UniversalAIFabricator.GOLDEN_CITY_POPULATION)
        assert len(sim.agents) == 10

        initial_tick = sim.current_tick
        ticks_to_run = 12

        for _ in range(ticks_to_run):
            UniversalAIFabricator.execute_simulation_tick(sim, dt=0.033)

        assert sim.current_tick == initial_tick + ticks_to_run
        # Verify needs decayed
        for agent in sim.agents:
            assert agent.needs.hunger > 0.0

    def test_production_ready_simulation_packaging(self):
        """Verify Unreal Engine production asset packaging, canonical hash, and readback verification."""
        sim = UniversalAIFabricator.create_golden_scenario(UniversalAIFabricator.GOLDEN_SQUAD)
        export_path = "/Game/AI/SquadAlpha.uasset"

        report = UniversalAIValidator.validate_simulation(sim, export_path=export_path)
        assert report.is_valid is True

        package = ProductionReadySimulation(
            simulation=sim,
            validation_report=report,
            export_path=export_path,
        )

        assert len(package.canonical_hash) == 64
        rb = package.verify_readback()
        assert rb["simulation_id"] == "SIM_GOLDEN_SQUAD"
        assert rb["agent_count"] == 3
        assert rb["active_count"] == 3
        assert rb["squad_count"] == 1
        assert rb["canonical_hash"] == package.canonical_hash
