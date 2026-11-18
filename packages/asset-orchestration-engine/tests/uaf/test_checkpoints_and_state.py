"""
Tests for Checkpoint and CheckpointValidator.
Verifies snapshot integrity, hash validation prior to restoration, and detection of tampered artifacts.
UAF-81.0 Sections 39, 40.
"""

import tempfile
import pytest
from pathlib import Path
from uaf.core.state.checkpoint import Checkpoint
from uaf.core.state.checkpoint_validator import CheckpointValidator
from uaf.core.artifacts.artifact import Artifact
from uaf.core.diagnostics.errors import RecoveryError


def test_checkpoint_creation_and_serialization():
    cp = Checkpoint(
        checkpoint_id="cp_stage_01",
        production_id="prod_01",
        operation_id="op_gen",
        state={"step": 3, "progress": 0.5},
        artifacts=[],
        input_hash="hash_input_123",
        configuration_hash="hash_cfg_456",
    )
    data = cp.to_dict()
    reconstructed = Checkpoint.from_dict(data)

    assert reconstructed.checkpoint_id == "cp_stage_01"
    assert reconstructed.input_hash == "hash_input_123"
    assert reconstructed.state["step"] == 3


def test_checkpoint_validation_valid():
    cp = Checkpoint(
        checkpoint_id="cp_valid",
        production_id="p1",
        operation_id="op1",
        state={},
        artifacts=[],
        input_hash="expected_in",
        configuration_hash="expected_cfg",
    )
    res = CheckpointValidator.validate_for_restore(
        cp,
        expected_input_hash="expected_in",
        expected_config_hash="expected_cfg",
    )
    assert res.is_valid is True
    assert len(res.reasons) == 0


def test_checkpoint_validation_mismatched_hashes_rejected():
    cp = Checkpoint(
        checkpoint_id="cp_bad_hash",
        production_id="p1",
        operation_id="op1",
        state={},
        artifacts=[],
        input_hash="hash_alpha",
        configuration_hash="hash_beta",
    )
    res = CheckpointValidator.validate_for_restore(
        cp,
        expected_input_hash="hash_different_input",
        expected_config_hash="hash_beta",
    )
    assert res.is_valid is False
    assert any("Input hash mismatch" in r for r in res.reasons)

    with pytest.raises(RecoveryError, match="Input hash mismatch"):
        CheckpointValidator.assert_valid_for_restore(
            cp,
            expected_input_hash="hash_different_input",
            expected_config_hash="hash_beta",
        )


def test_checkpoint_validation_tampered_artifact_rejected():
    with tempfile.TemporaryDirectory() as tmp:
        f = Path(tmp) / "mesh.bin"
        f.write_bytes(b"good_data")

        art = Artifact.create_from_file(f, "art_mesh", "MESH", "asset_01", "test_producer")

        cp = Checkpoint(
            checkpoint_id="cp_tampered_art",
            production_id="p1",
            operation_id="op1",
            state={},
            artifacts=[art.to_dict()],
            input_hash="in_hash",
            configuration_hash="cfg_hash",
        )

        # Before tampering: valid
        res1 = CheckpointValidator.validate_for_restore(cp, "in_hash", "cfg_hash")
        assert res1.is_valid is True

        # Tamper the file on disk
        f.write_bytes(b"corrupted_tampered_data")

        res2 = CheckpointValidator.validate_for_restore(cp, "in_hash", "cfg_hash")
        assert res2.is_valid is False
        assert any("integrity verification" in r for r in res2.reasons)
