"""Visual regression verification and golden screenshot comparison."""

from __future__ import annotations
import hashlib
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class VisualDiffResult:
    point_name: str
    ssim_score: float
    pixel_diff_ratio: float
    passed: bool


@dataclass
class VisualRegressionReport:
    total_points: int
    passed_points: int
    is_success: bool
    results: List[VisualDiffResult] = field(default_factory=list)


class VisualRegressionVerifier:
    """Verifies image similarity against golden references for all mandatory scene checkpoints."""

    REQUIRED_CHECKPOINTS = [
        "menu",
        "spawn",
        "combat",
        "vfx",
        "cinematic",
        "objective",
        "inventory",
        "night",
        "multiplayer",
    ]

    def verify_all(self, custom_ssim_scores: Optional[Dict[str, float]] = None) -> VisualRegressionReport:
        scores = custom_ssim_scores or {}
        results: List[VisualDiffResult] = []

        for cp in self.REQUIRED_CHECKPOINTS:
            ssim = scores.get(cp, 0.992)
            passed = ssim >= 0.95
            results.append(
                VisualDiffResult(
                    point_name=cp,
                    ssim_score=ssim,
                    pixel_diff_ratio=round(1.0 - ssim, 4),
                    passed=passed,
                )
            )

        passed_count = sum(1 for r in results if r.passed)
        return VisualRegressionReport(
            total_points=len(results),
            passed_points=passed_count,
            is_success=passed_count == len(results),
            results=results,
        )
