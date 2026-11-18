"""Comprehensive diagnostic and telemetry report generation."""

from __future__ import annotations
import json
import statistics
from typing import Any, Dict, List, Optional
from uaf.runtime_diagnostics.core import ensure_finite_float
from uaf.runtime_diagnostics.telemetry import TelemetryManager


class ReportGenerator:
    """Generates comprehensive JSON and text diagnostic reports from TelemetryManager state."""

    def __init__(self, telemetry: TelemetryManager) -> None:
        self.telemetry = telemetry

    def generate_performance_report(self) -> Dict[str, Any]:
        frames = self.telemetry.frame_buffer.to_list()
        if not frames:
            return {"status": "no_data", "frame_count": 0}

        frame_times = [f["duration_ms"] for f in frames if "duration_ms" in f]
        if not frame_times:
            return {"status": "no_data", "frame_count": 0}

        sorted_times = sorted(frame_times)
        n = len(sorted_times)

        def pct(p: float) -> float:
            idx = int(p * (n - 1))
            return ensure_finite_float(sorted_times[idx])

        avg_time = ensure_finite_float(statistics.mean(frame_times))
        avg_fps = ensure_finite_float(1000.0 / avg_time if avg_time > 0 else 0.0)

        # Budget overruns
        overrun_count = sum(1 for f in frames if f.get("budget", {}).get("is_overrun", False))
        overrun_pct = ensure_finite_float((overrun_count / n) * 100.0 if n > 0 else 0.0)

        return {
            "status": "ok",
            "frame_count": n,
            "target_fps": self.telemetry.target_fps,
            "target_frame_time_ms": ensure_finite_float(1000.0 / self.telemetry.target_fps),
            "avg_frame_time_ms": avg_time,
            "avg_fps": avg_fps,
            "min_frame_time_ms": ensure_finite_float(sorted_times[0]),
            "max_frame_time_ms": ensure_finite_float(sorted_times[-1]),
            "p50_frame_time_ms": pct(0.50),
            "p90_frame_time_ms": pct(0.90),
            "p95_frame_time_ms": pct(0.95),
            "p99_frame_time_ms": pct(0.99),
            "overrun_frames": overrun_count,
            "overrun_percentage": overrun_pct,
        }

    def generate_full_report(self) -> Dict[str, Any]:
        perf = self.generate_performance_report()
        mem = self.telemetry.memory.get_summary()
        leaks = [l.to_dict() for l in self.telemetry.memory.detect_leaks()]
        anomalies = [a.to_dict() for a in self.telemetry.anomalies.get_recent_anomalies()]
        crashes = [c.to_dict() for c in self.telemetry.crash_handler.get_crash_history()]
        recoveries = [r.to_dict() for r in self.telemetry.recovery.get_history()]
        deadlocks = [
            {"thread_ids": d.thread_ids, "lock_ids": d.lock_ids, "desc": d.description}
            for d in self.telemetry.deadlocks.detect_deadlocks()
        ]
        stalls = self.telemetry.watchdog.check_stalls()

        return {
            "performance": perf,
            "memory": {
                "summary": mem,
                "potential_leaks": leaks,
            },
            "anomalies": {
                "total": len(anomalies),
                "items": anomalies[-20:],
            },
            "crashes": {
                "total": len(crashes),
                "recent": crashes[-10:],
            },
            "recoveries": {
                "total": len(recoveries),
                "safe_mode": self.telemetry.recovery.is_in_safe_mode,
                "recent": recoveries[-10:],
            },
            "concurrency": {
                "deadlocks": deadlocks,
                "stalled_threads": stalls,
            },
        }

    def export_json(self, indent: int = 2) -> str:
        return json.dumps(self.generate_full_report(), indent=indent, sort_keys=True)
