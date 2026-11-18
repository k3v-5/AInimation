import time
from typing import Dict, Any, List, Optional
from ..core.job_types import JobType, JobState, JobPriority, RecoveryAction
from ..core.job_schema import (
    JobIdentity, JobDefinition, Job, JobCheckpoint,
    JobProgress, JobEvent, RecoverableJob, RecoveryReport,
    JobValidationResult
)
from ..store.job_store import JobStore
from ..recovery.recovery_manager import RecoveryManager
from ..scheduler.job_scheduler import JobScheduler
from .job_hasher import JobHasher

class LongRunningJobService:
    """
    Long-Running Job & Recovery Service (AOE v70)
    
    Regla Fundamental:
    A LONG-RUNNING JOB MUST NEVER DEPEND ON MEMORY ALONE.
    TODA OPERACIÓN LARGA DEL PIPELINE PERSISTE SUS ESTADOS, CHECKPOINTS HASH-CHAINED,
    LEASES Y HEARTBEATS, SOPORTANDO REANUDACIÓN Y RECUPERACIÓN AUTOMÁTICA O MANUAL ANTE CRASHES.
    """
    def __init__(self, service_version: str = "1.0.0", storage_dir: Optional[str] = None):
        self.service_version = service_version
        self.store = JobStore(storage_dir=storage_dir)
        self.recovery_manager = RecoveryManager(self.store)
        self.scheduler = JobScheduler(self.store)

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
        job_id = job_id or f"JOB_{asset_id}_{int(time.time()*1000)%100000}"
        identity = JobIdentity(job_id=job_id, asset_id=asset_id, semantic_id=semantic_id)
        definition = JobDefinition(job_type=job_type, input_params=input_params or {}, priority=priority)

        job = Job(
            identity=identity,
            definition=definition,
            state=JobState.CREATED,
            progress=JobProgress(overall_percent=0.0, current_phase="START", current_step="INIT"),
            created_at=time.time(),
            updated_at=time.time()
        )
        self.store.save_job(job)
        self.store.record_event(JobEvent(
            event_id=f"EVT_{job_id}_0", job_id=job_id,
            event_type="JOB_CREATED", state=JobState.CREATED, timestamp=time.time()
        ))

        # Enqueue and acquire
        self.scheduler.enqueue_job(job)
        acquired = self.scheduler.acquire_next_job(worker_id)
        return acquired or job

    def checkpoint_job(
        self,
        job_id: str,
        phase: str,
        step: str,
        state_hash: str,
        input_hash: str = "",
        output_hash: str = "",
        progress_percent: float = 0.0
    ) -> JobCheckpoint:
        job = self.store.get_job(job_id)
        if not job:
            raise ValueError(f"Job {job_id} not found.")

        latest = self.store.get_latest_checkpoint(job_id)
        prev_hash = latest.state_hash if latest else "ROOT"
        
        ckpt_id = f"CKPT_{job_id}_{int(time.time()*1000)%100000}"
        ckpt_hash = JobHasher.compute_checkpoint_hash(job_id, phase, step, state_hash, prev_hash)

        ckpt = JobCheckpoint(
            checkpoint_id=ckpt_id,
            job_id=job_id,
            phase=phase,
            step=step,
            state_hash=ckpt_hash,
            input_hash=input_hash,
            output_hash=output_hash,
            previous_checkpoint_id=latest.checkpoint_id if latest else None,
            created_at=time.time()
        )
        self.store.save_checkpoint(ckpt)

        job.checkpoint_id = ckpt_id
        job.current_phase = phase
        job.current_step = step
        job.progress.overall_percent = progress_percent
        job.progress.current_phase = phase
        job.progress.current_step = step
        self.store.save_job(job)

        self.store.record_event(JobEvent(
            event_id=f"EVT_{ckpt_id}", job_id=job_id,
            event_type="JOB_CHECKPOINT_CREATED", state=job.state, timestamp=time.time(),
            payload={"checkpoint_id": ckpt_id, "phase": phase, "step": step}
        ))

        return ckpt

    def pause_job(self, job_id: str) -> Job:
        job = self.store.get_job(job_id)
        if job and job.state == JobState.RUNNING:
            job.state = JobState.PAUSED
            self.store.save_job(job)
            self.store.record_event(JobEvent(
                event_id=f"EVT_PAUSE_{job_id}", job_id=job_id,
                event_type="JOB_PAUSED", state=JobState.PAUSED, timestamp=time.time()
            ))
        return job

    def resume_job(self, job_id: str, worker_id: str = "WORKER_MAIN") -> Job:
        job = self.store.get_job(job_id)
        if job and job.state == JobState.PAUSED:
            job.state = JobState.RUNNING
            job.worker_id = worker_id
            job.last_heartbeat = time.time()
            self.store.save_job(job)
            self.store.record_event(JobEvent(
                event_id=f"EVT_RESUME_{job_id}", job_id=job_id,
                event_type="JOB_RESUMED", state=JobState.RUNNING, timestamp=time.time()
            ))
        return job

    def cancel_job(self, job_id: str) -> Job:
        job = self.store.get_job(job_id)
        if job:
            job.state = JobState.CANCELLED
            job.completed_at = time.time()
            self.store.save_job(job)
            self.store.record_event(JobEvent(
                event_id=f"EVT_CANCEL_{job_id}", job_id=job_id,
                event_type="JOB_CANCELLED", state=JobState.CANCELLED, timestamp=time.time()
            ))
        return job

    def complete_job(self, job_id: str) -> Job:
        job = self.store.get_job(job_id)
        if job:
            job.state = JobState.COMPLETED
            job.progress.overall_percent = 100.0
            job.completed_at = time.time()
            self.store.save_job(job)
            self.store.record_event(JobEvent(
                event_id=f"EVT_COMPLETE_{job_id}", job_id=job_id,
                event_type="JOB_COMPLETED", state=JobState.COMPLETED, timestamp=time.time()
            ))
        return job

    def export_recoverable_job(self, job_id: str) -> Optional[RecoverableJob]:
        job = self.store.get_job(job_id)
        if not job:
            return None
        
        latest_ckpt = self.store.get_latest_checkpoint(job_id)
        ckpt_hash = latest_ckpt.state_hash if latest_ckpt else "NONE"

        return RecoverableJob(
            job_id=job.identity.job_id,
            asset_id=job.identity.asset_id,
            semantic_id=job.identity.semantic_id,
            job_type=job.definition.job_type,
            state=job.state,
            current_phase=job.current_phase,
            progress=job.progress,
            checkpoint_id=job.checkpoint_id,
            checkpoint_hash=ckpt_hash,
            attempt=job.attempt,
            last_heartbeat=job.last_heartbeat,
            errors=job.errors,
            recovery_history=[]
        )

    def validate_job(self, job: Job) -> JobValidationResult:
        errors = []
        warnings = []
        if not job.identity.job_id:
            errors.append("MISSING_JOB_ID: Job ID is mandatory.")
        if job.state == JobState.RUNNING and not job.worker_id:
            errors.append("RUNNING_WITHOUT_WORKER: Active job must have assigned worker.")
        return JobValidationResult(is_valid=(len(errors) == 0), errors=errors, warnings=warnings)
