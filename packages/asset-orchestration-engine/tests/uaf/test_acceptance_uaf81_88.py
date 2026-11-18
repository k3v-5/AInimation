"""Acceptance tests for UAF-81.88: Universal Production Golden Vertical Slice
& Autonomous Certification System.
"""

from __future__ import annotations
import pytest
from typing import Dict, Any

from uaf.golden_slice import (
    QualityProfile,
    CertificationLevel,
    PlatformType,
    BuildState,
    WorldConfig,
    PlayerConfig,
    EnemyConfig,
    GameplayConfig,
    MultiplayerConfig,
    PerformanceBudgetConfig,
    GoldenSliceManifest,
    SeedManager,
    GenerationTask,
    TaskType,
    GenerationDAG,
    CyclicDependencyError,
    WorldGenerator,
    WorldSlice,
    SpawnPoint,
    CharacterGenerator,
    CharacterSlice,
    CharacterProfile,
    GameplayGenerator,
    GameplaySlice,
    CombatAction,
    InventoryItem,
    ObjectiveState,
    VFXGenerator,
    VFXSlice,
    NiagaraSystemDescriptor,
    AudioGenerator,
    AudioSlice,
    SoundCueDescriptor,
    CinematicGenerator,
    CinematicSlice,
    CinematicKeyframe,
    UIGenerator,
    UISlice,
    AccessibilitySettings,
    ScenarioStep,
    ScenarioDefinition,
    create_golden_main_scenario,
    create_extended_stress_scenario,
    create_determinism_scenario,
    create_recovery_scenario,
    GoldenSliceBot,
    BotActionResult,
    BotExecutionReport,
    QATestResult,
    QARunner,
    QASuiteReport,
    TraceRecord,
    ReplayEngine,
    DeterminismRunResult,
    DeterminismComparisonReport,
    DeterminismVerifier,
    PerformanceBudget,
    BudgetComplianceReport,
    GoldenSliceProfiler,
    ProfilingSummary,
    SubsystemFrameCost,
    MultiplayerReplicationHarness,
    NetworkClientState,
    MultiplayerTestReport,
    VisualDiffResult,
    VisualRegressionReport,
    VisualRegressionVerifier,
    AudioEventMetric,
    AudioRegressionReport,
    AudioRegressionVerifier,
    FailureDiagnosis,
    FailureAnalyzer,
    KnowledgeEntry,
    FailureKnowledgeBase,
    RegressionTestRecord,
    RepairExecutionResult,
    SelfRepairEngine,
    ArtifactEntry,
    ArtifactManifest,
    BuildManifest,
    CookValidationResult,
    PackageResult,
    SlicePackager,
    GateEvaluation,
    GatekeeperResult,
    CertificationGatekeeper,
    GoldenSliceCertificationReport,
    HTMLReportGenerator,
    EvidencePackage,
    FailureArtifact,
    GoldenSliceOrchestrator,
    run_cli,
)


class TestManifestAndSeeds:
    """Tests declarative project manifest and deterministic seed isolation."""

    def test_manifest_models_and_declarative_specification(self):
        manifest = GoldenSliceManifest(
            project_id="AegisAscent",
            seed=4242,
            quality_profile=QualityProfile.GOLDEN,
        )
        data = manifest.to_dict()
        assert data["project_id"] == "AegisAscent"
        assert data["seed"] == 4242
        assert data["quality_profile"] == "GOLDEN"
        assert manifest.quality_profile_as_level() == CertificationLevel.GOLD
        assert manifest.feature_flags["niagara"] is True
        assert manifest.feature_flags["world_partition"] is True

    def test_seed_manager_isolation_and_determinism(self):
        sm1 = SeedManager(global_seed=9999)
        sm2 = SeedManager(global_seed=9999)
        sm3 = SeedManager(global_seed=1111)

        # Same global seed must yield identical domain seeds
        assert sm1.world_seed == sm2.world_seed
        assert sm1.character_seed == sm2.character_seed
        assert sm1.vfx_seed == sm2.vfx_seed

        # Different global seed must yield distinct domain seeds
        assert sm1.world_seed != sm3.world_seed

        # Isolated domain RNG stream consistency
        rng_world1 = sm1.get_rng("world")
        rng_world2 = sm2.get_rng("world")
        rng_vfx = sm1.get_rng("vfx")

        draws_w1 = [rng_world1.random() for _ in range(5)]
        draws_w2 = [rng_world2.random() for _ in range(5)]
        draws_vfx = [rng_vfx.random() for _ in range(5)]

        assert draws_w1 == draws_w2
        assert draws_w1 != draws_vfx  # Isolation between world and vfx domains


