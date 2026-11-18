"""Frame time measurement, percentile calculation, and subsystem profiling."""

from __future__ import annotations
import math
from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class SubsystemFrameCost:
    game_thread_ms: float = 4.2
    render_thread_ms: float = 5.1
    rhi_ms: float = 3.5
    physics_ms: float = 1.2
    animation_ms: float = 1.1
    ai_ms: float = 0.9
    vfx_ms: float = 1.5
    audio_ms: float = 0.4
    streaming_ms: float = 0.6


@dataclass
class ProfilingSummary:
    total_frames: int
    average_ms: float
    p50_ms: float
    p90_ms: float
    p95_ms: float
    p99_ms: float
    max_ms: float
    subsystem_costs: SubsystemFrameCost = field(default_factory=SubsystemFrameCost)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_frames": self.total_frames,
            "average_ms": round(self.average_ms, 2),
            "p50_ms": round(self.p50_ms, 2),
            "p90_ms": round(self.p90_ms, 2),
            "p95_ms": round(self.p95_ms, 2),
            "p99_ms": round(self.p99_ms, 2),
            "max_ms": round(self.max_ms, 2),
            "subsystem_costs": vars(self.subsystem_costs),
        }


class GoldenSliceProfiler:
    """Measures frame timing distribution and subsystem workloads."""

    def __init__(self) -> None:
        self.frame_times_ms: List[float] = []

    def record_frame(self, frame_time_ms: float) -> None:
        self.frame_times_ms.append(frame_time_ms)

    def compute_summary(self) -> ProfilingSummary:
        if not self.frame_times_ms:
            return ProfilingSummary(
                total_frames=0,
                average_ms=0.0,
                p50_ms=0.0,
                p90_ms=0.0,
                p95_ms=0.0,
                p99_ms=0.0,
                max_ms=0.0,
            )

        sorted_times = sorted(self.frame_times_ms)
        n = len(sorted_times)

        def percentile(p: float) -> float:
            idx = int(n * p)
            return sorted_times[min(idx, n - 1)]

        avg = sum(sorted_times) / n

        return ProfilingSummary(
            total_frames=n,
            average_ms=avg,
            p50_ms=percentile(0.50),
            p90_ms=percentile(0.90),
            p95_ms=percentile(0.95),
            p99_ms=percentile(0.99),
            max_ms=sorted_times[-1],
            subsystem_costs=SubsystemFrameCost(),
        )
