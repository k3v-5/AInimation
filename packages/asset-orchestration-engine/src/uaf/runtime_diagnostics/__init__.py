"""UAF Runtime Diagnostics, Profiling, Telemetry, Frame Budgeting & Crash Recovery Package."""

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
)
from uaf.runtime_diagnostics.metrics import (
    TelemetryMetric,
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
    PhysicsProfiler,
    AIProfiler,
    NetworkProfiler,
    AnimationProfiler,
    VFXProfiler,
    DiagnosticsVFXProfiler,
    LightingProfiler,
    DiagnosticsLightingProfiler,
    RenderProfiler,
    AudioProfiler,
    UIProfiler,
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
)
from uaf.runtime_diagnostics.telemetry import TelemetryManager
from uaf.runtime_diagnostics.reports import ReportGenerator
from uaf.runtime_diagnostics.validation import TelemetryValidator

__all__ = [
    "MetricId",
    "SpanId",
    "SessionId",
    "AllocationId",
    "DiagnosticEventId",
    "MetricType",
    "MetricUnit",
    "SubsystemType",
    "ProfilingMode",
    "InstrumentationLevel",
    "SeverityLevel",
    "CrashType",
    "RecoveryLevel",
    "QualityGateResult",
    "ensure_finite_float",
    "TelemetryMetric",
    "TelemetryCounter",
    "TelemetryGauge",
    "TelemetryHistogram",
    "TelemetrySpan",
    "TelemetryEvent",
    "TelemetryBuffer",
    "SpanManager",
    "SpanScope",
    "SubsystemBudget",
    "FrameBudgetManager",
    "MemoryAllocation",
    "MemorySnapshot",
    "MemoryLeakInfo",
    "MemoryProfiler",
    "StreamingProfiler",
    "PhysicsProfiler",
    "AIProfiler",
    "NetworkProfiler",
    "AnimationProfiler",
    "VFXProfiler",
    "DiagnosticsVFXProfiler",
    "LightingProfiler",
    "DiagnosticsLightingProfiler",
    "RenderProfiler",
    "AudioProfiler",
    "UIProfiler",
    "AnomalyType",
    "HitchSeverity",
    "PerformanceAnomaly",
    "AnomalyDetector",
    "BenchmarkBaseline",
    "RegressionReport",
    "RegressionEngine",
    "DivergencePoint",
    "DeterminismDiagnosticEngine",
    "TraceSpanRecord",
    "TraceFrameRecord",
    "UAFTraceRecorder",
    "CrashReport",
    "CrashHandler",
    "ThreadWatchdog",
    "DeadlockDetector",
    "DeadlockCycle",
    "CrashRecoveryOrchestrator",
    "RecoveryRecord",
    "TelemetryManager",
    "ReportGenerator",
    "TelemetryValidator",
]
