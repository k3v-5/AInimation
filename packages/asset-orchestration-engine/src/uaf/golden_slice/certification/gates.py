"""Certification gates evaluating Bronze, Silver, Gold, and Platinum criteria."""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from uaf.golden_slice.manifest.models import CertificationLevel


@dataclass
class GateEvaluation:
    gate_name: str
    passed: bool
    message: str
    is_blocking: bool = True
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class GatekeeperResult:
    target_level: CertificationLevel
    achieved_level: Optional[CertificationLevel]
    is_certified: bool
    evaluations: List[GateEvaluation] = field(default_factory=list)
    critical_failures: int = 0
    blocking_warnings: int = 0
    replay_mismatches: int = 0

    @property
    def summary_status(self) -> str:
        if self.is_certified and self.achieved_level:
            return f"CERTIFIED {self.achieved_level.value}"
        elif self.blocking_warnings > 0:
            return "BLOCKED"
        return "FAILED"


class CertificationGatekeeper:
    """Enforces strict multi-tier certification gates with zero tolerance for silent errors."""

    def evaluate(
        self,
        target_level: CertificationLevel,
        functional_tests_passed: bool,
        performance_compliant: bool,
        determinism_verified: bool,
        recovery_verified: bool,
        reproducibility_verified: bool,
        critical_failures: int = 0,
        blocking_warnings: int = 0,
        replay_mismatches: int = 0,
        missing_assets: int = 0,
    ) -> GatekeeperResult:
        evals: List[GateEvaluation] = []

        # Gate 1: Functional Completeness (BRONZE baseline)
        g1_pass = functional_tests_passed and (critical_failures == 0) and (missing_assets == 0)
        evals.append(GateEvaluation(
            "GATE_01_FUNCTIONAL",
            g1_pass,
            "All functional QA test suites passed" if g1_pass else "Functional failures detected",
        ))

        # Gate 2: Performance Budgeting (SILVER requirement)
        g2_pass = performance_compliant
        evals.append(GateEvaluation(
            "GATE_02_PERFORMANCE",
            g2_pass,
            "Performance and memory within budget" if g2_pass else "Performance budget violated",
        ))

        # Gate 3: Determinism & Replay Equivalence (GOLD requirement)
        g3_pass = determinism_verified and (replay_mismatches == 0)
        evals.append(GateEvaluation(
            "GATE_03_DETERMINISM",
            g3_pass,
            "Deterministic replay and hash alignment verified" if g3_pass else "Determinism mismatch detected",
        ))

        # Gate 4: Recovery & Toolchain Reproducibility (PLATINUM requirement)
        g4_pass = recovery_verified and reproducibility_verified
        evals.append(GateEvaluation(
            "GATE_04_RECOVERY_REPRODUCIBILITY",
            g4_pass,
            "Fault recovery and binary reproducibility verified" if g4_pass else "Recovery or reproducibility failed",
        ))

        # Determine achieved level
        achieved: Optional[CertificationLevel] = None
        if g1_pass:
            achieved = CertificationLevel.BRONZE
            if g2_pass:
                achieved = CertificationLevel.SILVER
                if g3_pass:
                    achieved = CertificationLevel.GOLD
                    if g4_pass:
                        achieved = CertificationLevel.PLATINUM

        # Check if requested target level is reached and no blocking warnings exist
        level_order = [CertificationLevel.BRONZE, CertificationLevel.SILVER, CertificationLevel.GOLD, CertificationLevel.PLATINUM]
        target_idx = level_order.index(target_level)
        achieved_idx = level_order.index(achieved) if achieved else -1

        is_certified = (achieved_idx >= target_idx) and (blocking_warnings == 0) and (critical_failures == 0)

        return GatekeeperResult(
            target_level=target_level,
            achieved_level=achieved,
            is_certified=is_certified,
            evaluations=evals,
            critical_failures=critical_failures,
            blocking_warnings=blocking_warnings,
            replay_mismatches=replay_mismatches,
        )
