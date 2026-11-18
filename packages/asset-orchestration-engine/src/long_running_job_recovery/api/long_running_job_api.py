from typing import Dict, Any, List, Optional
from ..core.job_types import (
    JobType, JobState, JobPriority, BackoffStrategy,
    ErrorCategory, RecoveryAction
)
from ..core.job_schema import (
    JobIdentity, JobDefinition, Job, JobCheckpoint,
    JobProgress, JobEvent, RecoverableJob, RecoveryReport,
    JobValidationResult
)
from ..engine.long_running_job_service import LongRunningJobService

class LongRunningJobAPI:
    """
    Long-Running Job API (AOE v70)
    
    Regla Fundamental:
    A LONG-RUNNING JOB MUST NEVER DEPEND ON MEMORY ALONE.
    TODA OPERACIÓN LARGA DEL PIPELINE PERSISTE SUS ESTADOS, CHECKPOINTS HASH-CHAINED,
    LEASES Y HEARTBEATS, SOPORTANDO REANUDACIÓN Y RECUPERACIÓN AUTOMÁTICA O MANUAL ANTE CRASHES.
    """
    def __init__(self, service_version: str = "1.0.0", storage_dir: Optional[str] = None):
        self._service = LongRunningJobService(service_version=service_version, storage_dir=storage_dir)

    def create_and_start_job(
        self,
        job_type: JobType,
        asset_id: str,
        semantic_id: str,
        input_params: Optional[Dict[str, Any]] = None,
        priority: JobPriority = JobPriority.NORMAL,
        worker_id: str = "WORKER_MAIN",
        job_id: Optional[str] = None
    ) -> Job:
        return self._service.create_and_start_job(
            job_type, asset_id, semantic_id, input_params, priority, worker_id, job_id
        )

    def create_checkpoint(
        self,
        job_id: str,
        phase: str,
        step: str,
        state_hash: str,
        input_hash: str = "",
        output_hash: str = "",
        progress_percent: float = 0.0
    ) -> JobCheckpoint:
        return self._service.checkpoint_job(
            job_id, phase, step, state_hash, input_hash, output_hash, progress_percent
        )

    def pause_job(self, job_id: str) -> Job:
        return self._service.pause_job(job_id)

    def resume_job(self, job_id: str, worker_id: str = "WORKER_MAIN") -> Job:
        return self._service.resume_job(job_id, worker_id)

    def cancel_job(self, job_id: str) -> Job:
        return self._service.cancel_job(job_id)

    def complete_job(self, job_id: str) -> Job:
        return self._service.complete_job(job_id)

    def export_recoverable_job(self, job_id: str) -> Optional[RecoverableJob]:
        return self._service.export_recoverable_job(job_id)

    def recover_interrupted_jobs(self) -> List[RecoveryReport]:
        return self._service.recovery_manager.detect_and_recover_interrupted_jobs()

    def recover_job_manually(self, job_id: str, checkpoint_id: Optional[str] = None) -> RecoveryReport:
        return self._service.recovery_manager.recover_job_manually(job_id, checkpoint_id)

    def validate_job(self, job: Job) -> JobValidationResult:
        return self._service.validate_job(job)
