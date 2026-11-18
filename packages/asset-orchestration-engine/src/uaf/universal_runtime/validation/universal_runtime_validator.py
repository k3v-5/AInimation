"""
Universal Runtime Validator (UAF-81.64).
Authoritative state transition validator, dependency integrity validator,
health consistency checker, secret redaction auditor, and diagnostic bundle verifier.
"""

from __future__ import annotations
import hashlib
import json
import re
import time
from typing import Any, Dict, List, Set, Tuple

from ..models.definition import (
    RuntimeState,
    ServiceLifecycle,
    HealthState,
    ServiceDefinition,
    HealthReport,
    DiagnosticBundle,
    RuntimeDiagnosticReport,
)


class UniversalRuntimeValidator:
    """
    Authoritative validator enforcing UAF-81.64 runtime constraints.
    """

    VALID_TRANSITIONS: Dict[RuntimeState, Set[RuntimeState]] = {
        RuntimeState.CREATED: {RuntimeState.BOOTSTRAPPING, RuntimeState.FAILED},
        RuntimeState.BOOTSTRAPPING: {
            RuntimeState.DISCOVERING,
            RuntimeState.SAFE_MODE,
            RuntimeState.RECOVERY_MODE,
            RuntimeState.FAILED,
        },
        RuntimeState.DISCOVERING: {RuntimeState.LOADING_CONFIGURATION, RuntimeState.FAILED},
        RuntimeState.LOADING_CONFIGURATION: {
            RuntimeState.REGISTERING_SERVICES,
            RuntimeState.SAFE_MODE,
            RuntimeState.FAILED,
        },
        RuntimeState.REGISTERING_SERVICES: {
            RuntimeState.RESOLVING_DEPENDENCIES,
            RuntimeState.FAILED,
        },
        RuntimeState.RESOLVING_DEPENDENCIES: {
            RuntimeState.INITIALIZING,
            RuntimeState.SAFE_MODE,
            RuntimeState.FAILED,
        },
        RuntimeState.INITIALIZING: {
            RuntimeState.STARTING,
            RuntimeState.DEGRADED,
            RuntimeState.SAFE_MODE,
            RuntimeState.FAILED,
        },
        RuntimeState.STARTING: {
            RuntimeState.VALIDATING,
            RuntimeState.DEGRADED,
            RuntimeState.FAILED,
        },
        RuntimeState.VALIDATING: {
            RuntimeState.HEALTH_CHECK,
            RuntimeState.DEGRADED,
            RuntimeState.FAILED,
        },
        RuntimeState.HEALTH_CHECK: {
            RuntimeState.READY,
            RuntimeState.DEGRADED,
            RuntimeState.SAFE_MODE,
            RuntimeState.FAILED,
        },
        RuntimeState.READY: {
            RuntimeState.DEGRADED,
            RuntimeState.SAFE_MODE,
            RuntimeState.SHUTTING_DOWN,
            RuntimeState.FAILED,
        },
        RuntimeState.DEGRADED: {
            RuntimeState.READY,
            RuntimeState.SAFE_MODE,
            RuntimeState.SHUTTING_DOWN,
            RuntimeState.FAILED,
        },
        RuntimeState.SAFE_MODE: {
            RuntimeState.READY,
            RuntimeState.RECOVERY_MODE,
            RuntimeState.SHUTTING_DOWN,
            RuntimeState.FAILED,
        },
        RuntimeState.RECOVERY_MODE: {
            RuntimeState.BOOTSTRAPPING,
            RuntimeState.SAFE_MODE,
            RuntimeState.SHUTTING_DOWN,
            RuntimeState.FAILED,
        },
        RuntimeState.SHUTTING_DOWN: {RuntimeState.STOPPED, RuntimeState.FAILED},
        RuntimeState.STOPPED: {RuntimeState.BOOTSTRAPPING, RuntimeState.CREATED},
        RuntimeState.FAILED: {
            RuntimeState.BOOTSTRAPPING,
            RuntimeState.RECOVERY_MODE,
            RuntimeState.SAFE_MODE,
            RuntimeState.SHUTTING_DOWN,
        },
    }

    SECRET_PATTERNS = [
        re.compile(r"bearer\s+[a-zA-Z0-9_\-\.]{20,}", re.IGNORECASE),
        re.compile(r"api[_-]?key", re.IGNORECASE),
        re.compile(r"password", re.IGNORECASE),
    ]

    def validate_state_transition(
        self,
        from_state: RuntimeState,
        to_state: RuntimeState,
    ) -> RuntimeDiagnosticReport:
        errors: List[str] = []
        warnings: List[str] = []
        info: List[str] = []

        allowed = self.VALID_TRANSITIONS.get(from_state, set())
        if to_state not in allowed:
            errors.append(
                f"Illegal state transition from {from_state.value} to {to_state.value}. "
                f"Valid targets: {[s.value for s in allowed]}."
            )
        else:
            info.append(f"Transition {from_state.value} -> {to_state.value} is valid.")

        return RuntimeDiagnosticReport(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            info=info,
        )

    def validate_service_definitions(
        self,
        services: Dict[str, ServiceDefinition],
    ) -> RuntimeDiagnosticReport:
        errors: List[str] = []
        warnings: List[str] = []
        info: List[str] = []

        for sid, defn in services.items():
            if not sid or not sid.strip():
                errors.append("Encountered empty service_id in definitions.")
            if defn.startup_timeout <= 0:
                errors.append(f"Service '{sid}' has non-positive startup_timeout: {defn.startup_timeout}")
            if defn.shutdown_timeout <= 0:
                errors.append(f"Service '{sid}' has non-positive shutdown_timeout: {defn.shutdown_timeout}")
            if defn.heartbeat_timeout <= 0:
                errors.append(f"Service '{sid}' has non-positive heartbeat_timeout: {defn.heartbeat_timeout}")

            for dep in defn.dependencies:
                if dep not in services:
                    errors.append(f"Service '{sid}' requires missing dependency '{dep}'.")

        return RuntimeDiagnosticReport(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            info=info,
        )

    def validate_health_report(
        self,
        report: HealthReport,
        services: Dict[str, ServiceDefinition],
    ) -> RuntimeDiagnosticReport:
        errors: List[str] = []
        warnings: List[str] = []
        info: List[str] = []

        for sid in report.failed_services:
            defn = services.get(sid)
            if defn and defn.is_critical and report.overall_state not in (HealthState.UNHEALTHY, HealthState.FAILED):
                errors.append(
                    f"Critical service '{sid}' is failed, but overall state is '{report.overall_state.value}' "
                    "instead of UNHEALTHY or FAILED."
                )

        return RuntimeDiagnosticReport(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            info=info,
        )

    def validate_diagnostic_bundle(
        self,
        bundle: DiagnosticBundle,
    ) -> RuntimeDiagnosticReport:
        errors: List[str] = []
        warnings: List[str] = []
        info: List[str] = []

        expected = bundle.sha256_digest
        computed = bundle.compute_digest()
        if expected != computed:
            errors.append(f"Digest mismatch: expected '{expected}', computed '{computed}'.")

        serialized = json.dumps(bundle.service_logs)
        for pat in self.SECRET_PATTERNS:
            if pat.search(serialized):
                errors.append("Unredacted credential or secret detected in diagnostic bundle logs.")

        return RuntimeDiagnosticReport(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            info=info,
        )
