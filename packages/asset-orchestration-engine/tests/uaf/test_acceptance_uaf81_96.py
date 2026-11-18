"""
Acceptance Test Suite for UAF-81.96: Autonomous Gameplay Playtesting & AI QA Simulation.
Validates headless player bot simulation, multi-archetype behaviors, combat resolution,
topological reachability, static and empirical softlock detection, difficulty spike analysis,
spatial 2D Gaussian heatmaps, closed-loop auto-calibration, and multi-format QA reporting.
"""

import pytest
from pathlib import Path
import tempfile
import json
import csv

from uaf.playtesting import (
    PlaytestArchetype,
    SimulationOutcome,
    SoftlockType,
    SoftlockSeverity,
    TelemetryEventType,
    HeatmapMetric,
    Vector3D,
    AgentStats,
    ArchetypeProfile,
    TelemetryEvent,
    EnemySpawn,
    DoorConnection,
    RoomSpec,
    PlaytestLevelSpec,
    SoftlockIncident,
    DifficultySpikeIncident,
    HeatmapGrid2D,
    PlaytestRunResult,
    QASimulationSuiteSummary,
    HeadlessPlaytestAgent,
    SpatialHeatmapGenerator,
    SoftlockAndDifficultyAnalyzer,
    ClosedLoopPacingCalibrator,
    QAReportExporter,
)


def _build_test_linear_level() -> PlaytestLevelSpec:
    """
    Creates a valid 3-room level: Start -> Hallway (contains Key_Alpha) -> Locked Door -> Vault (Goal).
    """
    rooms = {
        "room_start": RoomSpec(
            room_id="room_start",
            room_name="Entry Air-lock",
            center_position=Vector3D(x=0.0, y=0.0, z=0.0),
            is_start=True,
            is_goal=False,
        ),
        "room_hallway": RoomSpec(
            room_id="room_hallway",
            room_name="Security Hallway",
            center_position=Vector3D(x=20.0, y=0.0, z=0.0),
            is_start=False,
            is_goal=False,
            contained_keys=["Key_Alpha"],
            enemies=[
                EnemySpawn(
                    enemy_id="patrol_drone_1",
                    enemy_type="DRONE",
                    health=30.0,
                    damage=5.0,
                    fire_rate=1.0,
                    is_mandatory=True,
                )
            ],
            health_pickups=1,
            ammo_pickups=1,
        ),
        "room_vault": RoomSpec(
            room_id="room_vault",
            room_name="Core Vault",
            center_position=Vector3D(x=40.0, y=0.0, z=0.0),
            is_start=False,
            is_goal=True,
        ),
    }

    connections = [
        DoorConnection(
            source_room_id="room_start",
            target_room_id="room_hallway",
            is_two_way=True,
            required_key_id=None,
        ),
        DoorConnection(
            source_room_id="room_hallway",
            target_room_id="room_vault",
            is_two_way=True,
            required_key_id="Key_Alpha",
            is_locked_initially=True,
        ),
    ]

    return PlaytestLevelSpec(
        level_id="LVL_TEST_LINEAR",
        level_name="Linear Air-lock Level",
        rooms=rooms,
        connections=connections,
        seed=101,
    )


