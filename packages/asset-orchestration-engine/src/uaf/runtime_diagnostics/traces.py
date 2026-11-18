"""Universal trace recording, Chrome trace export, and canonical trace serialization."""

from __future__ import annotations
import json
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from uaf.runtime_diagnostics.core import SubsystemType, ensure_finite_float


@dataclass
class TraceSpanRecord:
    span_id: str
    name: str
    subsystem: SubsystemType
    start_time_ns: int
    end_time_ns: int
    duration_ms: float
    parent_id: Optional[str] = None
    tags: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "span_id": self.span_id,
            "name": self.name,
            "subsystem": self.subsystem.value,
            "start_time_ns": self.start_time_ns,
            "end_time_ns": self.end_time_ns,
            "duration_ms": ensure_finite_float(self.duration_ms),
            "parent_id": self.parent_id,
            "tags": self.tags,
        }


@dataclass
class TraceFrameRecord:
    frame_index: int
    start_time_ns: int
    end_time_ns: int
    duration_ms: float
    state_hash: str
    spans: List[TraceSpanRecord] = field(default_factory=list)
    metrics: Dict[str, float] = field(default_factory=dict)
    events: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "frame_index": self.frame_index,
            "start_time_ns": self.start_time_ns,
            "end_time_ns": self.end_time_ns,
            "duration_ms": ensure_finite_float(self.duration_ms),
            "state_hash": self.state_hash,
            "spans": [s.to_dict() for s in self.spans],
            "metrics": {k: ensure_finite_float(v) for k, v in self.metrics.items()},
            "events": self.events,
        }