class TestPlannerAndGenerationDAG:
    """Tests generation DAG, dependency resolution, and Kahn's topological sort."""

    def test_generation_dag_topological_sort_and_cycle_detection(self):
        manifest = GoldenSliceManifest()
        dag = GenerationDAG.build_standard_dag(manifest)
        assert dag.count >= 15

        order = dag.topological_order()
        task_ids = [t.task_id for t in order]

        # Verify dependency ordering invariants (Section 8)
        assert task_ids.index("char_skeleton") < task_ids.index("char_animation")
        assert task_ids.index("char_animation") < task_ids.index("char_animbp")
        assert task_ids.index("char_animbp") < task_ids.index("char_player")
        assert task_ids.index("world_terrain") < task_ids.index("world_vegetation")
        assert task_ids.index("char_player") < task_ids.index("gameplay_combat")

        # Test cyclic dependency detection
        cyclic_dag = GenerationDAG()
        cyclic_dag.add_task(GenerationTask("A", TaskType.WORLD_TERRAIN, ["B"]))
        cyclic_dag.add_task(GenerationTask("B", TaskType.WORLD_VEGETATION, ["A"]))
        with pytest.raises(CyclicDependencyError):
            cyclic_dag.topological_order()


class TestSubsystemGenerators:
    """Tests generation of world, characters, combat, VFX, audio, cinematics, and UI."""

    def test_world_generator_biomes_streaming_and_spawn_points(self):
        manifest = GoldenSliceManifest()
        seeds = SeedManager(manifest.seed)
        gen = WorldGenerator(manifest.world, seeds)
        world_slice = gen.generate()

        assert world_slice.biome_name == "temperate_forest"
        assert world_slice.size_km == 4.0
        assert world_slice.streaming_cells_count >= 4
        assert len(world_slice.spawn_points) >= 6

        # Validation checks
        validation_errors = world_slice.validate()
        assert len(validation_errors) == 0

    def test_character_generator_player_and_enemy_archetypes(self):
        manifest = GoldenSliceManifest()
        seeds = SeedManager(manifest.seed)
        gen = CharacterGenerator(manifest.player, manifest.enemy, seeds)
        char_slice = gen.generate()

        assert char_slice.player.archetype == "humanoid"
        assert char_slice.player.health == 100.0
        assert len(char_slice.enemies) == 4

        # Differentiated archetypes (Section 18)
        scout = char_slice.enemies["scout"]
        heavy = char_slice.enemies["heavy"]
        assert scout.walk_speed > heavy.walk_speed
        assert heavy.health > scout.health
        assert heavy.attack_damage > scout.attack_damage

    def test_gameplay_generator_combat_actions_inventory_objective(self):
        manifest = GoldenSliceManifest()
        seeds = SeedManager(manifest.seed)
        gen = GameplayGenerator(manifest.gameplay, seeds)
        gp_slice = gen.generate()

        assert "light_attack" in gp_slice.actions
        assert "heavy_attack" in gp_slice.actions
        assert len(gp_slice.initial_inventory) == 3

        # Deterministic damage calculations (Section 21 & 22)
        dmg_normal = gp_slice.compute_damage("light_attack", attacker_base=35.0)
        dmg_crit = gp_slice.compute_damage("light_attack", attacker_base=35.0, is_critical=True)
        dmg_blocked = gp_slice.compute_damage("light_attack", attacker_base=35.0, is_blocked=True)

        assert dmg_normal == 55.0  # 20 + 35
        assert dmg_crit == 82.5    # 55 * 1.5
        assert dmg_blocked == 16.5  # 55 * 0.3

        # Objective progression
        gp_slice.objective.progress(50)
        assert gp_slice.objective.current_score == 50
        assert not gp_slice.objective.is_completed
        gp_slice.objective.progress(50)
        assert gp_slice.objective.is_completed

    def test_vfx_generator_10_golden_niagara_systems(self):
        seeds = SeedManager(1337)
        gen = VFXGenerator(seeds)
        vfx_slice = gen.generate()

        assert len(vfx_slice.systems) == 10
        errors = vfx_slice.validate()
        assert len(errors) == 0
        assert "muzzle_flash" in vfx_slice.systems
        assert "blood_damage" in vfx_slice.systems
        assert "weather" in vfx_slice.systems
        assert vfx_slice.systems["weather"].sim_target == "GPUSim"

    def test_audio_generator_spatialized_sound_cues(self):
        seeds = SeedManager(1337)
        gen = AudioGenerator(seeds)
        audio_slice = gen.generate()

        assert len(audio_slice.cues) == 8
        errors = audio_slice.validate()
        assert len(errors) == 0
        assert audio_slice.cues["footsteps"].is_spatialized is True
        assert audio_slice.cues["music"].bus == "Music"

    def test_cinematic_generator_camera_and_gameplay_transitions(self):
        gen = CinematicGenerator()
        cine_slice = gen.generate()

        assert cine_slice.duration_frames == 200
        assert len(cine_slice.keyframes) >= 4
        assert cine_slice.has_transition_to_gameplay is True
        assert len(cine_slice.validate()) == 0

    def test_ui_generator_hud_widgets_and_accessibility(self):
        gen = UIGenerator()
        ui_slice = gen.generate()

        assert len(ui_slice.hud_widgets) == 8
        assert len(ui_slice.validate()) == 0
        assert ui_slice.accessibility.high_contrast is True
        assert ui_slice.accessibility.colorblind_filter == "Deuteranopia"


