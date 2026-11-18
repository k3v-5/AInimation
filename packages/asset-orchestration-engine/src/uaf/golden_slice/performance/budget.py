"""Memory and frame budget definitions and compliance checks."""

from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass
class BudgetComplianceReport:
    is_compliant: bool
    violations: List[str]
    metrics: Dict[str, float]


class PerformanceBudget:
    """Enforces RAM, VRAM, and frame time limits defined in the manifest."""

    def __init__(
        self,
        target_fps: int = 60,
        ram_budget_mb: float = 4096.0,
        vram_budget_mb: float = 6144.0,
        max_frame_time_ms: float = 16.67,
    ) -> None:
        self.target_fps = target_fps
        self.ram_budget_mb = ram_budget_mb
        self.vram_budget_mb = vram_budget_mb
        self.max_frame_time_ms = max_frame_time_ms

    def evaluate_compliance(
        self,
        used_ram_mb: float,
        used_vram_mb: float,
        p99_frame_time_ms: float,
    ) -> BudgetComplianceReport:
        violations: List[str] = []

        if used_ram_mb > self.ram_budget_mb:
            violations.append(f"RAM usage ({used_ram_mb:.1f}MB) exceeds budget ({self.ram_budget_mb:.1f}MB)")

        if used_vram_mb > self.vram_budget_mb:
            violations.append(f"VRAM usage ({used_vram_mb:.1f}MB) exceeds budget ({self.vram_budget_mb:.1f}MB)")

        if p99_frame_time_ms > (self.max_frame_time_ms * 1.15):  # 15% tolerance for p99
            violations.append(f"P99 frame time ({p99_frame_time_ms:.2f}ms) exceeds target ({self.max_frame_time_ms:.2f}ms)")

        return BudgetComplianceReport(
            is_compliant=len(violations) == 0,
            violations=violations,
            metrics={
                "used_ram_mb": used_ram_mb,
                "used_vram_mb": used_vram_mb,
                "p99_frame_time_ms": p99_frame_time_ms,
            },
        )
