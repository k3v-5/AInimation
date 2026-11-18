"""
OperationStatus defines the lifecycle states of an operation.
UAF-81.0 Section 19.
"""

from enum import Enum


class OperationStatus(str, Enum):
    PENDING = "PENDING"
    READY = "READY"
    RUNNING = "RUNNING"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"
    PARTIAL = "PARTIAL"
    RECOVERABLE = "RECOVERABLE"

    @property
    def is_terminal(self) -> bool:
        return self in (
            OperationStatus.SUCCEEDED,
            OperationStatus.FAILED,
            OperationStatus.CANCELLED,
            OperationStatus.PARTIAL,
        )
