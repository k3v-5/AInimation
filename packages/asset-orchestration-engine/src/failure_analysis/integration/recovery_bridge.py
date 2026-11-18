from typing import Optional, Dict, Any
from ...long_running_job_recovery import LongRunningJobAPI

class RecoveryBridge:
    """Bridges Failure Analysis to F70 Long-Running Job & Recovery System."""

    def __init__(self, job_api: Optional[LongRunningJobAPI] = None):
        self.jobs = job_api or LongRunningJobAPI()

    def record_job_failure(self, job_id: str, error_message: str):
        job = self.jobs.get_job(job_id)
        if job:
            self.jobs.fail_job(job_id, error_message)

    def restore_checkpoint(self, checkpoint_id: str) -> Optional[Dict[str, Any]]:
        return self.jobs.checkpoints.get_checkpoint(checkpoint_id)
