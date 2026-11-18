"""
Hierarchical Profiling Spans & Scopes for UAF-81.86.
"""

from __future__ import annotations
import time
import uuid
from typing import Dict, List, Optional

from .core import SpanId, SubsystemType
from .metrics import TelemetrySpan


class SpanScope:
    """Context manager for hierarchical profiling spans."""

    def __init__(
        self,
        manager: SpanManager,
        name: str,
        subsystem: SubsystemType,
        tags: Optional[Dict[str, str]] = None,
    ) -> None:
        self.manager = manager
        self.name = name
        self.subsystem = subsystem
        self.tags = tags
        self.span: Optional[TelemetrySpan] = None

    def __enter__(self) -> TelemetrySpan:
        self.span = self.manager.begin_span(self.name, self.subsystem, self.tags)
        return self.span

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        if self.span:
            self.manager.end_span(self.span)


class SpanManager:
    """
    Manages active hierarchical profiling spans (tree of execution scopes).
    """

    def __init__(self) -> None:
        self.active_stack: List[TelemetrySpan] = []
        self.root_spans: List[TelemetrySpan] = []
        self.completed_spans: List[TelemetrySpan] = []
        self.span_counter: int = 0

    def begin_span(
        self,
        name: str,
        subsystem: SubsystemType,
        tags: Optional[Dict[str, str]] = None
    ) -> TelemetrySpan:
        """Starts a new profiling span, nesting it under the current active span if one exists."""
        self.span_counter += 1
        span_id = SpanId(f"span_{self.span_counter}_{name}")
        parent_id = self.active_stack[-1].span_id if self.active_stack else None

        span = TelemetrySpan(
            span_id=span_id,
            name=name,
            subsystem=subsystem,
            start_timestamp=time.perf_counter(),
            parent_span_id=parent_id,
            tags=tags or {},
        )

        if self.active_stack:
            self.active_stack[-1].children.append(span)
        else:
            self.root_spans.append(span)

        self.active_stack.append(span)
        return span

    def end_span(self, target_span: Optional[TelemetrySpan] = None) -> TelemetrySpan:
        """Ends the innermost span or a specifically targeted span."""
        if not self.active_stack:
            raise RuntimeError("No active span to end.")

        if target_span is not None and target_span in self.active_stack:
            while self.active_stack and self.active_stack[-1] != target_span:
                span_to_close = self.active_stack.pop()
                span_to_close.complete()
                self.completed_spans.append(span_to_close)
            span = self.active_stack.pop()
            span.complete()
            self.completed_spans.append(span)
            return span
        else:
            span = self.active_stack.pop()
            span.complete()
            self.completed_spans.append(span)
            return span

    def scope(
        self,
        name: str,
        subsystem: SubsystemType,
        tags: Optional[Dict[str, str]] = None,
    ) -> SpanScope:
        return SpanScope(self, name, subsystem, tags)

    def get_completed_spans(self, clear: bool = True) -> List[TelemetrySpan]:
        spans = list(self.completed_spans)
        if clear:
            self.completed_spans.clear()
        return spans

    def clear(self) -> None:
        self.active_stack.clear()
        self.root_spans.clear()
        self.completed_spans.clear()
