import time
from typing import Dict, List, Optional
from ..core.job_types import JobState, JobPriority
from ..core.job_schema import Job
from ..store.job_store import JobStore

class JobScheduler:
    def __init__(self, store: JobStore, lease_duration_sec: float = 30.0):
        self.store = store
        self.lease_duration_sec = lease_duration_sec

    def enqueue_job(self, job: Job):
        job.state = JobState.QUEUED
        self.store.save_job(job)

    def acquire_next_job(self, worker_id: str) -> Optional[Job]:
        queued_jobs = self.store.list_jobs(state=JobState.QUEUED)
        if not queued_jobs:
            return None

        # Sort by priority
        priority_map = {
            JobPriority.CRITICAL: 1,
            JobPriority.HIGH: 2,
            JobPriority.NORMAL: 3,
            JobPriority.LOW: 4,
            JobPriority.BACKGROUND: 5
        }
        queued_jobs.sort(key=lambda j: priority_map.get(j.definition.priority, 3))
        selected_job = queued_jobs[0]

        now = time.time()
        selected_job.state = JobState.RUNNING
        selected_job.worker_id = worker_id
        selected_job.lease_id = f"LEASE_{selected_job.identity.job_id}_{worker_id}"
        selected_job.last_heartbeat = now
        self.store.save_job(selected_job)

        return selected_job

    def heartbeat(self, job_id: str, worker_id: str) -> bool:
        job = self.store.get_job(job_id)
        if not job or job.worker_id != worker_id or job.state != JobState.RUNNING:
            return False
        job.last_heartbeat = time.time()
        self.store.save_job(job)
        return True

    def detect_stale_leases(self) -> List[Job]:
        stale: List[Job] = []
        now = time.time()
        running_jobs = self.store.list_jobs(state=JobState.RUNNING)
        for job in running_jobs:
            if (now - job.last_heartbeat) > self.lease_duration_sec:
                stale.append(job)
        return stale
