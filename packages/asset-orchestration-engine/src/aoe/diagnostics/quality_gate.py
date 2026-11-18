"""Autonomous CI/CD and release Quality Gate evaluation."""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from uaf.runtime_diagnostics.core import QualityGateResult, ensure_finite_float


@dataclass
class QualityGateThresholds:
    max_p95_frame_time_ms: float = 16.67
    max_p99_frame_time_ms: float = 25.00
    max_overrun_pct: float = 3.0
    max_crashes: int = 0
    max_memory_leaks: int = 0
    require_zero_determinism_desyncs: bool = True


@dataclass
class QualityGateVerdict:
    result: QualityGateResult
    score: float
    violations: List[str] = field(default_factory=list)
    metrics_evaluated: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "result": self.result.value,
            "score": ensure_finite_float(self.score),
            "violations": list(self.violations),
            "metrics_evaluated": dict(self.metrics_evaluated),
        }


class QualityGateEvaluator:
    """Evaluates benchmark and session telemetry against release criteria."""

    def __init__(self, thresholds: Optional[QualityGateThresholds] = None) -> None:
        self.thresholds = thresholds or QualityGateThresholds()

    def evaluate(
        self,
        performance_report: Dict[str, Any],
        leak_count: int = 0,
        crash_count: int = 0,
        determinism_desync_count: int = 0,
    ) -> QualityGateVerdict:
        violations: List[str] = []
        score = 100.0

        p95 = performance_report.get("p95_frame_time_ms", 0.0)
        p99 = performance_report.get("p99_frame_time_ms", 0.0)
        overrun_pct = performance_report.get("overrun_percentage", 0.0)

        # 1. Performance checks
        if p95 > self.thresholds.max_p95_frame_time_ms:
            violations.append(f"P95 frame time {p95:.2f}ms exceeds target {self.thresholds.max_p95_frame_time_ms:.2f}ms")
            score -= 25.0

        if p99 > self.thresholds.max_p99_frame_time_ms:
            violations.append(f"P99 frame time {p99:.2f}ms exceeds threshold {self.thresholds.max_p99_frame_time_ms:.2f}ms")
            score -= 15.0

        if overrun_pct > self.thresholds.max_overrun_pct:
            violations.append(f"Budget overrun percentage {overrun_pct:.2f}% exceeds {self.thresholds.max_overrun_pct:.2f}%")
            score -= 10.0

        # 2. Stability checks
        if crash_count > self.thresholds.max_crashes:
            violations.append(f"Recorded {crash_count} crashes (max allowed: {self.thresholds.max_crashes})")
            score -= 50.0

        # 3. Memory checks
        if leak_count > self.thresholds.max_memory_leaks:
            violations.append(f"Detected {leak_count} memory leaks (max allowed: {self.thresholds.max_memory_leaks})")
            score -= 20.0

        # 4. Determinism checks
        if self.thresholds.require_zero_determinism_desyncs and determinism_desync_count > 0:
            violations.append(f"Found {determinism_desync_count} determinism desync divergences")
            score -= 30.0

        score = max(0.0, score)

        # Determine result
        if crash_count > 0 or determinism_desync_count > 0:
            result = QualityGateResult.FAIL
        elif len(violations) == 0 and score >= 90.0:
            result = QualityGateResult.CERTIFY
        elif len(violations) == 0:
            result = QualityGateResult.PASS
        elif score >= 60.0:
            result = QualityGateResult.DEGRADE
        else:
            result = QualityGateResult.FAIL

        return QualityGateVerdict(
            result=result,
            score=score,
            violations=violations,
            metrics_evaluated={
                "p95_ms": p95,
                "p99_ms": p99,
                "overrun_pct": overrun_pct,
                "crashes": crash_count,
                "leaks": leak_count,
                "desyncs": determinism_desync_count,
            },
        )
