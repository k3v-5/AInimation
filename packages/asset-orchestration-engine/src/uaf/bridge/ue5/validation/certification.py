"""LiveLink Golden Scene certification gates and test suite."""

from __future__ import annotations
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class GateResult:
    """Result of evaluating a single certification gate."""
    gate_name: str
    passed: bool
    message: str
    details: Dict[str, Any] = field(default_factory=dict)
    duration_ms: float = 0.0


@dataclass
class CertificationReport:
    """Comprehensive report output by the LiveLink certification gatekeeper."""
    passed: bool
    gates_total: int
    gates_passed: int
    gates_failed: int
    results: List[GateResult] = field(default_factory=list)
    total_duration_ms: float = 0.0

    def summary(self) -> Dict[str, Any]:
        return {
            "passed": self.passed,
            "gates_total": self.gates_total,
            "gates_passed": self.gates_passed,
            "gates_failed": self.gates_failed,
            "total_duration_ms": round(self.total_duration_ms, 2),
            "failures": [
                {"gate": r.gate_name, "message": r.message}
                for r in self.results if not r.passed
            ],
        }


class LiveLinkCertificationSuite:
    """Automated certification suite for verifying UE5 bridge readiness."""

    def __init__(self, bridge: Any) -> None:
        self.bridge = bridge

    def run_all(self) -> CertificationReport:
        t0 = time.perf_counter()
        results: List[GateResult] = []

        # Gate 1: Handshake & Connection state
        results.append(self._gate_connection())

        # Gate 2: Registry integrity
        results.append(self._gate_registry())

        # Gate 3: Transaction atomicity
        results.append(self._gate_transaction_atomicity())

        # Gate 4: Audit trail validity
        results.append(self._gate_audit_trail())

        total_ms = (time.perf_counter() - t0) * 1000.0
        passed_count = sum(1 for r in results if r.passed)
        failed_count = len(results) - passed_count

        return CertificationReport(
            passed=failed_count == 0,
            gates_total=len(results),
            gates_passed=passed_count,
            gates_failed=failed_count,
            results=results,
            total_duration_ms=total_ms,
        )

    def _gate_connection(self) -> GateResult:
        t0 = time.perf_counter()
        try:
            is_active = self.bridge.is_connected
            duration = (time.perf_counter() - t0) * 1000.0
            return GateResult(
                gate_name="GATE_01_CONNECTION",
                passed=is_active,
                message="Bridge connection state verified" if is_active else "Bridge is not connected",
                duration_ms=duration,
            )
        except Exception as e:
            return GateResult(
                gate_name="GATE_01_CONNECTION",
                passed=False,
                message=f"Connection verification failed: {e}",
            )

    def _gate_registry(self) -> GateResult:
        t0 = time.perf_counter()
        try:
            obj_reg = self.bridge.object_registry
            asset_reg = self.bridge.asset_registry
            valid = (obj_reg is not None) and (asset_reg is not None)
            duration = (time.perf_counter() - t0) * 1000.0
            return GateResult(
                gate_name="GATE_02_REGISTRY",
                passed=valid,
                message="Object and asset registries online and accessible",
                duration_ms=duration,
                details={
                    "registered_objects": obj_reg.count if obj_reg else 0,
                    "registered_assets": asset_reg.count if asset_reg else 0,
                },
            )
        except Exception as e:
            return GateResult(
                gate_name="GATE_02_REGISTRY",
                passed=False,
                message=f"Registry verification failed: {e}",
            )

    def _gate_transaction_atomicity(self) -> GateResult:
        t0 = time.perf_counter()
        try:
            tx_mgr = self.bridge.transaction_manager
            # Test transaction staging and commit
            tx = tx_mgr.begin()
            tx.stage_operation("test_op", {"sample": 123})
            tx_mgr.commit(tx.transaction_id)
            duration = (time.perf_counter() - t0) * 1000.0
            return GateResult(
                gate_name="GATE_03_TRANSACTION_ATOMICITY",
                passed=True,
                message="Transaction lifecycle staging and commit verified",
                duration_ms=duration,
            )
        except Exception as e:
            return GateResult(
                gate_name="GATE_03_TRANSACTION_ATOMICITY",
                passed=False,
                message=f"Transaction atomicity check failed: {e}",
            )

    def _gate_audit_trail(self) -> GateResult:
        t0 = time.perf_counter()
        try:
            audit = self.bridge.audit_trail
            valid_chain = audit.verify_chain()
            duration = (time.perf_counter() - t0) * 1000.0
            return GateResult(
                gate_name="GATE_04_AUDIT_TRAIL",
                passed=valid_chain,
                message="Tamper-evident audit trail hash chain verified" if valid_chain else "Audit trail hash chain broken",
                duration_ms=duration,
                details={"audit_entries": audit.count},
            )
        except Exception as e:
            return GateResult(
                gate_name="GATE_04_AUDIT_TRAIL",
                passed=False,
                message=f"Audit trail verification failed: {e}",
            )
