"""Engine and schema compatibility validation for the UE5 bridge."""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from uaf.bridge.ue5.protocol.versioning import BridgeProtocolVersion, VersionMismatchError
from uaf.bridge.ue5.protocol.capabilities import UE5Capabilities, UE5Feature


@dataclass
class ValidationIssue:
    """Represents a compatibility or schema issue."""
    severity: str  # "ERROR", "WARNING", "INFO"
    code: str
    message: str
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CompatibilityReport:
    """Comprehensive report on engine and protocol compatibility."""
    is_compatible: bool
    protocol_version: str
    engine_version: str
    issues: List[ValidationIssue] = field(default_factory=list)

    @property
    def has_errors(self) -> bool:
        return any(issue.severity == "ERROR" for issue in self.issues)


class EngineCompatibilityValidator:
    """Validates compatibility between UAF bridge and target Unreal Engine version/features."""

    SUPPORTED_ENGINE_VERSIONS = {"5.3", "5.4", "5.5"}

    def __init__(self, target_protocol: Optional[BridgeProtocolVersion] = None) -> None:
        self.target_protocol = target_protocol or BridgeProtocolVersion()

    def validate_engine(
        self,
        engine_version: str,
        capabilities: Optional[UE5Capabilities] = None,
        remote_protocol: Optional[BridgeProtocolVersion] = None,
    ) -> CompatibilityReport:
        issues: List[ValidationIssue] = []

        # 1. Engine version check (major.minor)
        major_minor = ".".join(engine_version.split(".")[:2])
        if major_minor not in self.SUPPORTED_ENGINE_VERSIONS:
            issues.append(
                ValidationIssue(
                    severity="ERROR",
                    code="UNSUPPORTED_ENGINE_VERSION",
                    message=f"Unreal Engine version {engine_version} is not officially supported. Expected one of {sorted(self.SUPPORTED_ENGINE_VERSIONS)}.",
                    details={"engine_version": engine_version},
                )
            )

        # 2. Protocol version handshake check
        if remote_protocol is not None:
            try:
                self.target_protocol.assert_compatible(remote_protocol)
            except VersionMismatchError as ex:
                issues.append(
                    ValidationIssue(
                        severity="ERROR",
                        code="PROTOCOL_VERSION_MISMATCH",
                        message=str(ex),
                        details={"target": str(self.target_protocol), "remote": str(remote_protocol)},
                    )
                )

        # 3. Capability requirements
        if capabilities:
            if not capabilities.has_feature(UE5Feature.NANITE):
                issues.append(
                    ValidationIssue(
                        severity="WARNING",
                        code="FEATURE_MISSING_NANITE",
                        message="Target engine does not report Nanite capability; fallback LODs will be enforced.",
                    )
                )
            if not capabilities.has_feature(UE5Feature.LUMEN):
                issues.append(
                    ValidationIssue(
                        severity="WARNING",
                        code="FEATURE_MISSING_LUMEN",
                        message="Target engine does not report Lumen capability; global illumination will use baked/probe fallback.",
                    )
                )

        is_compatible = not any(issue.severity == "ERROR" for issue in issues)
        return CompatibilityReport(
            is_compatible=is_compatible,
            protocol_version=str(self.target_protocol),
            engine_version=engine_version,
            issues=issues,
        )