class TestQAScenariosAndAutomatedBot:
    """Tests the 12 functional QA suites and the autonomous GoldenSliceBot."""

    def test_qa_runner_12_functional_test_suites(self):
        runner = QARunner()
        report = runner.run_all()

        assert report.total_tests == 12
        assert report.passed_tests == 12
        assert report.failed_tests == 0
        assert report.is_success is True
        assert report.get_result("BOOT_TEST").passed is True
        assert report.get_result("COMBAT_TEST").passed is True
        assert report.get_result("NETWORK_TEST").passed is True

    def test_golden_slice_bot_autonomous_scenario_execution(self):
        bot = GoldenSliceBot()
        scenario = create_golden_main_scenario()
        assert scenario.step_count == 19

        report = bot.execute_scenario(scenario)
        assert report.is_success is True
        assert report.total_steps == 19
        assert report.successful_steps == 19
        assert report.failed_steps == 0
        assert bot.state["is_spawned"] is True
        assert bot.state["objective_score"] >= 25
        assert len(bot.state["inventory"]) > 0


class TestDeterminismPerformanceAndNetworking:
    """Tests multi-run hash equivalence, frame budgeting, and multiplayer replication."""

    def test_determinism_verifier_multi_run_state_hashes(self):
        verifier = DeterminismVerifier()
        run_a = DeterminismRunResult("run_A", 1337, "hash_golden_state_xyz", ["h0", "h1", "h2"], 10)
        run_b = DeterminismRunResult("run_B", 1337, "hash_golden_state_xyz", ["h0", "h1", "h2"], 10)
        run_c = DeterminismRunResult("run_C", 1337, "hash_golden_state_xyz", ["h0", "h1", "h2"], 10)

        report = verifier.compare_runs([run_a, run_b, run_c])
        assert report.is_deterministic is True
        assert report.runs_evaluated == 3

        # Test divergence detection
        run_diverged = DeterminismRunResult("run_D", 1337, "hash_different", ["h0", "h1_diverged", "h2"], 10)
        diverge_report = verifier.compare_runs([run_a, run_diverged])
        assert diverge_report.is_deterministic is False

    def test_performance_budget_and_frame_time_profiler(self):
        budget = PerformanceBudget(target_fps=60, ram_budget_mb=4096.0, vram_budget_mb=6144.0, max_frame_time_ms=16.67)
        compliance = budget.evaluate_compliance(used_ram_mb=2100.0, used_vram_mb=3200.0, p99_frame_time_ms=15.2)
        assert compliance.is_compliant is True
        assert len(compliance.violations) == 0

        # Test violation trigger
        bad_compliance = budget.evaluate_compliance(used_ram_mb=5000.0, used_vram_mb=3200.0, p99_frame_time_ms=25.0)
        assert bad_compliance.is_compliant is False
        assert len(bad_compliance.violations) >= 2

        # Profiler percentile calculation
        profiler = GoldenSliceProfiler()
        for t in [10.0, 12.0, 13.0, 14.0, 15.0, 16.0, 20.0]:
            profiler.record_frame(t)
        summary = profiler.compute_summary()
        assert summary.total_frames == 7
        assert summary.p50_ms == 14.0
        assert summary.max_ms == 20.0

    def test_multiplayer_replication_and_server_authority(self):
        harness = MultiplayerReplicationHarness(client_count=4)
        rep = harness.run_replication_test()
        assert rep.server_running is True
        assert rep.connected_clients == 4
        assert rep.replication_passed is True
        assert rep.server_authority_enforced is True
        assert rep.fault_recovery_passed is True

    def test_visual_and_audio_regression_verifiers(self):
        vis = VisualRegressionVerifier()
        vis_rep = vis.verify_all()
        assert vis_rep.is_success is True
        assert vis_rep.total_points == 9

        audio = AudioRegressionVerifier()
        audio_rep = audio.verify_all()
        assert audio_rep.is_success is True
        assert audio_rep.total_cues == 8


