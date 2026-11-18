"""
OperationStateMachine enforces valid lifecycle transitions and rejects invalid state mutations.
UAF-81.0 Section 20.
"""

from typing import Set, Dict
from .operation_status import OperationStatus


class InvalidStateTransitionError(Exception):
    """Raised when an illegal operation state transition is attempted."""
    pass


class OperationStateMachine:
    """
    Validates state transitions for UAF operations according to normative rules.
    """
    _VALID_TRANSITIONS: Dict[OperationStatus, Set[OperationStatus]] = {
        OperationStatus.PENDING: {
            OperationStatus.READY,
            OperationStatus.CANCELLED,
            OperationStatus.FAILED,
        },
        OperationStatus.READY: {
            OperationStatus.RUNNING,
            OperationStatus.CANCELLED,
        },
        OperationStatus.RUNNING: {
            OperationStatus.SUCCEEDED,
            OperationStatus.FAILED,
            OperationStatus.CANCELLED,
            OperationStatus.PARTIAL,
            OperationStatus.RECOVERABLE,
        },
        OperationStatus.RECOVERABLE: {
            OperationStatus.READY,  # Retry after recovery
            OperationStatus.FAILED,
            OperationStatus.CANCELLED,
        },
        OperationStatus.FAILED: {
            OperationStatus.READY,  # Explicit retry operation
        },
        OperationStatus.PARTIAL: {
            OperationStatus.READY,  # Resume/retry
        },
        OperationStatus.SUCCEEDED: set(),  # Terminal
        OperationStatus.CANCELLED: set(),  # Terminal
    }

    @classmethod
    def validate_transition(cls, current: OperationStatus, target: OperationStatus) -> None:
        """
        Validates transition from current to target status.
        Raises InvalidStateTransitionError if the transition is prohibited.
        """
        if current == target:
            return  # Idempotent state assertion

        allowed = cls._VALID_TRANSITIONS.get(current, set())
        if target not in allowed:
            raise InvalidStateTransitionError(
                f"Illegal operation state transition: {current.value} -> {target.value} is strictly prohibited."
            )
