"""Acceptance tests for UAF-81.86 — Universal Runtime Profiling, Telemetry, Frame Budgeting, Diagnostics & Crash Recovery."""

import pytest
import time
from typing import Dict, Any

from uaf.runtime_diagnostics.core import (
    MetricId,
    SpanId,
    SessionId,
    AllocationId,
    DiagnosticEventId,
    MetricType,
    MetricUnit,
    SubsystemType,
    ProfilingMode,
    InstrumentationLevel,
    SeverityLevel,
    CrashType,
    RecoveryLevel,
    QualityGateResult,
    ensure_finite_float,
    ensure_finite_scalar,
)
from uaf.runtime_diagnostics.metrics import (
    TelemetryCounter,
    TelemetryGauge,
    TelemetryHistogram,
    TelemetrySpan,
    TelemetryEvent,
)
from uaf.runtime_diagnostics.buffers import TelemetryBuffer
from uaf.runtime_diagnostics.spans import SpanManager, SpanScope
from uaf.runtime_diagnostics.budget import SubsystemBudget, FrameBudgetManager
from uaf.runtime_diagnostics.memory_profiler import (
    MemoryAllocation,
    MemorySnapshot,
    MemoryLeakInfo,
    MemoryProfiler,
)
from uaf.runtime_diagnostics.subsystem_profilers import (
    StreamingProfiler,
    StreamingProfileMetrics,
    PhysicsProfiler,
    PhysicsProfileMetrics,
    AIProfiler,
    AIProfileMetrics,
    NetworkProfiler,
    NetworkProfileMetrics,
    AnimationProfiler,
    AnimationProfileMetrics,
    VFXProfiler,
    VFXProfileMetrics,
    LightingProfiler,
    LightingProfileMetrics,
    RenderProfiler,
    RenderProfileMetrics,
    AudioProfiler,
    AudioProfileMetrics,
    UIProfiler,
    UIProfileMetrics,
)
from uaf.runtime_diagnostics.anomalies import (
    AnomalyType,
    HitchSeverity,
    PerformanceAnomaly,
    AnomalyDetector,
)
from uaf.runtime_diagnostics.regression import (
    BenchmarkBaseline,
    RegressionReport,
    RegressionEngine,
)
from uaf.runtime_diagnostics.determinism import (
    DivergencePoint,
    DeterminismDiagnosticEngine,
)
from uaf.runtime_diagnostics.traces import (
    TraceSpanRecord,
    TraceFrameRecord,
    UAFTraceRecorder,
)
from uaf.runtime_diagnostics.crash import CrashReport, CrashHandler
from uaf.runtime_diagnostics.watchdog import (
    ThreadWatchdog,
    DeadlockDetector,
    DeadlockCycle,
)
from uaf.runtime_diagnostics.recovery import (
    CrashRecoveryOrchestrator,
    RecoveryRecord,
    ORDERED_RECOVERY_LEVELS,
)
from uaf.runtime_diagnostics.telemetry import TelemetryManager
from uaf.runtime_diagnostics.reports import ReportGenerator
from uaf.runtime_diagnostics.validation import TelemetryValidator

from aoe.diagnostics.failure_analysis import (
    FailureIncident,
    FailureAnalysisReport,
    FailureAnalyzer,
)
from aoe.diagnostics.root_cause import (
    RootCauseHypothesis,
    RootCauseAnalyzer,
)
from aoe.diagnostics.remediation import (
    RemediationAction,
    RemediationPlanner,
)
from aoe.diagnostics.quality_gate import (
    QualityGateThresholds,
    QualityGateVerdict,
    QualityGateEvaluator,
)
from aoe.diagnostics.benchmark import (
    BenchmarkConfig,
    BenchmarkRunResult,
    BenchmarkRunner,
)
from aoe.diagnostics.certification import (
    GoldenCertificationCertificate,
    GoldenCertificationEngine,
)


