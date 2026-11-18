from typing import Tuple
from ..core.production_job import ProductionJob, JobStatus
from ..core.state_machine import ProductionStateMachine

class CancellationManager:
    """Handles safe cancellation of running production jobs, releasing locks."""

    @staticmethod
    def cancel_job(job: ProductionJob, reason: str = "User requested cancellation") -> Tuple[bool, str]:
        if job.status in (JobStatus.COMPLETED, JobStatus.CANCELLED, JobStatus.REJECTED):
            return False, f"Cannot cancel job in terminal state {job.status.value}"

        ProductionStateMachine.transition(job, JobStatus.CANCELLED)
        job.failure_state = {"cancellation_reason": reason}
        return True, "Job cancelled safely"
