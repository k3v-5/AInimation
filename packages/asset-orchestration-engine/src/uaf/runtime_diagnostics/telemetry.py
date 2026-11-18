"""Central telemetry manager orchestrating metrics, spans, ring buffers, budgets, and profilers."""

from __future__ import annotations
import time
from typing import Any, Dict, List, Optional
from uaf.runtime_diagnostics.core import (
    ProfilingMode,
    SubsystemType,
    ensure_finite_float,
)
from uaf.runtime_diagnostics.buffers import TelemetryBuffer
from uaf.runtime_diagnostics.spans import SpanManager, SpanScope
from uaf.runtime_diagnostics.metrics import TelemetryCounter, TelemetryGauge, TelemetryHistogram
from uaf.runtime_diagnostics.budget import FrameBudgetManager
from uaf.runtime_diagnostics.memory_profiler import MemoryProfiler
from uaf.runtime_diagnostics.subsystem_profilers import (
    StreamingProfiler,
    PhysicsProfiler,
    AIProfiler,
    NetworkProfiler,
    AnimationProfiler,
    VFXProfiler,
    LightingProfiler,
    RenderProfiler,
    AudioProfiler,
    UIProfiler,
)
from uaf.runtime_diagnostics.anomalies import AnomalyDetector, PerformanceAnomaly
from uaf.runtime_diagnostics.crash import CrashHandler
from uaf.runtime_diagnostics.watchdog import ThreadWatchdog, DeadlockDetector
from uaf.runtime_diagnostics.recovery import CrashRecoveryOrchestrator
from uaf.runtime_diagnostics.traces import UAFTraceRecorder
from uaf.runtime_diagnostics.determinism import DeterminismDiagnosticEngine
from uaf.runtime_diagnostics.regression import RegressionEngine


