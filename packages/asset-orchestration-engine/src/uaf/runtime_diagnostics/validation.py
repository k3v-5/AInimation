"""Validation and integrity verification of telemetry metrics, spans, and traces."""

from __future__ import annotations
import math
from typing import Any, Dict, List, Optional
from uaf.runtime_diagnostics.traces import TraceFrameRecord, TraceSpanRecord
from uaf.runtime_diagnostics.budget import FrameBudgetManager


class TelemetryValidator:
    """Validates structural correctness and numerical sanity of telemetry data."""

    @staticmethod
    def validate_number(value: float, name: str = "metric") -> List[str]:
        errors = []
        if math.isnan(value):
            errors.append(f"{name} is NaN")
        elif math.isinf(value):
            errors.append(f"{name} is Infinite")
        return errors

    @staticmethod
    def validate_budget_manager(budget_mgr: FrameBudgetManager) -> List[str]:
        errors = []
        sum_targets = sum(b.target_ms for b in budget_mgr.budgets.values())
        if abs(sum_targets - budget_mgr.total_budget_ms) > 0.05:
            errors.append(
                f"Budget sum mismatch: sum of subsystem targets ({sum_targets:.2f}ms) "
                f"differs from total frame budget ({budget_mgr.total_budget_ms:.2f}ms)"
            )
        return errors

    @staticmethod
    def validate_trace_spans(spans: List[TraceSpanRecord]) -> List[str]:
        errors = []
        span_map = {s.span_id: s for s in spans}

        for span in spans:
            if span.duration_ms < 0:
                errors.append(f"Span '{span.name}' ({span.span_id}) has negative duration: {span.duration_ms}")
            if span.end_time_ns < span.start_time_ns:
                errors.append(f"Span '{span.name}' ({span.span_id}) end_time < start_time")
            if span.parent_id and span.parent_id not in span_map:
                errors.append(f"Span '{span.name}' references missing parent_id '{span.parent_id}'")

        return errors

    @staticmethod
    def validate_trace_frames(frames: List[TraceFrameRecord]) -> List[str]:
        errors = []
        prev_idx: Optional[int] = None

        for frame in frames:
            if prev_idx is not None and frame.frame_index <= prev_idx:
                errors.append(f"Frame indices not strictly monotonic: previous {prev_idx} >= current {frame.frame_index}")
            prev_idx = frame.frame_index

            if frame.duration_ms < 0:
                errors.append(f"Frame {frame.frame_index} has negative duration: {frame.duration_ms}")

            errors.extend(TelemetryValidator.validate_trace_spans(frame.spans))

        return errors