class TestTelemetryMetricsAndBuffers:
    """Test 81.86.0: Metrics data model, percentiles, and ring buffers."""

    def test_identifiers_and_finite_scalars(self):
        mid = MetricId("sim_cost")
        sid = SpanId("span_update")
        assert str(mid) == "sim_cost"
        assert str(sid) == "span_update"

        assert ensure_finite_scalar(42.5, "test") == 42.5
        assert ensure_finite_scalar(float("nan"), "test", default=0.0) == 0.0
        assert ensure_finite_scalar(float("inf"), "test", default=10.0) == 10.0
        assert ensure_finite_float(float("-inf"), default=-1.0) == -1.0

    def test_counter_and_gauge(self):
        counter = TelemetryCounter(MetricId("packets"), "packets", SubsystemType.NETWORKING)
        assert counter.value == 0
        counter.increment(5)
        counter.increment(10)
        assert counter.value == 15
        counter.reset()
        assert counter.value == 0

        gauge = TelemetryGauge(MetricId("cpu_usage"), "cpu_usage", SubsystemType.GENERAL)
        gauge.set(45.2)
        assert gauge.value == 45.2
        gauge.set(float("nan"))
        assert gauge.value == 0.0

    def test_histogram_percentiles(self):
        hist = TelemetryHistogram(MetricId("frame_time"), "frame_time", SubsystemType.RENDERING)
        for i in range(1, 101):
            hist.record(float(i))

        assert hist.count == 100
        assert hist.min_val == 1.0
        assert hist.max_val == 100.0
        assert hist.mean == 50.5
        assert 49.0 <= hist.percentile(50.0) <= 51.0
        assert 94.0 <= hist.percentile(95.0) <= 96.0
        assert 98.0 <= hist.percentile(99.0) <= 100.0

    def test_bounded_ring_buffer_and_freeze(self):
        buf = TelemetryBuffer[int](capacity=5)
        for i in range(10):
            buf.push(i)

        assert buf.size == 5
        assert buf.overflow_count == 5
        assert buf.to_list() == [5, 6, 7, 8, 9]

        buf.freeze()
        assert buf.is_frozen
        # Subsequent pushes are dropped while frozen
        buf.push(100)
        assert buf.to_list() == [5, 6, 7, 8, 9]

        buf.unfreeze()
        buf.push(200)
        assert buf.to_list() == [6, 7, 8, 9, 200]


class TestHierarchicalSpansAndScopes:
    """Test spans and scope managers."""

    def test_nested_spans(self):
        mgr = SpanManager()
        root = mgr.begin_span("FrameRoot", SubsystemType.GENERAL)
        time.sleep(0.002)

        child1 = mgr.begin_span("PhysicsUpdate", SubsystemType.PHYSICS)
        time.sleep(0.002)
        mgr.end_span(child1)

        child2 = mgr.begin_span("RenderPass", SubsystemType.RENDERING)
        time.sleep(0.002)
        mgr.end_span(child2)

        mgr.end_span(root)

        completed = mgr.get_completed_spans()
        assert len(completed) == 3
        assert root.duration_ms > 0
        assert child1.duration_ms > 0
        assert len(root.children) == 2

    def test_span_scope_context_manager(self):
        mgr = SpanManager()
        with mgr.scope("AudioMix", SubsystemType.AUDIO) as span:
            assert span.name == "AudioMix"
            assert span.subsystem == SubsystemType.AUDIO
            time.sleep(0.001)

        completed = mgr.get_completed_spans()
        assert len(completed) == 1
        assert completed[0].duration_ms > 0


