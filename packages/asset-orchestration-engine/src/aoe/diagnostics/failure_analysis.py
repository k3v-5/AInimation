"""Autonomous AOE failure analysis, log parsing, and diagnostic synthesis."""

from __future__ import annotations
import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from uaf.runtime_diagnostics.core import CrashType, SeverityLevel, SubsystemType
from uaf.runtime_diagnostics.crash import CrashReport
from uaf.runtime_diagnostics.anomalies import PerformanceAnomaly


@dataclass
class FailureIncident:
    incident_id: str
    timestamp_ns: int
    category: str  # "crash", "hitch", "memory_leak", "determinism_desync", "deadlock", "budget_overrun"
    severity: SeverityLevel
    subsystem: SubsystemType
    summary: str
    details: Dict[str, Any] = field(default_factory=dict)
    stack_trace: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "incident_id": self.incident_id,
            "timestamp_ns": self.timestamp_ns,
            "category": self.category,
            "severity": self.severity.value,
            "subsystem": self.subsystem.value,
            "summary": self.summary,
            "details": self.details,
            "stack_trace": self.stack_trace,
        }


@dataclass
class FailureAnalysisReport:
    report_id: str
    timestamp_ns: int
    incident_count: int
    incidents: List[FailureIncident] = field(default_factory=list)
    has_critical_failure: bool = False
    affected_subsystems: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "report_id": self.report_id,
            "timestamp_ns": self.timestamp_ns,
            "incident_count": self.incident_count,
            "has_critical_failure": self.has_critical_failure,
            "affected_subsystems": self.affected_subsystems,
            "incidents": [i.to_dict() for i in self.incidents],
        }


class FailureAnalyzer:
    """Automated incident cataloging and failure pattern synthesis."""

    def __init__(self) -> None:
        self.incidents: List[FailureIncident] = []

    def ingest_crash(self, crash: CrashReport) -> FailureIncident:
        incident = FailureIncident(
            incident_id=f"inc_{uuid.uuid4().hex[:10]}",
            timestamp_ns=crash.timestamp_ns,
            category="crash",
            severity=SeverityLevel.FATAL,
            subsystem=crash.subsystem,
            summary=f"Crash ({crash.crash_type.value}): {crash.error_message}",
            details={
                "crash_id": crash.crash_id,
                "frame_index": crash.frame_index,
                "state_hash": crash.state_hash,
                "active_spans": crash.active_spans,
                "system_info": crash.system_info,
            },
            stack_trace=crash.stack_trace,
        )
        self.incidents.append(incident)
        return incident

    def ingest_anomaly(self, anomaly: PerformanceAnomaly) -> FailureIncident:
        severity = (
            SeverityLevel.CRITICAL
            if anomaly.hitch_severity and anomaly.hitch_severity.value in ("severe", "critical")
            else SeverityLevel.WARNING
        )
        incident = FailureIncident(
            incident_id=f"inc_{uuid.uuid4().hex[:10]}",
            timestamp_ns=anomaly.timestamp_ns,
            category="hitch",
            severity=severity,
            subsystem=anomaly.subsystem,
            summary=f"Hitch detected: {anomaly.observed_value:.2f}ms exceeds threshold {anomaly.threshold_value:.2f}ms",
            details=anomaly.to_dict(),
        )
        self.incidents.append(incident)
        return incident

    def ingest_generic_incident(
        self,
        category: str,
        severity: SeverityLevel,
        subsystem: SubsystemType,
        summary: str,
        details: Optional[Dict[str, Any]] = None,
    ) -> FailureIncident:
        incident = FailureIncident(
            incident_id=f"inc_{uuid.uuid4().hex[:10]}",
            timestamp_ns=time.perf_counter_ns(),
            category=category,
            severity=severity,
            subsystem=subsystem,
            summary=summary,
            details=details or {},
        )
        self.incidents.append(incident)
        return incident

    def generate_report(self) -> FailureAnalysisReport:
        has_critical = any(
            i.severity in (SeverityLevel.FATAL, SeverityLevel.CRITICAL)
            for i in self.incidents
        )
        affected = sorted(list({i.subsystem.value for i in self.incidents}))

        return FailureAnalysisReport(
            report_id=f"far_{uuid.uuid4().hex[:12]}",
            timestamp_ns=time.perf_counter_ns(),
            incident_count=len(self.incidents),
            incidents=list(self.incidents),
            has_critical_failure=has_critical,
            affected_subsystems=affected,
        )

    def clear(self) -> None:
        self.incidents.clear()
