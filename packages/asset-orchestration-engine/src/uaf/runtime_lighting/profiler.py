"""
Lighting Telemetry Profiler for UAF-81.85.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass
class LightingProfileFrame:
    """Detailed performance snapshot for a single rendered/simulated frame."""
    frame_number: int
    light_culling_ms: float
    shadow_generation_ms: float
    ambient_gi_ms: float
    volumetric_ms: float
    postprocess_ms: float
    color_management_ms: float
    total_cpu_ms: float
    total_gpu_ms: float
    active_light_count: int
    active_shadow_count: int
    probe_count: int
    memory_bytes: int
    degradation_step: int

    def summary(self) -> str:
        return (
            f"FRAME {self.frame_number}\n"
            f" ├── Light Culling       {self.light_culling_ms:.2f} ms\n"
            f" ├── Shadow Generation   {self.shadow_generation_ms:.2f} ms\n"
            f" ├── GI                  {self.ambient_gi_ms:.2f} ms\n"
            f" ├── Volumetrics         {self.volumetric_ms:.2f} ms\n"
            f" ├── Post Process        {self.postprocess_ms:.2f} ms\n"
            f" └── Color Management    {self.color_management_ms:.2f} ms\n"
            f" TOTAL: CPU={self.total_cpu_ms:.2f}ms | GPU={self.total_gpu_ms:.2f}ms | Lights={self.active_light_count}"
        )


class LightingProfiler:
    """Collects and aggregates frame performance telemetry."""

    def __init__(self, history_capacity: int = 120) -> None:
        self.capacity = max(10, history_capacity)
        self.history: List[LightingProfileFrame] = []

    def record_frame(self, frame: LightingProfileFrame) -> None:
        self.history.append(frame)
        if len(self.history) > self.capacity:
            self.history.pop(0)

    @property
    def latest_frame(self) -> Optional[LightingProfileFrame]:
        return self.history[-1] if self.history else None

    def get_average_cpu_ms(self) -> float:
        if not self.history:
            return 0.0
        return sum(f.total_cpu_ms for f in self.history) / float(len(self.history))
