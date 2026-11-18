"""
Performance Regression Engine & Statistical Baselines for UAF-81.86.
"""

from __future__ import annotations
import math
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from .metrics import TelemetryHistogram


@dataclass
class BenchmarkBaseline:
    benchmark_name: str
    metric_name: str = "frame_time"
    mean: float = 0.0
    median: float = 0.0
    p95: float = 0.0
    p99: float = 0.0
    max_val: float = 0.0
    sample_count: int = 0
    commit_hash: str = "HEAD"
    mean_frame_time_ms: float = 0.0
    p95_frame_time_ms: float = 0.0
    p99_frame_time_ms: float = 0.0
    max_memory_mb: float = 64.0

    def __post_init__(self) -> None:
        if self.mean_frame_time_ms and not self.mean:
            self.mean = self.mean_frame_time_ms
        elif self.mean and not self.mean_frame_time_ms:
            self.mean_frame_time_ms = self.mean

        if self.p95_frame_time_ms and not self.p95:
            self.p95 = self.p95_frame_time_ms
        elif self.p95 and not self.p95_frame_time_ms:
            self.p95_frame_time_ms = self.p95

        if self.p99_frame_time_ms and not self.p99:
            self.p99 = self.p99_frame_time_ms
        elif self.p99 and not self.p99_frame_time_ms:
            self.p99_frame_time_ms = self.p99

    def to_dict(self) -> Dict[str, Any]:
        return {
            "benchmark_name": self.benchmark_name,
            "metric_name": self.metric_name,
            "commit_hash": self.commit_hash,
            "mean": self.mean,
            "median": self.median,
            "p95": self.p95,
            "p99": self.p99,
            "max_val": self.max_val,
            "sample_count": self.sample_count,
            "max_memory_mb": self.max_memory_mb,
        }


@dataclass
class RegressionReport:
    benchmark_name: str
    metric_name: str
    baseline_p95: float
    candidate_p95: float
    delta_percent: float
    result: str  # PASS, WARNING, FAIL, CRITICAL
    message: str

    @property
    def is_passing(self) -> bool:
        return self.result in ("PASS", "WARNING")


class RegressionEngine:
    """
    Compares candidate benchmark runs against historical baselines using statistical percentiles (P95/P99).
    Enforces regression policy gates:
    - P95 delta <= +2.0%: PASS
    - P95 delta <= +5.0%: WARNING
    - P95 delta <= +10.0%: FAIL
    - P95 delta > +10.0%: CRITICAL
    """

    def __init__(self) -> None:
        self.baselines: Dict[Tuple[str, str], BenchmarkBaseline] = {}

    def register_baseline(self, baseline: BenchmarkBaseline) -> None:
        key = (baseline.benchmark_name, baseline.metric_name)
        self.baselines[key] = baseline

    def create_baseline_from_samples(
        self,
        benchmark_name: str,
        metric_name: str,
        samples: List[float]
    ) -> BenchmarkBaseline:
        hist = TelemetryHistogram(
            metric_id=None,  # type: ignore
            subsystem=None,   # type: ignore
            metric_type=None, # type: ignore
            unit=None,        # type: ignore
            max_samples=len(samples) + 10,
        )
        for s in samples:
            hist.record(s)

        baseline = BenchmarkBaseline(
            benchmark_name=benchmark_name,
            metric_name=metric_name,
            mean=round(hist.mean, 4),
            median=round(hist.percentile(50.0), 4),
            p95=round(hist.percentile(95.0), 4),
            p99=round(hist.percentile(99.0), 4),
            max_val=round(hist.max_val, 4),
            sample_count=hist.count,
        )
        self.register_baseline(baseline)
        return baseline

    def evaluate_candidate(
        self,
        benchmark_name: str,
        metric_name: str,
        candidate_samples: List[float]
    ) -> RegressionReport:
        key = (benchmark_name, metric_name)
        baseline = self.baselines.get(key)

        if not baseline:
            # First run, establish baseline
            baseline = self.create_baseline_from_samples(benchmark_name, metric_name, candidate_samples)
            return RegressionReport(
                benchmark_name=benchmark_name,
                metric_name=metric_name,
                baseline_p95=baseline.p95,
                candidate_p95=baseline.p95,
                delta_percent=0.0,
                result="PASS",
                message="No baseline existed. Created new baseline from candidate samples.",
            )

        hist = TelemetryHistogram(
            metric_id=None,  # type: ignore
            subsystem=None,   # type: ignore
            metric_type=None, # type: ignore
            unit=None,        # type: ignore
            max_samples=len(candidate_samples) + 10,
        )
        for s in candidate_samples:
            hist.record(s)

        cand_p95 = hist.percentile(95.0)
        base_p95 = max(1e-4, baseline.p95)
        delta_pct = ((cand_p95 - base_p95) / base_p95) * 100.0

        if delta_pct <= 2.0:
            res = "PASS"
            msg = f"Candidate within expected variance ({delta_pct:+.2f}% P95)"
        elif delta_pct <= 5.0:
            res = "WARNING"
            msg = f"Minor performance regression ({delta_pct:+.2f}% P95)"
        elif delta_pct <= 10.0:
            res = "FAIL"
            msg = f"Regression exceeds 5% threshold ({delta_pct:+.2f}% P95)"
        else:
            res = "CRITICAL"
            msg = f"Severe regression exceeds 10% threshold ({delta_pct:+.2f}% P95)"

        return RegressionReport(
            benchmark_name=benchmark_name,
            metric_name=metric_name,
            baseline_p95=round(base_p95, 4),
            candidate_p95=round(cand_p95, 4),
            delta_percent=round(delta_pct, 2),
            result=res,
            message=msg,
        )
