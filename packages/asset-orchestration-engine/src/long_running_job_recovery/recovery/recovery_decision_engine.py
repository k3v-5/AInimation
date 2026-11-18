from typing import Tuple
from ..core.job_types import ErrorCategory, RecoveryAction
from ..core.job_schema import Job, JobError

class RecoveryDecisionEngine:
    @classmethod
    def decide_recovery(cls, job: Job, error: JobError) -> RecoveryAction:
        if not error.recoverable:
            return RecoveryAction.FAIL

        if job.attempt >= job.definition.retry_policy.max_attempts:
            return RecoveryAction.FAIL

        if error.category in [ErrorCategory.NETWORK_ERROR, ErrorCategory.CAPABILITY_ERROR, ErrorCategory.BLENDER_ERROR]:
            return RecoveryAction.RETRY

        if error.category == ErrorCategory.VALIDATION_ERROR:
            return RecoveryAction.ROLLBACK

        return RecoveryAction.FAIL
