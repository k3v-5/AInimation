"""Golden Slice certification report and immutable release candidate management."""

from __future__ import annotations
import json
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from uaf.golden_slice.manifest.models import CertificationLevel


@dataclass
class GoldenSliceCertificationReport:
    """Master structured certification report and release candidate certificate."""
    project_id: str
    build_id: str
    target_level: CertificationLevel
    achieved_level: Optional[CertificationLevel]
    is_certified: bool
    final_status: str
    generation_passed: bool
    integration_passed: bool
    qa_tests_passed: bool
    performance_compliant: bool
    determinism_verified: bool
    recovery_verified: bool
    packaging_passed: bool
    critical_failures: int
    blocking_warnings: int
    replay_mismatches: int
    execution_time_s: float
    evidence_package: Dict[str, Any] = field(default_factory=dict)
    release_candidate_tag: Optional[str] = None
    is_immutable: bool = False

    def freeze_as_rc(self) -> None:
        """Labels and locks this build as an immutable GOLDEN_RC (Section 78 & 79)."""
        if self.is_certified:
            self.release_candidate_tag = "GOLDEN_RC"
            self.is_immutable = True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "project_id": self.project_id,
            "build_id": self.build_id,
            "target_level": self.target_level.value,
            "achieved_level": self.achieved_level.value if self.achieved_level else None,
            "is_certified": self.is_certified,
            "final_status": self.final_status,
            "generation_passed": self.generation_passed,
            "integration_passed": self.integration_passed,
            "qa_tests_passed": self.qa_tests_passed,
            "performance_compliant": self.performance_compliant,
            "determinism_verified": self.determinism_verified,
            "recovery_verified": self.recovery_verified,
            "packaging_passed": self.packaging_passed,
            "critical_failures": self.critical_failures,
            "blocking_warnings": self.blocking_warnings,
            "replay_mismatches": self.replay_mismatches,
            "execution_time_s": round(self.execution_time_s, 2),
            "release_candidate_tag": self.release_candidate_tag,
            "is_immutable": self.is_immutable,
            "evidence_package": self.evidence_package,
        }

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent)