class TestRepairPackagingAndCertification:
    """Tests failure analysis, self-repair, packaging, and multi-tier certification gates."""

    def test_autonomous_failure_analysis_and_self_repair(self):
        repair_engine = SelfRepairEngine(max_repair_attempts=3)
        simulated_state = {"actor_01": {"material": "broken_ref"}}

        # Attempt repair of a missing texture symptom
        res = repair_engine.attempt_repair(
            simulated_state,
            error_message="Shader compiler: unresolved texture map path",
            targeted_verifier=lambda s: s.get("fallback_texture_assigned", False) is True,
        )

        assert res.success is True
        assert res.repair_action == "assign_fallback_texture"
        assert res.regression_test is not None
        assert len(repair_engine.generated_regression_tests) == 1

    def test_slice_packager_cook_validation_and_artifact_manifests(self):
        packager = SlicePackager()
        manifest = GoldenSliceManifest(target_platform=PlatformType.WINDOWS)

        res = packager.package(manifest)
        assert res.is_success is True
        assert res.platform == PlatformType.WINDOWS
        assert len(res.artifact_manifest.artifacts) >= 2
        assert len(res.build_manifest.binary_hash) == 64

    def test_certification_gates_multi_tier_criteria(self):
        gatekeeper = CertificationGatekeeper()

        # Evaluate GOLD certification
        gold_res = gatekeeper.evaluate(
            target_level=CertificationLevel.GOLD,
            functional_tests_passed=True,
            performance_compliant=True,
            determinism_verified=True,
            recovery_verified=True,
            reproducibility_verified=True,
            critical_failures=0,
            blocking_warnings=0,
            replay_mismatches=0,
        )
        assert gold_res.is_certified is True
        assert gold_res.achieved_level == CertificationLevel.PLATINUM
        assert gold_res.summary_status == "CERTIFIED PLATINUM"

        # Evaluate rejection on critical failure
        failed_res = gatekeeper.evaluate(
            target_level=CertificationLevel.GOLD,
            functional_tests_passed=True,
            performance_compliant=True,
            determinism_verified=True,
            recovery_verified=True,
            reproducibility_verified=True,
            critical_failures=1,
        )
        assert failed_res.is_certified is False
        assert failed_res.summary_status == "FAILED"

    def test_golden_slice_certification_report_and_rc_immutability(self):
        report = GoldenSliceCertificationReport(
            project_id="AegisAscent",
            build_id="bld_001",
            target_level=CertificationLevel.GOLD,
            achieved_level=CertificationLevel.GOLD,
            is_certified=True,
            final_status="CERTIFIED GOLD",
            generation_passed=True,
            integration_passed=True,
            qa_tests_passed=True,
            performance_compliant=True,
            determinism_verified=True,
            recovery_verified=True,
            packaging_passed=True,
            critical_failures=0,
            blocking_warnings=0,
            replay_mismatches=0,
            execution_time_s=2.5,
        )

        assert not report.is_immutable
        report.freeze_as_rc()
        assert report.is_immutable is True
        assert report.release_candidate_tag == "GOLDEN_RC"

        html = HTMLReportGenerator.generate(report)
        assert "UAF Golden Slice Certification" in html
        assert "CERTIFIED GOLD" in html
        assert "LOCKED IMMUTABLE RELEASE CANDIDATE" in html


class TestMasterOrchestratorEndToEnd:
    """Tests the complete autonomous vertical slice pipeline and CLI integration."""

    def test_master_orchestrator_end_to_end_production_pipeline(self):
        manifest = GoldenSliceManifest(
            project_id="GoldenCitadel",
            seed=777,
            quality_profile=QualityProfile.GOLDEN,
        )
        orchestrator = GoldenSliceOrchestrator(manifest)

        # Execute full autonomous pipeline: plan -> generate -> integrate -> validate -> test -> profile -> package -> certify
        report = orchestrator.run_full_pipeline(target_level=CertificationLevel.GOLD)

        assert report.is_certified is True
        assert report.generation_passed is True
        assert report.integration_passed is True
        assert report.qa_tests_passed is True
        assert report.performance_compliant is True
        assert report.determinism_verified is True
        assert report.packaging_passed is True
        assert report.critical_failures == 0
        assert report.blocking_warnings == 0
        assert report.replay_mismatches == 0
        assert report.is_immutable is True
        assert report.release_candidate_tag == "GOLDEN_RC"
        assert orchestrator.state == BuildState.CERTIFIED

    def test_cli_commands_execution(self):
        # Test CLI commands
        assert run_cli(["plan"]) == 0
        assert run_cli(["generate"]) == 0
        assert run_cli(["test"]) == 0
        assert run_cli(["profile"]) == 0
        assert run_cli(["package"]) == 0
        assert run_cli(["certify", "--profile", "GOLD"]) == 0