class TestAcceptanceUAF81_96:

    def test_uaf81_96_contracts_and_models(self):
        """Validates instantiation of all core Pydantic domain models with keyword arguments."""
        vec = Vector3D(x=10.0, y=20.0, z=5.0)
        assert vec.x == 10.0
        assert vec.to_ue5_cm().x == 1000.0

        stats = AgentStats(max_health=100.0, current_health=100.0, ammo=120)
        assert stats.max_health == 100.0
        assert stats.ammo == 120

        enemy = EnemySpawn(enemy_id="e1", enemy_type="SENTRY", health=40.0, damage=8.0)
        assert enemy.enemy_id == "e1"

        conn = DoorConnection(source_room_id="r1", target_room_id="r2", required_key_id="k1")
        assert conn.required_key_id == "k1"

        incident = SoftlockIncident(
            incident_id="inc_1",
            softlock_type=SoftlockType.KEY_BEHIND_LOCKED_DOOR,
            severity=SoftlockSeverity.FATAL_SOFTLOCK,
            room_id="r2",
            description="Locked door test",
        )
        assert incident.severity == SoftlockSeverity.FATAL_SOFTLOCK

    def test_uaf81_96_vector3d_coordinate_conversions(self):
        """Verifies SI meter to UE5 centimeter conversions and distance calculations."""
        v1 = Vector3D(x=0.0, y=0.0, z=0.0)
        v2 = Vector3D(x=3.0, y=4.0, z=0.0)
        assert round(v1.distance_to(v2), 2) == 5.0

        v_ue5 = v2.to_ue5_cm()
        assert v_ue5.x == 300.0
        assert v_ue5.y == 400.0

        v_back = Vector3D.from_ue5_cm(300.0, 400.0, 0.0)
        assert round(v_back.x, 2) == 3.0
        assert round(v_back.y, 2) == 4.0

    def test_uaf81_96_archetype_initialization(self):
        """Ensures all 5 archetypes have properly tailored stats and behavior profiles."""
        for arch in PlaytestArchetype:
            agent = HeadlessPlaytestAgent(archetype=arch, seed=42)
            assert agent.archetype == arch
            assert agent.stats.max_health > 0.0
            assert agent.stats.ammo > 0
            assert agent.profile.accuracy_mult > 0.0

        # Novice has lower accuracy than combatant
        novice = HeadlessPlaytestAgent(archetype=PlaytestArchetype.NOVICE)
        combatant = HeadlessPlaytestAgent(archetype=PlaytestArchetype.COMBATANT)
        assert novice.stats.accuracy < combatant.stats.accuracy

    def test_uaf81_96_headless_agent_single_run_victory(self):
        """Tests that an autonomous agent successfully completes the linear level."""
        level = _build_test_linear_level()
        agent = HeadlessPlaytestAgent(archetype=PlaytestArchetype.SPEEDRUNNER, seed=77)
        result = agent.simulate_run(level)

        assert result.outcome == SimulationOutcome.VICTORY
        assert "room_start" in result.rooms_visited
        assert "room_hallway" in result.rooms_visited
        assert "room_vault" in result.rooms_visited
        assert "Key_Alpha" in result.keys_collected
        assert result.enemies_defeated >= 1
        assert len(result.telemetry_events) > 5

    def test_uaf81_96_headless_agent_combat_resolution(self):
        """Tests that combat interactions consume ammo, register hits, and defeat enemies."""
        level = _build_test_linear_level()
        agent = HeadlessPlaytestAgent(archetype=PlaytestArchetype.COMBATANT, seed=99)
        result = agent.simulate_run(level)

        assert result.ammo_spent > 0
        assert result.shots_fired > 0
        assert result.damage_dealt > 0.0
        assert result.enemies_defeated == 1
        assert result.accuracy_achieved > 0.0

    def test_uaf81_96_headless_agent_death_outcome(self):
        """Pits an under-equipped novice agent against a lethal squad to verify death handling."""
        level = _build_test_linear_level()
        # Make the hallway enemy overwhelmingly lethal
        level.rooms["room_hallway"].enemies[0].damage = 200.0
        level.rooms["room_hallway"].enemies[0].health = 500.0

        agent = HeadlessPlaytestAgent(archetype=PlaytestArchetype.NOVICE, seed=123)
        result = agent.simulate_run(level)

        assert result.outcome == SimulationOutcome.DEATH
        death_events = [
            e for e in result.telemetry_events if e.event_type == TelemetryEventType.DEATH
        ]
        assert len(death_events) == 1
        assert death_events[0].room_id == "room_hallway"

    def test_uaf81_96_static_softlock_detection_missing_start_and_goal(self):
        """Validates that analyzer catches missing start and missing goal rooms."""
        analyzer = SoftlockAndDifficultyAnalyzer()

        # Missing start
        level_no_start = _build_test_linear_level()
        level_no_start.rooms["room_start"].is_start = False
        incidents_1 = analyzer.analyze_level_topology(level_no_start)
        assert any(inc.softlock_type == SoftlockType.DISCONNECTED_ROOM for inc in incidents_1)

        # Missing goal
        level_no_goal = _build_test_linear_level()
        level_no_goal.rooms["room_vault"].is_goal = False
        incidents_2 = analyzer.analyze_level_topology(level_no_goal)
        assert any(inc.softlock_type == SoftlockType.MISSING_GOAL for inc in incidents_2)

    def test_uaf81_96_static_softlock_detection_key_behind_locked_door(self):
        """Validates detection of a key trapped behind the locked door that requires it."""
        level = _build_test_linear_level()
        # Move Key_Alpha from hallway to vault (behind the locked door)
        level.rooms["room_hallway"].contained_keys = []
        level.rooms["room_vault"].contained_keys = ["Key_Alpha"]

        analyzer = SoftlockAndDifficultyAnalyzer()
        incidents = analyzer.analyze_level_topology(level)

        fatal = [inc for inc in incidents if inc.severity == SoftlockSeverity.FATAL_SOFTLOCK]
        assert len(fatal) >= 1
        assert fatal[0].softlock_type == SoftlockType.KEY_BEHIND_LOCKED_DOOR
        assert "room_vault" in fatal[0].room_id

    def test_uaf81_96_static_softlock_detection_disconnected_room(self):
        """Validates detection of an isolated room without incoming or outgoing connections."""
        level = _build_test_linear_level()
        level.rooms["orphan_room"] = RoomSpec(
            room_id="orphan_room",
            room_name="Orphaned Chamber",
            center_position=Vector3D(x=100.0, y=100.0, z=0.0),
        )

        analyzer = SoftlockAndDifficultyAnalyzer()
        incidents = analyzer.analyze_level_topology(level)

        orphan_incidents = [inc for inc in incidents if inc.room_id == "orphan_room"]
        assert len(orphan_incidents) == 1
        assert orphan_incidents[0].softlock_type == SoftlockType.DISCONNECTED_ROOM

    def test_uaf81_96_empirical_difficulty_spike_detection(self):
        """Simulates multiple runs and verifies difficulty spike identification."""
        level = _build_test_linear_level()
        # Make the enemy lethal enough to trigger difficulty spike
        level.rooms["room_hallway"].enemies[0].damage = 120.0
        level.rooms["room_hallway"].enemies[0].health = 150.0

        runs = []
        for i in range(10):
            agent = HeadlessPlaytestAgent(archetype=PlaytestArchetype.NOVICE, seed=1000 + i)
            runs.append(agent.simulate_run(level))

        analyzer = SoftlockAndDifficultyAnalyzer(spike_death_threshold=0.20)
        summary = analyzer.analyze_simulation_runs(level, runs)

        assert summary.total_runs == 10
        assert summary.death_count > 0
        assert len(summary.difficulty_spikes) >= 1
        spike = summary.difficulty_spikes[0]
        assert spike.room_id == "room_hallway"
        assert spike.player_death_count > 0

    def test_uaf81_96_spatial_heatmap_generation(self):
        """Tests 2D grid binning, Gaussian kernel smoothing, and hotspot extraction."""
        level = _build_test_linear_level()
        runs = []
        for i in range(5):
            agent = HeadlessPlaytestAgent(archetype=PlaytestArchetype.EXPLORER, seed=200 + i)
            runs.append(agent.simulate_run(level))

        generator = SpatialHeatmapGenerator(
            cell_size_m=5.0,
            min_x=-10.0,
            max_x=50.0,
            min_y=-10.0,
            max_y=50.0,
        )

        heatmap = generator.generate_heatmap(
            runs=runs,
            metric=HeatmapMetric.PATH_TRAVERSAL,
            apply_smoothing=True,
            hotspot_threshold=0.50,
        )

        assert heatmap.grid_width > 0
        assert heatmap.grid_height > 0
        assert len(heatmap.cells) == heatmap.grid_height
        assert len(heatmap.cells[0]) == heatmap.grid_width

        # Check normalization bounds
        for row in heatmap.cells:
            for val in row:
                assert 0.0 <= val <= 1.0

        # Hotspots check
        assert isinstance(heatmap.hotspots, list)
        if heatmap.hotspots:
            assert heatmap.hotspots[0]["intensity"] >= 0.50

    def test_uaf81_96_closed_loop_calibrator_softlock_repair(self):
        """Tests that closed-loop calibrator automatically relocates keys to solve softlocks."""
        level = _build_test_linear_level()
        # Trap the key behind the locked door
        level.rooms["room_hallway"].contained_keys = []
        level.rooms["room_vault"].contained_keys = ["Key_Alpha"]

        analyzer = SoftlockAndDifficultyAnalyzer()
        summary = analyzer.analyze_simulation_runs(level, [])
        assert any(
            inc.softlock_type == SoftlockType.KEY_BEHIND_LOCKED_DOOR
            for inc in summary.identified_softlocks
        )

        calibrator = ClosedLoopPacingCalibrator()
        calibrated_level, changelog = calibrator.calibrate_level(level, summary)

        assert changelog["total_corrections"] >= 1
        # Check that Key_Alpha is now in the predecessor room
        assert "Key_Alpha" in calibrated_level.rooms["room_hallway"].contained_keys

        # Re-analyzing should reveal zero fatal softlocks
        re_summary = analyzer.analyze_simulation_runs(calibrated_level, [])
        fatal_remaining = [
            inc for inc in re_summary.identified_softlocks if inc.severity == SoftlockSeverity.FATAL_SOFTLOCK
        ]
        assert len(fatal_remaining) == 0

    def test_uaf81_96_closed_loop_calibrator_difficulty_dampening(self):
        """Tests that closed-loop calibrator dampens enemy stats and injects resource caches."""
        level = _build_test_linear_level()
        # Create a severe difficulty spike
        level.rooms["room_hallway"].enemies[0].damage = 100.0
        level.rooms["room_hallway"].enemies[0].health = 200.0

        runs = []
        for i in range(8):
            agent = HeadlessPlaytestAgent(archetype=PlaytestArchetype.NOVICE, seed=500 + i)
            runs.append(agent.simulate_run(level))

        analyzer = SoftlockAndDifficultyAnalyzer(spike_death_threshold=0.25)
        summary = analyzer.analyze_simulation_runs(level, runs)
        assert len(summary.difficulty_spikes) >= 1

        calibrator = ClosedLoopPacingCalibrator(max_acceptable_death_rate_per_room=0.25)
        calibrated_level, changelog = calibrator.calibrate_level(level, summary)

        # Check enemy damage was dampened
        original_dmg = level.rooms["room_hallway"].enemies[0].damage
        calibrated_dmg = calibrated_level.rooms["room_hallway"].enemies[0].damage
        assert calibrated_dmg < original_dmg
        # Check resource caches were added
        assert calibrated_level.rooms["room_hallway"].ammo_pickups > level.rooms["room_hallway"].ammo_pickups

    def test_uaf81_96_qa_report_exporter_json_md_csv(self):
        """Tests multi-format report exports (JSON, Markdown, telemetry CSV, heatmap CSV)."""
        level = _build_test_linear_level()
        runs = [
            HeadlessPlaytestAgent(archetype=PlaytestArchetype.EXPLORER, seed=1).simulate_run(level),
            HeadlessPlaytestAgent(archetype=PlaytestArchetype.COMBATANT, seed=2).simulate_run(level),
        ]

        analyzer = SoftlockAndDifficultyAnalyzer()
        summary = analyzer.analyze_simulation_runs(level, runs)

        generator = SpatialHeatmapGenerator()
        heatmap = generator.generate_heatmap(runs, HeatmapMetric.PATH_TRAVERSAL)

        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)

            # JSON export
            json_file = tmp_path / "qa_summary.json"
            json_str = QAReportExporter.export_json(summary, runs, [heatmap], json_file)
            assert json_file.exists()
            data = json.loads(json_str)
            assert data["run_count"] == 2

            # Markdown export
            md_file = tmp_path / "qa_report.md"
            md_str = QAReportExporter.export_markdown(summary, level, md_file)
            assert md_file.exists()
            assert "# UAF-81.96 Autonomous Playtesting QA Audit Report" in md_str

            # Telemetry CSV
            csv_file = tmp_path / "telemetry.csv"
            csv_str = QAReportExporter.export_telemetry_csv(runs, csv_file)
            assert csv_file.exists()
            assert "session_id,archetype,event_id" in csv_str

            # Heatmap CSV
            heat_csv_file = tmp_path / "heatmap.csv"
            heat_csv_str = QAReportExporter.export_heatmap_csv(heatmap, heat_csv_file)
            assert heat_csv_file.exists()
            assert len(heat_csv_str.strip().split("\n")) == heatmap.grid_height

    def test_uaf81_96_multi_archetype_monte_carlo_simulation(self):
        """Runs batch simulation across all 5 archetypes and checks aggregated performance."""
        level = _build_test_linear_level()
        runs: List[PlaytestRunResult] = []

        for arch in PlaytestArchetype:
            agent = HeadlessPlaytestAgent(archetype=arch, seed=42)
            res = agent.simulate_run(level)
            runs.append(res)

        analyzer = SoftlockAndDifficultyAnalyzer()
        summary = analyzer.analyze_simulation_runs(level, runs)

        assert summary.total_runs == 5
        assert len(summary.archetype_survival_rates) == 5
        assert summary.overall_survival_rate > 0.0
