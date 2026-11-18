"""
Core Contracts, Enums, Identifiers & Units for UAF-81.86.
"""

from __future__ import annotations
import math
import json
import hashlib
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Dict, List, Optional, Tuple


# ---------------------------------------------------------------------------
# Identifiers
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class MetricId:
    """Stable, unique identifier for a metric."""
    value: str

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class SpanId:
    """Stable identifier for a profiling span."""
    value: str

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class SessionId:
    """Unique identifier for a profiling/telemetry session."""
    value: str

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class AllocationId:
    """Unique identifier for a tracked memory allocation."""
    value: str

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class DiagnosticEventId:
    """Unique identifier for a diagnostic report event."""
    value: str

    def __str__(self) -> str:
        return self.value


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class MetricType(str, Enum):
    COUNTER = "COUNTER"
    GAUGE = "GAUGE"
    HISTOGRAM = "HISTOGRAM"
    TIMER = "TIMER"
    RATE = "RATE"
    EVENT = "EVENT"
    SPAN = "SPAN"
    SIZE = "SIZE"
    COUNT = "COUNT"


class MetricUnit(str, Enum):
    MILLISECONDS = "milliseconds"
    MICROSECONDS = "microseconds"
    BYTES = "bytes"
    KILOBYTES = "kilobytes"
    MEGABYTES = "megabytes"
    GIGABYTES = "gigabytes"
    FRAMES = "frames"
    ENTITIES = "entities"
    DRAW_CALLS = "draw_calls"
    TRIANGLES = "triangles"
    PACKETS = "packets"
    KB_PER_SECOND = "kilobytes_per_second"
    PERCENT = "percent"


class SubsystemType(str, Enum):
    GAMEPLAY = "GAMEPLAY"
    PHYSICS = "PHYSICS"
    AI = "AI"
    ANIMATION = "ANIMATION"
    VFX = "VFX"
    LIGHTING = "LIGHTING"
    RENDERING = "RENDERING"
    AUDIO = "AUDIO"
    STREAMING = "STREAMING"
    NETWORKING = "NETWORKING"
    UI = "UI"
    TELEMETRY = "TELEMETRY"
    GENERAL = "GENERAL"


class ProfilingMode(str, Enum):
    OFF = "OFF"
    BASIC = "BASIC"
    EXTENDED = "EXTENDED"
    DEEP = "DEEP"
    PROFILING_MODE = "PROFILING_MODE"
    DIAGNOSTIC_MODE = "DIAGNOSTIC_MODE"
    BENCHMARK_MODE = "BENCHMARK_MODE"
    CI_MODE = "CI_MODE"
    DEVELOPMENT_MODE = "DEVELOPMENT_MODE"
    SHIPPING_MODE = "SHIPPING_MODE"
    EMERGENCY_MODE = "EMERGENCY_MODE"


class InstrumentationLevel(str, Enum):
    OFF = "OFF"
    MINIMAL = "MINIMAL"
    STANDARD = "STANDARD"
    DETAILED = "DETAILED"
    VERBOSE = "VERBOSE"
    TRACE = "TRACE"


class SeverityLevel(str, Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    BLOCKING_WARNING = "BLOCKING_WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"
    FATAL = "CRITICAL"
    PERFORMANCE_WARNING = "PERFORMANCE_WARNING"
    BUDGET_VIOLATION = "BUDGET_VIOLATION"
    RESOURCE_LEAK = "RESOURCE_LEAK"
    STREAMING_FAILURE = "STREAMING_FAILURE"
    NETWORK_ANOMALY = "NETWORK_ANOMALY"
    DETERMINISM_FAILURE = "DETERMINISM_FAILURE"


class CrashType(str, Enum):
    ASSERT = "ASSERT"
    EXCEPTION = "EXCEPTION"
    UNHANDLED_EXCEPTION = "EXCEPTION"
    PANIC = "PANIC"
    ACCESS_VIOLATION = "ACCESS_VIOLATION"
    OUT_OF_MEMORY = "OUT_OF_MEMORY"
    GPU_FAILURE = "GPU_FAILURE"
    DEVICE_LOST = "DEVICE_LOST"
    STACK_OVERFLOW = "STACK_OVERFLOW"
    DEADLOCK = "DEADLOCK"
    WATCHDOG_TIMEOUT = "WATCHDOG_TIMEOUT"
    CORRUPTION = "CORRUPTION"
    UNKNOWN = "UNKNOWN"


class RecoveryLevel(str, Enum):
    LEVEL_0_COMPONENT_RESTART = "LEVEL_0_COMPONENT_RESTART"
    LEVEL_1_RESOURCE_RELOAD = "LEVEL_1_RESOURCE_RELOAD"
    LEVEL_2_SUBSYSTEM_RESTART = "LEVEL_2_SUBSYSTEM_RESTART"
    LEVEL_3_CHECKPOINT_RESTORE = "LEVEL_3_CHECKPOINT_RESTORE"
    LEVEL_4_SAFE_MODE = "LEVEL_4_SAFE_MODE"
    LEVEL_5_TERMINATE_CLEANLY = "LEVEL_5_TERMINATE_CLEANLY"
    LEVEL_5_CONTROLLED_SHUTDOWN = "LEVEL_5_TERMINATE_CLEANLY"


class QualityGateResult(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    RETRY = "RETRY"
    DEGRADE = "DEGRADE"
    ROLLBACK = "ROLLBACK"
    QUARANTINE = "QUARANTINE"
    CERTIFIED = "CERTIFIED"
    CERTIFY = "CERTIFIED"


# ---------------------------------------------------------------------------
# Numeric Validation
# ---------------------------------------------------------------------------

def ensure_finite_scalar(val: Any, name: str, default: float = 0.0) -> float:
    try:
        f = float(val)
        if math.isnan(f) or math.isinf(f):
            return default
        return f
    except (TypeError, ValueError):
        return default


def ensure_finite_float(val: Any, default: float = 0.0) -> float:
    return ensure_finite_scalar(val, "", default)