class TestFrameBudgetingAndDynamicNegotiation:
    """Test 81.86.1: Frame budget manager, overrun detection, and budget pooling."""

    def test_budget_initialization_and_targets(self):
        fbm = FrameBudgetManager(target_fps=60.0)
        assert round(fbm.total_budget_ms, 2) == 16.67
        assert SubsystemType.RENDERING in fbm.budgets
        assert SubsystemType.PHYSICS in fbm.budgets

        # Verify sum matches total budget
        errs = TelemetryValidator.validate_budget_manager(fbm)
        assert len(errs) == 0

    def test_budget_overrun_and_pooling(self):
        fbm = FrameBudgetManager(target_fps=60.0)
        fbm.begin_frame()

        # Under budget on Audio and UI, over budget on Physics
        fbm.record_duration(SubsystemType.AUDIO, 0.1)
        fbm.record_duration(SubsystemType.UI, 0.1)
        fbm.record_duration(SubsystemType.PHYSICS, 4.5)  # Nominal is ~2.2ms

        summary = fbm.end_frame(total_frame_ms=15.0)
        assert "subsystems" in summary

        # Test dynamic budget negotiation
        negotiated = fbm.negotiate_budgets()
        assert SubsystemType.PHYSICS in negotiated
        assert negotiated[SubsystemType.PHYSICS] >= fbm.budgets[SubsystemType.PHYSICS].target_ms

    def test_degradation_tier_recommendations(self):
        fbm = FrameBudgetManager(target_fps=60.0)
        fbm.begin_frame()
        # Catastrophic frame time
        summary = fbm.end_frame(total_frame_ms=45.0)
        assert summary["is_overrun"] is True
        rec = fbm.get_degradation_recommendation()
        assert rec["degradation_tier"] >= 2


class TestMemoryProfilerAndLeakDetection:
    """Test 81.86.2: Allocation tracking, snapshots, diffing, and leak detection."""

    def test_memory_allocation_and_free(self):
        mp = MemoryProfiler()
        a1 = mp.allocate(owner="mesh_loader", subsystem=SubsystemType.RENDERING, resource_type="VertexBuffer", size_bytes=1024, frame=1)
        a2 = mp.allocate(owner="vfx_system", subsystem=SubsystemType.VFX, resource_type="ParticleBuffer", size_bytes=2048, frame=1)

        assert mp.total_allocated_bytes == 3072
        assert mp.peak_allocated_bytes == 3072
        assert len(mp.active_allocations) == 2

        freed = mp.free(a1)
        assert freed is True
        assert mp.total_allocated_bytes == 2048
        assert mp.total_freed_bytes == 1024

    def test_snapshot_diffing(self):
        mp = MemoryProfiler()
        a1 = mp.allocate("sys1", SubsystemType.PHYSICS, "RigidBody", 500, frame=10)
        snap1 = mp.take_snapshot(frame=10)

        a2 = mp.allocate("sys2", SubsystemType.AI, "NavMeshTile", 1500, frame=15)
        mp.free(a1)
        snap2 = mp.take_snapshot(frame=15)

        diff = mp.diff_snapshots(snap1, snap2)
        assert diff["new_allocations_count"] == 1
        assert diff["released_allocations_count"] == 1
        assert diff["new_bytes"] == 1500
        assert diff["released_bytes"] == 500
        assert diff["net_byte_change"] == 1000

    def test_leak_detection(self):
        mp = MemoryProfiler()
        # Expected lifetime 5 frames, created at frame 10
        mp.allocate("audio_source", SubsystemType.AUDIO, "SoundInstance", 256, frame=10, expected_lifetime_frames=5)
        # Persistent buffer (lifetime None)
        mp.allocate("texture_pool", SubsystemType.RENDERING, "Texture2D", 4096, frame=10, expected_lifetime_frames=None)

        leaks_at_12 = mp.detect_leaks(current_frame=12)
        assert len(leaks_at_12) == 0

        leaks_at_20 = mp.detect_leaks(current_frame=20)
        assert len(leaks_at_20) == 1
        assert leaks_at_20[0].resource_type == "SoundInstance"
        assert leaks_at_20[0].age_frames == 10