class TelemetryManager:
    """Universal Telemetry & Runtime Diagnostics Manager for AOE & UAF."""

    def __init__(
        self,
        mode: ProfilingMode = ProfilingMode.EXTENDED,
        target_fps: float = 60.0,
        buffer_capacity: int = 600,
    ) -> None:
        self.mode = mode
        self.target_fps = target_fps
        self.buffer_capacity = buffer_capacity

        # Core subsystems
        self.frame_buffer: TelemetryBuffer[Dict[str, Any]] = TelemetryBuffer(capacity=buffer_capacity)
        self.event_buffer: TelemetryBuffer[Dict[str, Any]] = TelemetryBuffer(capacity=buffer_capacity * 2)

        self.spans = SpanManager()
        self.budgets = FrameBudgetManager(target_fps=target_fps)
        self.memory = MemoryProfiler()
        self.anomalies = AnomalyDetector()
        self.crash_handler = CrashHandler()
        self.watchdog = ThreadWatchdog()
        self.deadlocks = DeadlockDetector()
        self.recovery = CrashRecoveryOrchestrator()
        self.traces = UAFTraceRecorder(max_frames=buffer_capacity)
        self.determinism = DeterminismDiagnosticEngine()
        self.regression = RegressionEngine()

        # Dedicated subsystem profilers
        self.streaming = StreamingProfiler()
        self.physics = PhysicsProfiler()
        self.ai = AIProfiler()
        self.network = NetworkProfiler()
        self.animation = AnimationProfiler()
        self.vfx = VFXProfiler()
        self.lighting = LightingProfiler()
        self.render = RenderProfiler()
        self.audio = AudioProfiler()
        self.ui = UIProfiler()

        # Metrics aggregates
        self.counters: Dict[str, TelemetryCounter] = {}
        self.gauges: Dict[str, TelemetryGauge] = {}
        self.histograms: Dict[str, TelemetryHistogram] = {}

        # Frame timing state
        self._current_frame_index: Optional[int] = None
        self._frame_start_ns: int = 0
        self._current_state_hash: str = ""

    def set_mode(self, mode: ProfilingMode) -> None:
        self.mode = mode
        if mode == ProfilingMode.OFF:
            self.traces.stop_recording()
        elif mode in (ProfilingMode.EXTENDED, ProfilingMode.DEEP):
            self.traces.start_recording()

    def get_counter(self, name: str, subsystem: SubsystemType = SubsystemType.GENERAL) -> TelemetryCounter:
        if name not in self.counters:
            self.counters[name] = TelemetryCounter(metric_id=name, name=name, subsystem=subsystem)
        return self.counters[name]

    def get_gauge(self, name: str, subsystem: SubsystemType = SubsystemType.GENERAL) -> TelemetryGauge:
        if name not in self.gauges:
            self.gauges[name] = TelemetryGauge(metric_id=name, name=name, subsystem=subsystem)
        return self.gauges[name]

    def get_histogram(self, name: str, subsystem: SubsystemType = SubsystemType.GENERAL) -> TelemetryHistogram:
        if name not in self.histograms:
            self.histograms[name] = TelemetryHistogram(metric_id=name, name=name, subsystem=subsystem)
        return self.histograms[name]

    def record_event(self, name: str, subsystem: SubsystemType, payload: Optional[Dict[str, Any]] = None) -> None:
        if self.mode == ProfilingMode.OFF:
            return
        ev = {
            "name": name,
            "subsystem": subsystem.value,
            "timestamp_ns": time.perf_counter_ns(),
            "frame_index": self._current_frame_index,
            "payload": payload or {},
        }
        self.event_buffer.push(ev)
        if self.traces.is_recording:
            self.traces.record_event(name, payload)

    def scope(self, name: str, subsystem: SubsystemType, tags: Optional[Dict[str, Any]] = None) -> SpanScope:
        return self.spans.scope(name, subsystem, tags)

    def begin_frame(self, frame_index: int, state_hash: str = "") -> None:
        if self.mode == ProfilingMode.OFF:
            return
        self._current_frame_index = frame_index
        self._frame_start_ns = time.perf_counter_ns()
        self._current_state_hash = state_hash
        self.budgets.begin_frame()

        if self.traces.is_recording:
            self.traces.begin_frame_recording(frame_index, state_hash)

    def end_frame(
        self,
        subsystem_times: Optional[Dict[SubsystemType, float]] = None,
    ) -> Dict[str, Any]:
        if self.mode == ProfilingMode.OFF or self._current_frame_index is None:
            return {}

        now_ns = time.perf_counter_ns()
        total_frame_ms = max(0.001, (now_ns - self._frame_start_ns) / 1_000_000.0)
        frame_idx = self._current_frame_index

        # Apply timings to budget manager
        if subsystem_times:
            for subsys, duration in subsystem_times.items():
                self.budgets.record_duration(subsys, duration)

        budget_summary = self.budgets.end_frame(total_frame_ms)

        # Build subsystem profiling snapshot
        subsys_metrics = {
            "streaming": self.streaming.to_dict(),
            "physics": self.physics.to_dict(),
            "ai": self.ai.to_dict(),
            "network": self.network.to_dict(),
            "animation": self.animation.to_dict(),
            "vfx": self.vfx.to_dict(),
            "lighting": self.lighting.to_dict(),
            "render": self.render.to_dict(),
            "audio": self.audio.to_dict(),
            "ui": self.ui.to_dict(),
        }

        # Anomaly detection
        hitch_threshold = (1000.0 / self.target_fps) * 1.5
        anomalies = self.anomalies.feed_frame(
            frame_index=frame_idx,
            frame_time_ms=total_frame_ms,
            subsystem_times={k.value: v for k, v in (subsystem_times or {}).items()},
            hitch_threshold_ms=hitch_threshold,
        )

        # Freeze buffers if catastrophic hitch occurred
        for a in anomalies:
            if a.hitch_severity and a.hitch_severity.value in ("severe", "critical"):
                self.frame_buffer.freeze()
                self.event_buffer.freeze()

        # Update trace recorder
        if self.traces.is_recording:
            # Transfer completed spans
            for span in self.spans.get_completed_spans():
                self.traces.record_span(
                    span_id=span.span_id,
                    name=span.name,
                    subsystem=span.subsystem,
                    start_time_ns=span.start_time_ns,
                    end_time_ns=span.end_time_ns,
                    duration_ms=span.duration_ms,
                    parent_id=span.parent_id,
                    tags=span.tags,
                )
            self.traces.end_frame_recording(
                metrics={"frame_time_ms": total_frame_ms},
                state_hash=self._current_state_hash,
            )

        frame_record = {
            "frame_index": frame_idx,
            "duration_ms": ensure_finite_float(total_frame_ms),
            "state_hash": self._current_state_hash,
            "budget": budget_summary,
            "anomalies": [a.to_dict() for a in anomalies],
            "subsystems": subsys_metrics,
        }

        self.frame_buffer.push(frame_record)
        self._current_frame_index = None
        return frame_record