class UAFTraceRecorder:
    """High-performance trace recorder with bounded frame storage and Chrome Tracing export."""

    def __init__(self, max_frames: int = 1200) -> None:
        self.max_frames = max(10, max_frames)
        self.frames: List[TraceFrameRecord] = []
        self._is_recording = False
        self._current_frame_index: Optional[int] = None
        self._current_frame_start_ns: int = 0
        self._current_frame_hash: str = ""
        self._current_frame_spans: List[TraceSpanRecord] = []
        self._current_frame_metrics: Dict[str, float] = {}
        self._current_frame_events: List[Dict[str, Any]] = []

    @property
    def is_recording(self) -> bool:
        return self._is_recording

    def start_recording(self) -> None:
        self._is_recording = True

    def stop_recording(self) -> None:
        self._is_recording = False
        if self._current_frame_index is not None:
            self.end_frame_recording()

    def clear(self) -> None:
        self.frames.clear()
        self._current_frame_index = None
        self._current_frame_spans.clear()
        self._current_frame_metrics.clear()
        self._current_frame_events.clear()

    def begin_frame_recording(self, frame_index: int, state_hash: str = "") -> None:
        if not self._is_recording:
            return
        if self._current_frame_index is not None:
            self.end_frame_recording()

        self._current_frame_index = frame_index
        self._current_frame_start_ns = time.perf_counter_ns()
        self._current_frame_hash = state_hash
        self._current_frame_spans = []
        self._current_frame_metrics = {}
        self._current_frame_events = []

    def record_span(
        self,
        span_id: str,
        name: str,
        subsystem: SubsystemType,
        start_time_ns: int,
        end_time_ns: int,
        duration_ms: float,
        parent_id: Optional[str] = None,
        tags: Optional[Dict[str, Any]] = None,
    ) -> None:
        if not self._is_recording or self._current_frame_index is None:
            return
        self._current_frame_spans.append(
            TraceSpanRecord(
                span_id=span_id,
                name=name,
                subsystem=subsystem,
                start_time_ns=start_time_ns,
                end_time_ns=end_time_ns,
                duration_ms=ensure_finite_float(duration_ms),
                parent_id=parent_id,
                tags=tags or {},
            )
        )

    def record_metric(self, name: str, value: float) -> None:
        if not self._is_recording or self._current_frame_index is None:
            return
        self._current_frame_metrics[name] = ensure_finite_float(value)

    def record_event(self, event_name: str, payload: Optional[Dict[str, Any]] = None) -> None:
        if not self._is_recording or self._current_frame_index is None:
            return
        self._current_frame_events.append({
            "name": event_name,
            "timestamp_ns": time.perf_counter_ns(),
            "payload": payload or {},
        })

    def end_frame_recording(
        self,
        metrics: Optional[Dict[str, float]] = None,
        events: Optional[List[Dict[str, Any]]] = None,
        state_hash: Optional[str] = None,
    ) -> Optional[TraceFrameRecord]:
        if not self._is_recording or self._current_frame_index is None:
            return None

        end_ns = time.perf_counter_ns()
        duration_ms = max(0.0, (end_ns - self._current_frame_start_ns) / 1_000_000.0)

        if metrics:
            self._current_frame_metrics.update(metrics)
        if events:
            self._current_frame_events.extend(events)
        if state_hash:
            self._current_frame_hash = state_hash

        record = TraceFrameRecord(
            frame_index=self._current_frame_index,
            start_time_ns=self._current_frame_start_ns,
            end_time_ns=end_ns,
            duration_ms=duration_ms,
            state_hash=self._current_frame_hash,
            spans=list(self._current_frame_spans),
            metrics=dict(self._current_frame_metrics),
            events=list(self._current_frame_events),
        )

        if len(self.frames) >= self.max_frames:
            self.frames.pop(0)
        self.frames.append(record)

        self._current_frame_index = None
        self._current_frame_spans.clear()
        self._current_frame_metrics.clear()
        self._current_frame_events.clear()
        return record

    def get_frame(self, frame_index: int) -> Optional[TraceFrameRecord]:
        for f in self.frames:
            if f.frame_index == frame_index:
                return f
        return None

    def export_canonical_dict(self) -> Dict[str, Any]:
        return {
            "version": "1.0.0",
            "frame_count": len(self.frames),
            "frames": [f.to_dict() for f in self.frames],
        }

    def export_canonical_json(self, indent: Optional[int] = None) -> str:
        return json.dumps(self.export_canonical_dict(), indent=indent, sort_keys=True)

    def export_chrome_tracing_json(self) -> str:
        """Export in standard Chrome Tracing / Perfetto format (JSON array of trace events)."""
        events: List[Dict[str, Any]] = []

        for frame in self.frames:
            # Frame boundary event
            events.append({
                "name": f"Frame {frame.frame_index}",
                "cat": "frame",
                "ph": "X",  # Complete event
                "ts": frame.start_time_ns // 1000,  # microseconds
                "dur": max(1, (frame.end_time_ns - frame.start_time_ns) // 1000),
                "pid": 1,
                "tid": 1,
                "args": {
                    "frame_index": frame.frame_index,
                    "state_hash": frame.state_hash,
                    "duration_ms": frame.duration_ms,
                },
            })

            # Spans
            for span in frame.spans:
                events.append({
                    "name": span.name,
                    "cat": span.subsystem.value,
                    "ph": "X",
                    "ts": span.start_time_ns // 1000,
                    "dur": max(1, (span.end_time_ns - span.start_time_ns) // 1000),
                    "pid": 1,
                    "tid": span.subsystem.value,
                    "args": {
                        "span_id": span.span_id,
                        "duration_ms": span.duration_ms,
                        **span.tags,
                    },
                })

            # Instant events
            for ev in frame.events:
                events.append({
                    "name": ev["name"],
                    "cat": "event",
                    "ph": "i",  # Instant event
                    "ts": ev.get("timestamp_ns", frame.start_time_ns) // 1000,
                    "pid": 1,
                    "tid": 1,
                    "s": "g",  # Global scope
                    "args": ev.get("payload", {}),
                })

        return json.dumps({"traceEvents": events, "displayTimeUnit": "ms"}, indent=2)