class TestSubsystemProfilers:
    """Test 81.86.3 — 81.86.12: Dedicated subsystem profilers."""

    def test_profilers_recording(self):
        sp = StreamingProfiler()
        sp.record(StreamingProfileMetrics(cell_io_read_bytes=10000, uncompressed_bytes=25000, io_wait_ms=1.2))
        assert len(sp.history) == 1
        assert sp.to_dict()["history_samples"] == 1

        pp = PhysicsProfiler()
        pp.record(PhysicsProfileMetrics(broadphase_ms=0.5, narrowphase_ms=1.2, solver_ms=1.8, active_rigidbodies=350))
        assert len(pp.history) == 1

        aip = AIProfiler()
        aip.record(AIProfileMetrics(active_agents=500, path_requests=150, pathfinding_time_ms=12.0))
        assert aip.history[0].is_storm_detected is True

        net = NetworkProfiler()
        net.record(NetworkProfileMetrics(packet_loss_percent=15.0, prediction_corrections=60))
        assert net.history[0].is_anomaly_detected is True

        vfx = VFXProfiler()
        vfx.record(VFXProfileMetrics(active_emitters=600, cpu_particles=60000))
        assert vfx.history[0].is_leak_detected is True

        lp = LightingProfiler()
        lp.record(LightingProfileMetrics(dynamic_lights=250, atlas_occupancy_ratio=0.98))
        assert lp.history[0].is_overloaded is True


class TestAnomalyAndHitchDetection:
    """Test 81.86.13: Performance anomaly classification and contextual hitch capture."""

    def test_hitch_detection_and_severity(self):
        ad = AnomalyDetector()
        # Normal frames
        for f in range(5):
            anomalies = ad.feed_frame(frame_index=f, frame_time_ms=16.0, subsystem_times={"rendering": 8.0, "physics": 3.0})
            assert len(anomalies) == 0

        # Massive hitch frame (> 3x threshold)
        hitch_frame = ad.feed_frame(
            frame_index=6,
            frame_time_ms=65.0,
            subsystem_times={"rendering": 45.0, "physics": 10.0},
            hitch_threshold_ms=20.0,
        )
        assert len(hitch_frame) == 1
        assert hitch_frame[0].anomaly_type == AnomalyType.HITCH
        assert hitch_frame[0].hitch_severity in (HitchSeverity.SEVERE, HitchSeverity.CRITICAL)
        assert hitch_frame[0].subsystem == SubsystemType.RENDERING


class TestDeterminismDiagnostics:
    """Test 81.86.15: Determinism divergence search via binary search."""

    def test_binary_divergence_search(self):
        engine = DeterminismDiagnosticEngine()

        # Build 1000 identical frames except divergence starting at frame 374
        run_a = [f"hash_ok_{i}" for i in range(1000)]
        run_b = [f"hash_ok_{i}" if i < 374 else f"hash_diverged_{i}" for i in range(1000)]

        div_frame = engine.find_divergence_frame(run_a, run_b)
        assert div_frame == 374

    def test_component_diffing(self):
        engine = DeterminismDiagnosticEngine()
        state_a = {
            "entity_42": {"transform": {"x": 10.0, "y": 0.0}, "velocity": 5.0},
            "entity_43": {"transform": {"x": 20.0, "y": 1.0}},
        }
        state_b = {
            "entity_42": {"transform": {"x": 10.0001, "y": 0.0}, "velocity": 5.0},
            "entity_43": {"transform": {"x": 20.0, "y": 1.0}},
        }

        diffs = engine.diff_frame_states(state_a, state_b, frame_index=374)
        assert len(diffs) == 1
        assert diffs[0].entity_id == "entity_42"
        assert "transform.x" in diffs[0].divergent_properties


