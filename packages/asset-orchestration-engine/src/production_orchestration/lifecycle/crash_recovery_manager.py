from typing import Dict, Any, Optional
from ..core.production_job import ProductionJob, JobStatus
from ..core.state_machine import ProductionStateMachine

class CrashRecoveryManager:
    """Coordinates job recovery from checkpoints without duplicate generation."""

    @staticmethod
    def recover_job(job: ProductionJob, checkpoint_data: Dict[str, Any]) -> bool:
        if job.status not in (JobStatus.FAILED, JobStatus.PAUSED, JobStatus.RUNNING):
            return False

        ProductionStateMachine.transition(job, JobStatus.RECOVERING)
        job.checkpoint_id = checkpoint_data.get("checkpoint_id", job.checkpoint_id)
        job.current_stage = checkpoint_data.get("stage", job.current_stage)
        job.attempt += 1

        ProductionStateMachine.transition(job, JobStatus.RUNNING)
        return True
