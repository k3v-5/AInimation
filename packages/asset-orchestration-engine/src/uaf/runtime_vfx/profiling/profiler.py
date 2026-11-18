"""
UAF-81.84.11: VFX Telemetry and Performance Profiling.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Dict, List

from ..models.definition import VFXMetrics


@dataclass
class EmitterProfileStats:
    emitter_id: str
    active_particles: int = 0
    spawned_particles: int = 0
    cpu_time_ms: float = 0.0
    gpu_time_ms: float = 0.0
    draw_calls: int = 0


class VFXProfiler:
    """Tracks hierarchical CPU/GPU performance and memory usage per emitter and system."""

    def __init__(self):
        self.system_stats: Dict[str, EmitterProfileStats] = {}
        self.metrics = VFXMetrics()

    def record_emitter_frame(
        self,
        emitter_id: str,
        active_count: int,
        spawned_count: int,
        cpu_time_ms: float,
        gpu_time_ms: float = 0.0,
        draw_calls: int = 1,
    ) -> None:
        stats = self.system_stats.get(emitter_id)
        if not stats:
            stats = EmitterProfileStats(emitter_id=emitter_id)
            self.system_stats[emitter_id] = stats

        stats.active_particles = active_count
        stats.spawned_particles += spawned_count
        stats.cpu_time_ms = cpu_time_ms
        stats.gpu_time_ms = gpu_time_ms
        stats.draw_calls = draw_calls

        # Update global metrics
        self.metrics.active_particles = sum(s.active_particles for s in self.system_stats.values())
        self.metrics.cpu_time_ms = sum(s.cpu_time_ms for s in self.system_stats.values())
        self.metrics.draw_calls = sum(s.draw_calls for s in self.system_stats.values())

    def reset_frame(self) -> None:
        self.system_stats.clear()
        self.metrics = VFXMetrics()