class TestTracesAndExports:
    """Test 81.86.16: Trace recording and Chrome Tracing JSON export."""

    def test_trace_recording_and_chrome_export(self):
        rec = UAFTraceRecorder(max_frames=100)
        rec.start_recording()

        rec.begin_frame_recording(frame_index=1, state_hash="hash_1")
        rec.record_span("SpanA", "Task1", SubsystemType.PHYSICS, 1000, 2000, 1.0)
        rec.record_metric("metric_x", 123.4)
        rec.record_event("test_event", {"info": "ok"})
        frame1 = rec.end_frame_recording()

        assert frame1 is not None
        assert frame1.frame_index == 1
        assert len(frame1.spans) == 1
        assert len(frame1.events) == 1

        # Export Chrome Tracing JSON
        chrome_json = rec.export_chrome_tracing_json()
        assert "traceEvents" in chrome_json
        assert "Frame 1" in chrome_json
        assert "Task1" in chrome_json

        # Canonical JSON
        canonical = rec.export_canonical_json()
        assert "frame_count" in canonical


class TestWatchdogAndDeadlockDetection:
    """Test 81.86.17: Thread watchdog and deadlock cycle detection."""

    def test_thread_watchdog_stall(self):
        wd = ThreadWatchdog(default_timeout_s=0.05)
        wd.register_thread("t1", "RenderThread", SubsystemType.RENDERING)
        wd.heartbeat("t1")

        # Within timeout
        stalls = wd.check_stalls()
        assert len(stalls) == 0

        # Wait past timeout
        time.sleep(0.06)
        stalls = wd.check_stalls()
        assert len(stalls) == 1
        assert stalls[0]["thread_id"] == "t1"
        assert stalls[0]["subsystem"] == SubsystemType.RENDERING.value

    def test_deadlock_detector_cycles(self):
        dd = DeadlockDetector()
        # Thread 1 owns Lock A, waits for Lock B
        # Thread 2 owns Lock B, waits for Lock A
        dd.lock_acquired("LockA", "Thread1")
        dd.lock_acquired("LockB", "Thread2")

        dd.lock_waiting("LockB", "Thread1")
        dd.lock_waiting("LockA", "Thread2")

        cycles = dd.detect_deadlocks()
        assert len(cycles) >= 1
        c = cycles[0]
        assert "Thread1" in c.thread_ids
        assert "Thread2" in c.thread_ids
        assert "LockA" in c.lock_ids
        assert "LockB" in c.lock_ids


class TestCrashHandlerAndRecovery:
    """Test 81.86.17: Crash capture and 6-level recovery escalation."""

    def test_crash_capture(self):
        ch = CrashHandler()
        ch.add_breadcrumb("Entering simulation step")
        ch.add_breadcrumb("Updating rigidbodies")

        try:
            raise ValueError("Invalid matrix determinant")
        except Exception as e:
            rep = ch.capture_crash(
                error=e,
                crash_type=CrashType.EXCEPTION,
                subsystem=SubsystemType.PHYSICS,
                frame_index=120,
                state_hash="hash_crash_120",
            )

        assert rep.subsystem == SubsystemType.PHYSICS
        assert "ValueError" in rep.error_message
        assert len(rep.breadcrumbs) == 2
        assert ch.get_last_crash() == rep

    def test_recovery_escalation_to_safe_mode(self):
        r_orch = CrashRecoveryOrchestrator(escalation_threshold_s=10.0, max_attempts_per_level=1)
        ch = CrashHandler()

        # Simulate 5 consecutive crashes in rendering subsystem
        levels_reached = []
        for i in range(5):
            rep = ch.capture_crash(
                error=f"Crash #{i}",
                crash_type=CrashType.EXCEPTION,
                subsystem=SubsystemType.RENDERING,
            )
            rec = r_orch.handle_crash(rep)
            levels_reached.append(rec.level)

        # Should escalate to Level 4 SAFE_MODE or Level 5
        assert r_orch.is_in_safe_mode is True
        assert levels_reached[0] == RecoveryLevel.LEVEL_0_COMPONENT_RESTART
        assert levels_reached[-1] in (RecoveryLevel.LEVEL_4_SAFE_MODE, RecoveryLevel.LEVEL_5_TERMINATE_CLEANLY)


