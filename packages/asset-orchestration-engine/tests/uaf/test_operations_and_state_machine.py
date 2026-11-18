"""
Tests for Operation, OperationStatus, and OperationStateMachine.
Verifies valid execution progression and strict rejection of illegal state transitions.
UAF-81.0 Sections 17, 18, 19, 20, 21.
"""

import pytest
from uaf.core.operations.operation import Operation
from uaf.core.operations.operation_types import OperationType
from uaf.core.operations.operation_status import OperationStatus
from uaf.core.operations.operation_result import OperationResult
from uaf.core.operations.state_machine import OperationStateMachine, InvalidStateTransitionError


def test_operation_creation_and_defaults():
    op = Operation(
        operation_id="op_gen_01",
        operation_type=OperationType.GENERATE,
        asset_id="asset_rock",
    )
    assert op.status == OperationStatus.PENDING
    assert op.operation_type == OperationType.GENERATE


def test_valid_operation_lifecycle():
    op = Operation(
        operation_id="op_valid",
        operation_type=OperationType.GENERATE,
        asset_id="asset_rock",
    )

    op.transition_to(OperationStatus.READY)
    assert op.status == OperationStatus.READY

    op.transition_to(OperationStatus.RUNNING)
    assert op.status == OperationStatus.RUNNING

    op.transition_to(OperationStatus.SUCCEEDED)
    assert op.status == OperationStatus.SUCCEEDED


def test_illegal_succeeded_to_running_rejected():
    op = Operation(
        operation_id="op_fail",
        operation_type=OperationType.GENERATE,
        asset_id="asset_rock",
    )
    op.transition_to(OperationStatus.READY)
    op.transition_to(OperationStatus.RUNNING)
    op.transition_to(OperationStatus.SUCCEEDED)

    with pytest.raises(InvalidStateTransitionError, match="SUCCEEDED -> RUNNING"):
        op.transition_to(OperationStatus.RUNNING)


def test_illegal_cancelled_to_running_rejected():
    op = Operation(
        operation_id="op_cancel",
        operation_type=OperationType.GENERATE,
        asset_id="asset_rock",
    )
    op.transition_to(OperationStatus.CANCELLED)

    with pytest.raises(InvalidStateTransitionError, match="CANCELLED -> RUNNING"):
        op.transition_to(OperationStatus.RUNNING)


def test_illegal_failed_to_succeeded_rejected():
    op = Operation(
        operation_id="op_failed",
        operation_type=OperationType.GENERATE,
        asset_id="asset_rock",
    )
    op.transition_to(OperationStatus.READY)
    op.transition_to(OperationStatus.RUNNING)
    op.transition_to(OperationStatus.FAILED)

    with pytest.raises(InvalidStateTransitionError, match="FAILED -> SUCCEEDED"):
        op.transition_to(OperationStatus.SUCCEEDED)


def test_retry_flow_from_failed():
    """An operation can only retry by transitioning from FAILED to READY."""
    op = Operation(
        operation_id="op_retry",
        operation_type=OperationType.GENERATE,
        asset_id="asset_rock",
    )
    op.transition_to(OperationStatus.READY)
    op.transition_to(OperationStatus.RUNNING)
    op.transition_to(OperationStatus.FAILED)

    op.transition_to(OperationStatus.READY)  # Retry approved
    assert op.status == OperationStatus.READY


def test_operation_result_serialization():
    res = OperationResult(
        operation_id="op_res_01",
        status=OperationStatus.SUCCEEDED,
        artifacts=[{"artifact_id": "art_01"}],
        duration_seconds=1.25,
    )
    assert res.is_success
    data = res.to_dict()
    reconstructed = OperationResult.from_dict(data)
    assert reconstructed.operation_id == "op_res_01"
    assert reconstructed.status == OperationStatus.SUCCEEDED
