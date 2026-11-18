"""
Tests for Diagnostics, Errors, and Metrics.
Verifies error hierarchy, recoverability/retryability flags, and structured reporting.
UAF-81.0 Sections 27, 28, 29, 30, 31, 32.
"""

from uaf.core.diagnostics.severity import DiagnosticSeverity
from uaf.core.diagnostics.diagnostic import Diagnostic
from uaf.core.diagnostics.metrics import OperationMetrics
from uaf.core.diagnostics.errors import (
    UAFError,
    SpecificationError,
    ConfigurationError,
    CapabilityError,
    GenerationError,
    ValidationError,
    ArtifactError,
    PersistenceError,
    PackagingError,
    PermissionError,
    ResourceError,
    ExternalProcessError,
    RecoveryError,
)


def test_diagnostic_creation_and_serialization():
    diag = Diagnostic(
        severity=DiagnosticSeverity.WARNING,
        code="POLYCOUNT_HIGH",
        message="Polygon count exceeds recommended budget for mobile.",
        component="mesh_validator",
        operation_id="op_mesh_01",
        asset_id="asset_vehicle",
        details={"current_polys": 55000, "budget": 40000},
    )
    data = diag.to_dict()
    assert data["severity"] == "WARNING"
    assert data["code"] == "POLYCOUNT_HIGH"

    reconstructed = Diagnostic.from_dict(data)
    assert reconstructed.code == diag.code
    assert reconstructed.severity == DiagnosticSeverity.WARNING


def test_uaf_error_recoverable_and_retryable_flags():
    gen_err = GenerationError("Blender subprocess killed by OS", operation_id="op_b1")
    assert gen_err.retryable is True
    assert gen_err.recoverable is False

    spec_err = SpecificationError("Missing bounding box parameter", asset_id="asset_01")
    assert spec_err.recoverable is True

    perm_err = PermissionError("Write access denied")
    assert perm_err.retryable is False
    assert perm_err.recoverable is False


def test_uaf_error_serialization():
    err = ResourceError(
        "Memory limit exceeded: 8GB > 4GB budget",
        operation_id="op_heavy",
        asset_id="terrain_01",
        phase="surface_synthesis",
        details={"peak_mb": 8192, "limit_mb": 4096},
    )
    data = err.to_dict()
    assert data["type"] == "ResourceError"
    assert data["code"] == "RESOURCE_ERROR"
    assert data["recoverable"] is True
    assert data["retryable"] is True
    assert data["details"]["peak_mb"] == 8192


def test_operation_metrics():
    metrics = OperationMetrics(
        duration_ms=450.5,
        cpu_time_ms=420.0,
        memory_peak_mb=128.5,
        disk_write_bytes=1048576,
        artifact_count=3,
        cache_hit=False,
    )
    data = metrics.to_dict()
    reconstructed = OperationMetrics.from_dict(data)
    assert reconstructed.duration_ms == 450.5
    assert reconstructed.disk_write_bytes == 1048576
    assert reconstructed.artifact_count == 3
