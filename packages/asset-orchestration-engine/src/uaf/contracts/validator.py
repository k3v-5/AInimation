"""
ContractValidator validates UAF specifications, operations, artifacts, and manifests against schema contracts.
UAF-81.0 Section 44.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from ..core.specification.asset_specification import AssetSpecification
from ..core.operations.operation import Operation
from ..core.operations.operation_result import OperationResult
from ..core.artifacts.artifact import Artifact
from ..core.artifacts.artifact_manifest import ArtifactManifest
from ..core.configuration.uaf_config import UAFConfig
from ..core.diagnostics.diagnostic import Diagnostic
from ..core.diagnostics.severity import DiagnosticSeverity


@dataclass
class ValidationReport:
    is_valid: bool
    diagnostics: List[Diagnostic] = field(default_factory=list)

    def add_error(self, code: str, message: str, component: str = "validator", **kwargs) -> None:
        self.is_valid = False
        self.diagnostics.append(
            Diagnostic(
                severity=DiagnosticSeverity.ERROR,
                code=code,
                message=message,
                component=component,
                **kwargs,
            )
        )

    def add_warning(self, code: str, message: str, component: str = "validator", **kwargs) -> None:
        self.diagnostics.append(
            Diagnostic(
                severity=DiagnosticSeverity.WARNING,
                code=code,
                message=message,
                component=component,
                **kwargs,
            )
        )


class ContractValidator:
    """
    Central validation engine for all UAF core contracts.
    """

    @classmethod
    def validate_specification(cls, spec: AssetSpecification) -> ValidationReport:
        report = ValidationReport(is_valid=True)
        if not spec.identity or not spec.identity.asset_id:
            report.add_error("SPEC_MISSING_ASSET_ID", "Asset specification must have a non-empty asset_id.")
        if not spec.schema_version:
            report.add_error("SPEC_MISSING_SCHEMA_VERSION", "Asset specification must specify schema_version.")
        if not isinstance(spec.seed, int) or spec.seed < 0:
            report.add_error("SPEC_INVALID_SEED", f"Specification seed must be a non-negative integer, got {spec.seed}.")
        return report

    @classmethod
    def validate_operation(cls, op: Operation) -> ValidationReport:
        report = ValidationReport(is_valid=True)
        if not op.operation_id:
            report.add_error("OP_MISSING_ID", "Operation must have an operation_id.")
        if not op.asset_id:
            report.add_error("OP_MISSING_ASSET_ID", "Operation must reference an asset_id.")
        if not op.operation_type:
            report.add_error("OP_MISSING_TYPE", "Operation must declare an operation_type.")
        return report

    @classmethod
    def validate_artifact(cls, artifact: Artifact, verify_content: bool = True) -> ValidationReport:
        report = ValidationReport(is_valid=True)
        if not artifact.artifact_id:
            report.add_error("ART_MISSING_ID", "Artifact must have an artifact_id.")
        if not artifact.content_hash:
            report.add_error("ART_MISSING_HASH", "Artifact must declare a content_hash.")
        if artifact.size < 0:
            report.add_error("ART_INVALID_SIZE", f"Artifact size cannot be negative: {artifact.size}")
        if verify_content and not artifact.verify_integrity():
            report.add_error(
                "ART_INTEGRITY_FAILED",
                f"Artifact '{artifact.artifact_id}' content does not match declared hash '{artifact.content_hash}' or size.",
            )
        return report

    @classmethod
    def validate_result(cls, result: OperationResult) -> ValidationReport:
        report = ValidationReport(is_valid=True)
        if not result.operation_id:
            report.add_error("RESULT_MISSING_OP_ID", "OperationResult must reference an operation_id.")
        if result.duration_seconds < 0:
            report.add_error("RESULT_INVALID_DURATION", "Operation duration cannot be negative.")
        return report

    @classmethod
    def validate_manifest(cls, manifest: ArtifactManifest, verify_artifacts: bool = True) -> ValidationReport:
        report = ValidationReport(is_valid=True)
        if not manifest.manifest_id:
            report.add_error("MANIFEST_MISSING_ID", "ArtifactManifest must have manifest_id.")
        if not manifest.asset_id:
            report.add_error("MANIFEST_MISSING_ASSET_ID", "ArtifactManifest must have asset_id.")

        if verify_artifacts:
            for art in manifest.artifacts:
                art_report = cls.validate_artifact(art, verify_content=True)
                if not art_report.is_valid:
                    for diag in art_report.diagnostics:
                        report.diagnostics.append(diag)
                    report.is_valid = False
        return report

    @classmethod
    def validate_config(cls, config: UAFConfig) -> ValidationReport:
        report = ValidationReport(is_valid=True)
        if not isinstance(config.execution, dict):
            report.add_error("CFG_INVALID_EXECUTION", "Configuration 'execution' section must be a dictionary.")
        if not isinstance(config.security, dict):
            report.add_error("CFG_INVALID_SECURITY", "Configuration 'security' section must be a dictionary.")
        return report
