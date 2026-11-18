"""
Telemetry Metrics (Counter, Gauge, Histogram, Span, Event) for UAF-81.86.
"""

from __future__ import annotations
import math
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

from .core import (
    MetricId,
    SpanId,
    MetricType,
    MetricUnit,
    SubsystemType,
    SeverityLevel,
    ensure_finite_scalar,
)


@dataclass
class TelemetryMetric:
    """Base class for all telemetry metrics."""
    metric_id: MetricId
    name: str = ""
    subsystem: SubsystemType = SubsystemType.GENERAL
    metric_type: MetricType = MetricType.COUNTER
    unit: MetricUnit = MetricUnit.MILLISECONDS
    description: str = ""
    tags: Dict[str, str] = field(default_factory=dict)


@dataclass
class TelemetryCounter(TelemetryMetric):
    """Monotonically increasing cumulative counter."""
    value: float = 0.0

    def __post_init__(self) -> None:
        self.metric_type = MetricType.COUNTER

    def increment(self, delta: float = 1.0) -> None:
        if delta > 0.0:
            self.value += ensure_finite_scalar(delta, "delta", 0.0)

    def reset(self) -> None:
        self.value = 0.0


@dataclass
class TelemetryGauge(TelemetryMetric):
    """Instantaneous numerical level or reading."""
    value: float = 0.0

    def __post_init__(self) -> None:
        self.metric_type = MetricType.GAUGE

    def set_value(self, val: float) -> None:
        self.value = ensure_finite_scalar(val, "val", 0.0)

    def set(self, val: float) -> None:
        self.set_value(val)


@dataclass
class TelemetryHistogram(TelemetryMetric):
    """Tracks numerical value distributions and calculates percentiles."""
    values: List[float] = field(default_factory=list)
    max_samples: int = 1000

    def __post_init__(self) -> None:
        self.metric_type = MetricType.HISTOGRAM

    def record(self, val: float) -> None:
        finite_val = ensure_finite_scalar(val, "val", 0.0)
        self.values.append(finite_val)
        if len(self.values) > self.max_samples:
            self.values.pop(0)

    @property
    def count(self) -> int:
        return len(self.values)

    @property
    def sum_val(self) -> float:
        return sum(self.values)

    @property
    def mean(self) -> float:
        return (sum(self.values) / float(len(self.values))) if self.values else 0.0

    @property
    def min_val(self) -> float:
        return min(self.values) if self.values else 0.0

    @property
    def max_val(self) -> float:
        return max(self.values) if self.values else 0.0

    def percentile(self, p: float) -> float:
        """Calculates percentile p in [0.0, 100.0]."""
        if not self.values:
            return 0.0
        sorted_vals = sorted(self.values)
        k = (len(sorted_vals) - 1) * (max(0.0, min(100.0, p)) / 100.0)
        f = math.floor(k)
        c = math.ceil(k)
        if f == c:
            return sorted_vals[int(k)]
        d0 = sorted_vals[int(f)] * (c - k)
        d1 = sorted_vals[int(c)] * (k - f)
        return d0 + d1


@dataclass
class TelemetrySpan:
    """Represents a scoped hierarchical block of execution time."""
    span_id: SpanId
    name: str
    subsystem: SubsystemType
    start_timestamp: float
    end_timestamp: Optional[float] = None
    duration_ms: float = 0.0
    parent_span_id: Optional[SpanId] = None
    tags: Dict[str, str] = field(default_factory=dict)
    children: List[TelemetrySpan] = field(default_factory=list)

    def complete(self, end_ts: Optional[float] = None) -> None:
        self.end_timestamp = end_ts or time.perf_counter()
        self.duration_ms = max(0.0, (self.end_timestamp - self.start_timestamp) * 1000.0)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "span_id": self.span_id.value,
            "name": self.name,
            "subsystem": self.subsystem.value,
            "start_timestamp": self.start_timestamp,
            "end_timestamp": self.end_timestamp,
            "duration_ms": round(self.duration_ms, 4),
            "parent_span_id": self.parent_span_id.value if self.parent_span_id else None,
            "children": [c.to_dict() for c in self.children],
            "tags": self.tags,
        }


@dataclass
class TelemetryEvent:
    """Discrete point-in-time telemetry or diagnostic event."""
    event_id: str
    severity: SeverityLevel
    subsystem: SubsystemType
    timestamp: float
    frame_index: int
    message: str
    source_id: Optional[str] = None
    payload: Dict[str, Any] = field(default_factory=dict)
    state_hash: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_id": self.event_id,
            "severity": self.severity.value,
            "subsystem": self.subsystem.value,
            "timestamp": round(self.timestamp, 4),
            "frame_index": self.frame_index,
            "message": self.message,
            "source_id": self.source_id,
            "payload": self.payload,
            "state_hash": self.state_hash,
        }
