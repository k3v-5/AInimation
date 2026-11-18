from typing import Set, Dict, Tuple
from .production_job import JobStatus, ProductionJob

class ProductionStateMachine:
    """Enforces rigorous, deterministic state transitions for ProductionJobs."""

    VALID_TRANSITIONS: Dict[JobStatus, Set[JobStatus]] = {
        JobStatus.CREATED: {JobStatus.PLANNED, JobStatus.FAILED, JobStatus.CANCELLED},
        JobStatus.PLANNED: {JobStatus.QUEUED, JobStatus.RUNNING, JobStatus.FAILED, JobStatus.CANCELLED},
        JobStatus.QUEUED: {JobStatus.RUNNING, JobStatus.PAUSED, JobStatus.CANCELLED, JobStatus.FAILED},
        JobStatus.RUNNING: {
            JobStatus.WAITING, JobStatus.EVALUATING, JobStatus.CORRECTING,
            JobStatus.OPTIMIZING, JobStatus.REGRESSION_CHECK, JobStatus.PACKAGING,
            JobStatus.DELIVERING, JobStatus.COMPLETED, JobStatus.FAILED,
            JobStatus.CANCELLED, JobStatus.PAUSED, JobStatus.REJECTED
        },
        JobStatus.WAITING: {JobStatus.RUNNING, JobStatus.FAILED, JobStatus.CANCELLED},
        JobStatus.EVALUATING: {JobStatus.CORRECTING, JobStatus.OPTIMIZING, JobStatus.REGRESSION_CHECK, JobStatus.REJECTED, JobStatus.FAILED},
        JobStatus.CORRECTING: {JobStatus.EVALUATING, JobStatus.REJECTED, JobStatus.FAILED, JobStatus.RUNNING},
        JobStatus.OPTIMIZING: {JobStatus.REGRESSION_CHECK, JobStatus.EVALUATING, JobStatus.FAILED, JobStatus.REJECTED},
        JobStatus.REGRESSION_CHECK: {JobStatus.PACKAGING, JobStatus.CORRECTING, JobStatus.REJECTED, JobStatus.FAILED},
        JobStatus.PACKAGING: {JobStatus.DELIVERING, JobStatus.FAILED, JobStatus.CANCELLED},
        JobStatus.DELIVERING: {JobStatus.COMPLETED, JobStatus.FAILED},
        JobStatus.COMPLETED: set(), # Terminal state: no modification without new version
        JobStatus.FAILED: {JobStatus.RECOVERING, JobStatus.CANCELLED},
        JobStatus.CANCELLED: set(), # Terminal
        JobStatus.PAUSED: {JobStatus.RUNNING, JobStatus.CANCELLED},
        JobStatus.RECOVERING: {JobStatus.RUNNING, JobStatus.FAILED, JobStatus.CANCELLED},
        JobStatus.REJECTED: {JobStatus.RECOVERING, JobStatus.CANCELLED}
    }

    @classmethod
    def can_transition(cls, current_status: JobStatus, target_status: JobStatus) -> bool:
        if current_status == target_status:
            return True
        allowed = cls.VALID_TRANSITIONS.get(current_status, set())
        return target_status in allowed

    @classmethod
    def transition(cls, job: ProductionJob, target_status: JobStatus) -> Tuple[bool, str]:
        if not cls.can_transition(job.status, target_status):
            return False, f"Illegal state transition from {job.status.value} to {target_status.value}"
        job.status = target_status
        return True, f"Job transitioned to {target_status.value}"
