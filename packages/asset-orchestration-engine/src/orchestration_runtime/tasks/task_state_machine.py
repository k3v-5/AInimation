from typing import Set, Dict
from ..core.runtime_types import RuntimeTaskStatus

class TaskStateMachine:
    VALID_TRANSITIONS: Dict[RuntimeTaskStatus, Set[RuntimeTaskStatus]] = {
        RuntimeTaskStatus.CREATED: {RuntimeTaskStatus.QUEUED, RuntimeTaskStatus.CANCELLED},
        RuntimeTaskStatus.QUEUED: {RuntimeTaskStatus.PLANNING, RuntimeTaskStatus.WAITING, RuntimeTaskStatus.READY, RuntimeTaskStatus.CANCELLED},
        RuntimeTaskStatus.PLANNING: {RuntimeTaskStatus.READY, RuntimeTaskStatus.WAITING, RuntimeTaskStatus.FAILED, RuntimeTaskStatus.CANCELLED},
        RuntimeTaskStatus.WAITING: {RuntimeTaskStatus.READY, RuntimeTaskStatus.BLOCKED, RuntimeTaskStatus.RECOVERING, RuntimeTaskStatus.CANCELLED},
        RuntimeTaskStatus.READY: {RuntimeTaskStatus.RUNNING, RuntimeTaskStatus.CANCELLED},
        RuntimeTaskStatus.RUNNING: {RuntimeTaskStatus.VALIDATING, RuntimeTaskStatus.FAILED, RuntimeTaskStatus.RECOVERING, RuntimeTaskStatus.CANCELLED},
        RuntimeTaskStatus.VALIDATING: {RuntimeTaskStatus.COMPLETED, RuntimeTaskStatus.CORRECTING, RuntimeTaskStatus.FAILED},
        RuntimeTaskStatus.CORRECTING: {RuntimeTaskStatus.RUNNING, RuntimeTaskStatus.FAILED, RuntimeTaskStatus.CANCELLED},
        RuntimeTaskStatus.BLOCKED: {RuntimeTaskStatus.WAITING, RuntimeTaskStatus.CANCELLED, RuntimeTaskStatus.FAILED},
        RuntimeTaskStatus.RECOVERING: {RuntimeTaskStatus.READY, RuntimeTaskStatus.RUNNING, RuntimeTaskStatus.FAILED},
        RuntimeTaskStatus.COMPLETED: set(),
        RuntimeTaskStatus.FAILED: {RuntimeTaskStatus.RECOVERING},
        RuntimeTaskStatus.CANCELLED: set(),
    }

    @classmethod
    def validate_transition(cls, from_status: RuntimeTaskStatus, to_status: RuntimeTaskStatus):
        valid = cls.VALID_TRANSITIONS.get(from_status, set())
        if to_status not in valid:
            raise ValueError(f"INVALID_STATE_TRANSITION: Cannot transition task from '{from_status.value}' to '{to_status.value}'.")
