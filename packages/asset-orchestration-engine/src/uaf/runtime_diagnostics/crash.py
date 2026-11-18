"""Crash capture, classification, diagnostic dump, and crash context tracking."""

from __future__ import annotations
import os
import platform
import sys
import time
import traceback
import uuid
import json
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional
from uaf.runtime_diagnostics.core import CrashType, SubsystemType


@dataclass
class CrashReport:
    crash_id: str
    timestamp_ns: int
    crash_type: CrashType
    subsystem: SubsystemType
    error_message: str
    stack_trace: str
    frame_index: Optional[int] = None
    state_hash: Optional[str] = None
    active_spans: List[str] = field(default_factory=list)
    breadcrumbs: List[str] = field(default_factory=list)
    system_info: Dict[str, Any] = field(default_factory=dict)
    extra_context: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "crash_id": self.crash_id,
            "timestamp_ns": self.timestamp_ns,
            "crash_type": self.crash_type.value,
            "subsystem": self.subsystem.value,
            "error_message": self.error_message,
            "stack_trace": self.stack_trace,
            "frame_index": self.frame_index,
            "state_hash": self.state_hash,
            "active_spans": list(self.active_spans),
            "breadcrumbs": list(self.breadcrumbs),
            "system_info": dict(self.system_info),
            "extra_context": dict(self.extra_context),
        }

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent, sort_keys=True)


class CrashHandler:
    """Subsystem crash handler providing fail-safe crash capture without crashing the telemetry pipeline."""

    def __init__(self, max_history: int = 50, max_breadcrumbs: int = 100) -> None:
        self.max_history = max_history
        self.max_breadcrumbs = max_breadcrumbs
        self.crash_history: List[CrashReport] = []
        self._breadcrumbs: List[str] = []
        self._listeners: List[Callable[[CrashReport], None]] = []

    def add_listener(self, listener: Callable[[CrashReport], None]) -> None:
        self._listeners.append(listener)

    def add_breadcrumb(self, message: str) -> None:
        if len(self._breadcrumbs) >= self.max_breadcrumbs:
            self._breadcrumbs.pop(0)
        timestamp = time.strftime("%H:%M:%S")
        self._breadcrumbs.append(f"[{timestamp}] {message}")

    def capture_crash(
        self,
        error: Exception | str,
        crash_type: CrashType = CrashType.UNHANDLED_EXCEPTION,
        subsystem: SubsystemType = SubsystemType.GENERAL,
        frame_index: Optional[int] = None,
        state_hash: Optional[str] = None,
        active_spans: Optional[List[str]] = None,
        extra_context: Optional[Dict[str, Any]] = None,
    ) -> CrashReport:
        crash_id = f"crash_{uuid.uuid4().hex[:12]}"
        timestamp_ns = time.perf_counter_ns()

        if isinstance(error, Exception):
            error_message = f"{type(error).__name__}: {str(error)}"
            tb = traceback.format_exception(type(error), error, error.__traceback__)
            stack_trace = "".join(tb)
        else:
            error_message = str(error)
            stack_trace = "".join(traceback.format_stack())

        sys_info = {
            "platform": platform.platform(),
            "python_version": sys.version,
            "pid": os.getpid(),
        }

        report = CrashReport(
            crash_id=crash_id,
            timestamp_ns=timestamp_ns,
            crash_type=crash_type,
            subsystem=subsystem,
            error_message=error_message,
            stack_trace=stack_trace,
            frame_index=frame_index,
            state_hash=state_hash,
            active_spans=list(active_spans or []),
            breadcrumbs=list(self._breadcrumbs),
            system_info=sys_info,
            extra_context=dict(extra_context or {}),
        )

        if len(self.crash_history) >= self.max_history:
            self.crash_history.pop(0)
        self.crash_history.append(report)

        # Notify listeners safely
        for listener in self._listeners:
            try:
                listener(report)
            except Exception:
                pass  # Telemetry crash handler must never throw

        return report

    def get_last_crash(self) -> Optional[CrashReport]:
        return self.crash_history[-1] if self.crash_history else None

    def get_crash_history(self) -> List[CrashReport]:
        return list(self.crash_history)

    def clear(self) -> None:
        self.crash_history.clear()
        self._breadcrumbs.clear()
