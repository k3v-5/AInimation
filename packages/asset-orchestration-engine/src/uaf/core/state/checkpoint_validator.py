"""
CheckpointValidator verifies checkpoint data and hashes prior to restoration.
UAF-81.0 Section 40.
"""

from typing import Optional, List, Dict, Any
from .checkpoint import Checkpoint
from ..artifacts.artifact import Artifact
from ..diagnostics.errors import RecoveryError


class CheckpointValidationResult:
    def __init__(self, is_valid: bool, reasons: Optional[List[str]] = None):
        self.is_valid = is_valid
        self.reasons = reasons or []

    def to_dict(self) -> Dict[str, Any]:
        return {
            "is_valid": self.is_valid,
            "reasons": self.reasons,
        }


class CheckpointValidator:
    """
    Guarantees that a checkpoint is valid, compatible, and uncorrupted before restoring.
    """
    SUPPORTED_SCHEMA_VERSIONS = {"1.0.0"}

    @classmethod
    def validate_for_restore(
        cls,
        checkpoint: Checkpoint,
        expected_input_hash: Optional[str] = None,
        expected_config_hash: Optional[str] = None,
        verify_artifacts_on_disk: bool = True,
    ) -> CheckpointValidationResult:
        reasons = []

        # Schema version check
        if checkpoint.schema_version not in cls.SUPPORTED_SCHEMA_VERSIONS:
            reasons.append(
                f"Unsupported checkpoint schema_version '{checkpoint.schema_version}'. Supported: {cls.SUPPORTED_SCHEMA_VERSIONS}"
            )

        # Input hash match check
        if expected_input_hash and checkpoint.input_hash != expected_input_hash:
            reasons.append(
                f"Input hash mismatch: expected '{expected_input_hash}', checkpoint has '{checkpoint.input_hash}'."
            )

        # Config hash match check
        if expected_config_hash and checkpoint.configuration_hash != expected_config_hash:
            reasons.append(
                f"Configuration hash mismatch: expected '{expected_config_hash}', checkpoint has '{checkpoint.configuration_hash}'."
            )

        # Artifact integrity check
        if verify_artifacts_on_disk:
            for art_data in checkpoint.artifacts:
                try:
                    artifact = Artifact.from_dict(art_data)
                    if not artifact.verify_integrity():
                        reasons.append(f"Artifact '{artifact.artifact_id}' failed integrity verification.")
                except Exception as e:
                    reasons.append(f"Failed to verify artifact from checkpoint: {str(e)}")

        is_valid = len(reasons) == 0
        return CheckpointValidationResult(is_valid=is_valid, reasons=reasons)

    @classmethod
    def assert_valid_for_restore(
        cls,
        checkpoint: Checkpoint,
        expected_input_hash: Optional[str] = None,
        expected_config_hash: Optional[str] = None,
        verify_artifacts_on_disk: bool = True,
    ) -> None:
        result = cls.validate_for_restore(
            checkpoint=checkpoint,
            expected_input_hash=expected_input_hash,
            expected_config_hash=expected_config_hash,
            verify_artifacts_on_disk=verify_artifacts_on_disk,
        )
        if not result.is_valid:
            raise RecoveryError(
                f"Cannot restore checkpoint '{checkpoint.checkpoint_id}': {'; '.join(result.reasons)}",
                details={"reasons": result.reasons},
            )