class TestCentralTelemetryManager:
    """Test complete telemetry pipeline integration."""

    def test_full_frame_lifecycle(self):
        tm = TelemetryManager(mode=ProfilingMode.EXTENDED, target_fps=60.0)

        for f in range(10):
            tm.begin_frame(frame_index=f, state_hash=f"hash_{f}")
            with tm.scope("SubPhysics", SubsystemType.PHYSICS):
                time.sleep(0.001)
            frame_data = tm.end_frame(subsystem_times={SubsystemType.PHYSICS: 1.5, SubsystemType.RENDERING: 3.0})
            assert frame_data["frame_index"] == f

        report_gen = ReportGenerator(tm)
        full_report = report_gen.generate_full_report()
        assert full_report["performance"]["status"] == "ok"
        assert full_report["performance"]["frame_count"] == 10
        assert full_report["performance"]["avg_frame_time_ms"] > 0


class TestAOEDiagnosticsAndQualityGate:
    """Test AOE autonomous diagnostics, failure analysis, root causes, and certification."""

    def test_failure_analysis_and_root_cause(self):
        fa = FailureAnalyzer()
        ch = CrashHandler()
        rep = ch.capture_crash("Memory allocation failed", crash_type=CrashType.OUT_OF_MEMORY, subsystem=SubsystemType.STREAMING)
        inc = fa.ingest_crash(rep)

        assert inc.category == "crash"
        assert inc.severity == SeverityLevel.FATAL

        far = fa.generate_report()
        assert far.has_critical_failure is True
        assert "STREAMING" in far.affected_subsystems

        rca = RootCauseAnalyzer()
        hyp = rca.analyze_incident(inc)
        assert hyp.offending_subsystem == SubsystemType.STREAMING
        assert "Memory" in hyp.primary_cause
        assert hyp.confidence >= 0.85

        planner = RemediationPlanner()
        action = planner.generate_remediation(hyp)
        assert action.target_subsystem == SubsystemType.STREAMING
        assert action.automated_applicable is True

    def test_quality_gate_evaluation(self):
        qg = QualityGateEvaluator(QualityGateThresholds(max_p95_frame_time_ms=16.67, max_crashes=0))

        # Passing report
        good_perf = {"p95_frame_time_ms": 14.2, "p99_frame_time_ms": 18.0, "overrun_percentage": 0.5}
        verdict_good = qg.evaluate(good_perf, leak_count=0, crash_count=0, determinism_desync_count=0)
        assert verdict_good.result in (QualityGateResult.PASS, QualityGateResult.CERTIFY)
        assert verdict_good.score >= 90.0

        # Failing report (crashes and high frame time)
        bad_perf = {"p95_frame_time_ms": 32.0, "p99_frame_time_ms": 45.0, "overrun_percentage": 25.0}
        verdict_bad = qg.evaluate(bad_perf, leak_count=2, crash_count=1, determinism_desync_count=1)
        assert verdict_bad.result == QualityGateResult.FAIL
        assert len(verdict_bad.violations) >= 3

    def test_golden_certification_engine(self):
        runner = BenchmarkRunner()
        config = BenchmarkConfig(name="Golden Acceptance Run", total_frames=30, target_fps=60.0)
        bench_result = runner.run_benchmark(config)

        assert bench_result.total_frames == 30
        assert bench_result.mean_frame_time_ms > 0

        cert_engine = GoldenCertificationEngine()
        certificate = cert_engine.certify(benchmark_result=bench_result, memory_leaks=0, crashes=0, determinism_desyncs=0)

        assert certificate.is_certified is True
        assert certificate.determinism_verified is True
        assert len(certificate.sha256_signature) == 64
        assert "Golden Acceptance Run" in certificate.audit_log[0]
