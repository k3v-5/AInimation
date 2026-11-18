import time
from typing import List, Optional
from ..core.job_types import JobState, RecoveryAction
from ..core.job_schema import Job, RecoveryReport, JobError, ErrorCategory
from ..store.job_store import JobStore
from .recovery_decision_engine import RecoveryDecisionEngine

class RecoveryManager:
    def __init__(self, store: JobStore):
        self.store = store

    def detect_and_recover_interrupted_jobs(self) -> List[RecoveryReport]:
        reports: List[RecoveryReport] = []
        active_states = [JobState.RUNNING, JobState.STARTING, JobState.RESUMING, JobState.RECOVERING, JobState.PAUSING]
        all_jobs = self.store.list_jobs()
        running_jobs = [j for j in all_jobs if j.state in active_states]

        for job in running_jobs:
            prev_state = job.state
            latest_ckpt = self.store.get_latest_checkpoint(job.identity.job_id)
            
            if latest_ckpt:
                # Recover to last checkpoint
                job.state = JobState.RESUMING
                job.attempt += 1
                job.current_phase = latest_ckpt.phase
                job.current_step = latest_ckpt.step
                action = RecoveryAction.RESUME
                recovered = True
            else:
                job.state = JobState.RECOVERY_FAILED
                action = RecoveryAction.FAIL
                recovered = False

            self.store.save_job(job)
            
            report = RecoveryReport(
                job_id=job.identity.job_id,
                previous_state=prev_state,
                failure_reason="PROCESS_CRASH_DETECTED",
                checkpoint_used=latest_ckpt.checkpoint_id if latest_ckpt else None,
                action_taken=action,
                final_state=job.state,
                recovered=recovered
            )
            reports.append(report)

        return reports

    def recover_job_manually(self, job_id: str, checkpoint_id: Optional[str] = None) -> RecoveryReport:
        job = self.store.get_job(job_id)
        if not job:
            return RecoveryReport(
                job_id=job_id, previous_state=JobState.FAILED,
                failure_reason="JOB_NOT_FOUND", checkpoint_used=None,
                action_taken=RecoveryAction.FAIL, final_state=JobState.FAILED, recovered=False
            )

        prev_state = job.state
        ckpts = self.store.get_all_checkpoints(job_id)
        target_ckpt = None
        if checkpoint_id:
            for c in ckpts:
                if c.checkpoint_id == checkpoint_id:
                    target_ckpt = c
                    break
        else:
            target_ckpt = ckpts[-1] if ckpts else None

        if target_ckpt:
            job.state = JobState.RESUMING
            job.attempt += 1
            job.current_phase = target_ckpt.phase
            job.current_step = target_ckpt.step
            action = RecoveryAction.RESUME
            recovered = True
        else:
            job.state = JobState.RECOVERY_FAILED
            action = RecoveryAction.FAIL
            recovered = False

        self.store.save_job(job)

        return RecoveryReport(
            job_id=job.identity.job_id,
            previous_state=prev_state,
            failure_reason="MANUAL_RECOVERY_TRIGGERED",
            checkpoint_used=target_ckpt.checkpoint_id if target_ckpt else None,
            action_taken=action,
            final_state=job.state,
            recovered=recovered
        )
