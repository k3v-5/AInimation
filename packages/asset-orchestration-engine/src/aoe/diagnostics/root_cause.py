"""Automated root cause identification for performance, memory, crashes, and desyncs."""

from __future__ import annotations
import uuid
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from uaf.runtime_diagnostics.core import SubsystemType, ensure_finite_float
from uaf.runtime_diagnostics.determinism import DivergencePoint
from aoe.diagnostics.failure_analysis import FailureIncident, FailureAnalysisReport


@dataclass
class RootCauseHypothesis:
    hypothesis_id: str
    offending_subsystem: SubsystemType
    primary_cause: str
    confidence: float
    supporting_evidence: List[str] = field(default_factory=list)
    recommended_action_category: str = "investigate"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "hypothesis_id": self.hypothesis_id,
            "offending_subsystem": self.offending_subsystem.value,
            "primary_cause": self.primary_cause,
            "confidence": ensure_finite_float(self.confidence),
            "supporting_evidence": self.supporting_evidence,
            "recommended_action_category": self.recommended_action_category,
        }


class RootCauseAnalyzer:
    """Infers root causes from diagnostic signals, stack traces, and anomalies."""

    def analyze_incident(self, incident: FailureIncident) -> RootCauseHypothesis:
        subsys = incident.subsystem
        cat = incident.category
        evidence: List[str] = []
        cause = "Unknown anomaly"
        confidence = 0.5
        rec_action = "inspect_logs"

        if cat == "crash":
            stack = incident.stack_trace or ""
            msg = incident.summary.lower()
            if "memory" in msg or "out_of_memory" in msg:
                cause = "Memory exhaustion or unbounded asset allocation"
                confidence = 0.9
                rec_action = "reduce_batch_size_or_increase_pool"
            elif "deadlock" in msg:
                cause = "Lock acquisition inversion or thread cycle"
                confidence = 0.95
                rec_action = "break_lock_cycle_or_use_try_lock"
            elif "assertion" in msg:
                cause = "Simulation invariant failure or corrupted state"
                confidence = 0.85
                rec_action = "validate_preconditions"
            else:
                cause = f"Unhandled exception in {subsys.value}"
                confidence = 0.75
                rec_action = "patch_exception_handling"
            evidence.append(f"Stack trace length: {len(stack)} characters")

        elif cat == "hitch":
            details = incident.details
            subsystem_times = details.get("context_frame_data", {}).get("subsystem_times", {})
            if subsystem_times:
                # Find maximum consumer
                max_sub = max(subsystem_times.items(), key=lambda x: x[1])
                cause = f"Subsystem '{max_sub[0]}' exceeded time slice ({max_sub[1]:.2f}ms)"
                confidence = 0.88
                rec_action = f"throttle_or_degrade_{max_sub[0]}"
                evidence.append(f"Highest subsystem cost: {max_sub[0]} at {max_sub[1]:.2f}ms")
            else:
                cause = f"Frame budget overrun in {subsys.value}"
                confidence = 0.7
                rec_action = "profile_subsystem_internals"

        elif cat == "memory_leak":
            cause = f"Unreleased allocations in {subsys.value} continuously growing"
            confidence = 0.9
            rec_action = "audit_subsystem_resource_disposal"
            evidence.append("Linear upward allocation slope observed across snapshots")

        elif cat == "deadlock":
            cause = "Mutual exclusion contention across worker threads"
            confidence = 0.95
            rec_action = "impose_strict_lock_ordering"

        return RootCauseHypothesis(
            hypothesis_id=f"rch_{uuid.uuid4().hex[:10]}",
            offending_subsystem=subsys,
            primary_cause=cause,
            confidence=confidence,
            supporting_evidence=evidence,
            recommended_action_category=rec_action,
        )

    def analyze_divergence(self, divergence: DivergencePoint) -> RootCauseHypothesis:
        evidence = [
            f"First divergence occurred at frame {divergence.divergent_frame}",
            f"Run A state hash: {divergence.run_a_hash}",
            f"Run B state hash: {divergence.run_b_hash}",
            f"Divergent properties: {divergence.divergent_properties}",
        ]

        cause = f"Non-deterministic property mutation in entity '{divergence.entity_id or 'global'}'"
        if divergence.divergent_properties:
            props_str = ", ".join(divergence.divergent_properties[:3])
            cause += f" (properties: {props_str})"

        return RootCauseHypothesis(
            hypothesis_id=f"rch_det_{uuid.uuid4().hex[:10]}",
            offending_subsystem=divergence.subsystem,
            primary_cause=cause,
            confidence=0.98,
            supporting_evidence=evidence,
            recommended_action_category="enforce_fixed_point_or_deterministic_ordering",
        )

    def analyze_report(self, report: FailureAnalysisReport) -> List[RootCauseHypothesis]:
        return [self.analyze_incident(inc) for inc in report.incidents]
