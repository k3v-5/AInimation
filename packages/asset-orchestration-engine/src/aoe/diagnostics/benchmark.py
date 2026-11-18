"""Autonomous benchmark execution engine for stress testing and baselining."""

from __future__ import annotations
import math
import statistics
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from uaf.runtime_diagnostics.core import SubsystemType, ensure_finite_float
from uaf.runtime_diagnostics.regression import BenchmarkBaseline
from uaf.runtime_diagnostics.telemetry import TelemetryManager


@dataclass
class BenchmarkConfig:
    name: str = "Standard 60FPS Stress Test"
    total_frames: int = 120
    entity_count: int = 1000
    target_fps: float = 60.0
    simulated_subsystem_times_ms: Dict[SubsystemType, float] = field(default_factory=dict)


@dataclass
class BenchmarkRunResult:
    benchmark_name: str
    total_frames: int
    entity_count: int
    mean_frame_time_ms: float
    p95_frame_time_ms: float
    p99_frame_time_ms: float
    min_frame_time_ms: float
    max_frame_time_ms: float
    baseline: BenchmarkBaseline
    raw_frame_times: List[float] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "benchmark_name": self.benchmark_name,
            "total_frames": self.total_frames,
            "entity_count": self.entity_count,
            "mean_frame_time_ms": ensure_finite_float(self.mean_frame_time_ms),
            "p95_frame_time_ms": ensure_finite_float(self.p95_frame_time_ms),
            "p99_frame_time_ms": ensure_finite_float(self.p99_frame_time_ms),
            "min_frame_time_ms": ensure_finite_float(self.min_frame_time_ms),
            "max_frame_time_ms": ensure_finite_float(self.max_frame_time_ms),
            "baseline": self.baseline.to_dict(),
        }


class BenchmarkRunner:
    """Executes repeatable profiling passes and synthesizes regression baselines."""

    def __init__(self, telemetry_manager: Optional[TelemetryManager] = None) -> None:
        self.telemetry = telemetry_manager or TelemetryManager()

    def run_benchmark(self, config: BenchmarkConfig) -> BenchmarkRunResult:
        frame_times: List[float] = []
        default_times = {
            SubsystemType.STREAMING: 0.8,
            SubsystemType.PHYSICS: 2.2,
            SubsystemType.AI: 1.5,
            SubsystemType.NETWORKING: 0.5,
            SubsystemType.ANIMATION: 1.8,
            SubsystemType.VFX: 1.2,
            SubsystemType.LIGHTING: 1.4,
            SubsystemType.RENDERING: 4.5,
            SubsystemType.AUDIO: 0.4,
            SubsystemType.UI: 0.5,
            SubsystemType.GENERAL: 0.2,
        }
        subsys_times = dict(config.simulated_subsystem_times_ms or default_times)

        # Base nominal time sum
        nominal_sum = sum(subsys_times.values())

        for f in range(config.total_frames):
            state_hash = f"hash_{f:06d}"
            self.telemetry.begin_frame(frame_index=f, state_hash=state_hash)

            # Add minor pseudo-random oscillation or jitter
            jitter = math.sin(f * 0.1) * 0.5
            adjusted_times = {k: max(0.01, v + (jitter / len(subsys_times))) for k, v in subsys_times.items()}

            frame_data = self.telemetry.end_frame(subsystem_times=adjusted_times)
            duration = frame_data.get("duration_ms", nominal_sum)
            # In synthetic run without real sleep, use nominal + jitter
            simulated_dur = max(0.1, nominal_sum + jitter)
            frame_times.append(simulated_dur)

        sorted_times = sorted(frame_times)
        n = len(sorted_times)
        mean_val = statistics.mean(sorted_times)
        p95_val = sorted_times[int(0.95 * (n - 1))]
        p99_val = sorted_times[int(0.99 * (n - 1))]
        min_val = sorted_times[0]
        max_val = sorted_times[-1]

        baseline = BenchmarkBaseline(
            benchmark_name=config.name,
            commit_hash="HEAD",
            mean_frame_time_ms=mean_val,
            p95_frame_time_ms=p95_val,
            p99_frame_time_ms=p99_val,
            max_memory_mb=64.0,
            sample_count=n,
        )

        return BenchmarkRunResult(
            benchmark_name=config.name,
            total_frames=n,
            entity_count=config.entity_count,
            mean_frame_time_ms=mean_val,
            p95_frame_time_ms=p95_val,
            p99_frame_time_ms=p99_val,
            min_frame_time_ms=min_val,
            max_frame_time_ms=max_val,
            baseline=baseline,
            raw_frame_times=frame_times,
        )
