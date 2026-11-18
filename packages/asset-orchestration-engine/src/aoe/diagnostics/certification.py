"""Autonomous Golden Certification Engine for performance, memory, and determinism."""

from __future__ import annotations
import hashlib
import json
import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from uaf.runtime_diagnostics.core import QualityGateResult
from aoe.diagnostics.quality_gate import QualityGateEvaluator, QualityGateVerdict
from aoe.diagnostics.benchmark import BenchmarkRunResult


@dataclass
class GoldenCertificationCertificate:
    certificate_id: str
    timestamp_ns: int
    is_certified: bool
    sha256_signature: str
    verdict: QualityGateVerdict
    benchmark_summary: Dict[str, Any]
    determinism_verified: bool
    audit_log: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "certificate_id": self.certificate_id,
            "timestamp_ns": self.timestamp_ns,
            "is_certified": self.is_certified,
            "sha256_signature": self.sha256_signature,
            "verdict": self.verdict.to_dict(),
            "benchmark_summary": self.benchmark_summary,
            "determinism_verified": self.determinism_verified,
            "audit_log": list(self.audit_log),
        }

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent, sort_keys=True)


class GoldenCertificationEngine:
    """Certifies autonomous vertical slices and runtime pipelines against golden performance baselines."""

    def __init__(self, evaluator: Optional[QualityGateEvaluator] = None) -> None:
        self.evaluator = evaluator or QualityGateEvaluator()

    def certify(
        self,
        benchmark_result: BenchmarkRunResult,
        memory_leaks: int = 0,
        crashes: int = 0,
        determinism_desyncs: int = 0,
    ) -> GoldenCertificationCertificate:
        cert_id = f"cert_{uuid.uuid4().hex[:12]}"
        now_ns = time.perf_counter_ns()
        audit_log: List[str] = []

        audit_log.append(f"Starting certification for benchmark '{benchmark_result.benchmark_name}'")
        audit_log.append(f"Frames evaluated: {benchmark_result.total_frames}, Entity count: {benchmark_result.entity_count}")

        perf_summary = {
            "mean_frame_time_ms": benchmark_result.mean_frame_time_ms,
            "p95_frame_time_ms": benchmark_result.p95_frame_time_ms,
            "p99_frame_time_ms": benchmark_result.p99_frame_time_ms,
            "min_frame_time_ms": benchmark_result.min_frame_time_ms,
            "max_frame_time_ms": benchmark_result.max_frame_time_ms,
            "overrun_percentage": 0.0,
        }

        verdict = self.evaluator.evaluate(
            performance_report=perf_summary,
            leak_count=memory_leaks,
            crash_count=crashes,
            determinism_desync_count=determinism_desyncs,
        )

        is_certified = verdict.result in (QualityGateResult.CERTIFY, QualityGateResult.PASS)
        determinism_verified = determinism_desyncs == 0

        if is_certified:
            audit_log.append("Quality gate evaluation PASSED successfully.")
        else:
            audit_log.append(f"Quality gate evaluation FAILED with {len(verdict.violations)} violations.")

        # Compute tamper-evident SHA-256 signature
        signature_payload = {
            "cert_id": cert_id,
            "benchmark_name": benchmark_result.benchmark_name,
            "p95": benchmark_result.p95_frame_time_ms,
            "verdict": verdict.result.value,
            "is_certified": is_certified,
        }
        sig_str = json.dumps(signature_payload, sort_keys=True)
        sha256_sig = hashlib.sha256(sig_str.encode("utf-8")).hexdigest()

        return GoldenCertificationCertificate(
            certificate_id=cert_id,
            timestamp_ns=now_ns,
            is_certified=is_certified,
            sha256_signature=sha256_sig,
            verdict=verdict,
            benchmark_summary=benchmark_result.to_dict(),
            determinism_verified=determinism_verified,
            audit_log=audit_log,
        )
