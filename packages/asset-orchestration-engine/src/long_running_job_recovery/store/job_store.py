import os
import json
import time
from typing import Dict, List, Optional, Any
from ..core.job_types import JobState, JobType, JobPriority, BackoffStrategy, ErrorCategory
from ..core.job_schema import (
    Job, JobIdentity, JobDefinition, JobCheckpoint,
    JobEvent, JobProgress, JobError, RetryPolicy, TimeoutPolicy
)

class JobStore:
    """
    JobStore with dual mode: In-Memory cache and Disk-Backed Atomic Persistence.
    Survives process termination and crashes.
    """
    def __init__(self, storage_dir: Optional[str] = None):
        self.storage_dir = storage_dir
        self._jobs: Dict[str, Job] = {}
        self._checkpoints: Dict[str, List[JobCheckpoint]] = {}
        self._events: Dict[str, List[JobEvent]] = {}

        if self.storage_dir:
            os.makedirs(self.storage_dir, exist_ok=True)
            self._load_from_disk()

    def _get_job_file(self, job_id: str) -> str:
        return os.path.join(self.storage_dir, f"{job_id}.json")

    def _serialize_job(self, job: Job) -> Dict[str, Any]:
        return {
            "identity": {
                "job_id": job.identity.job_id,
                "asset_id": job.identity.asset_id,
                "semantic_id": job.identity.semantic_id,
                "project_id": job.identity.project_id,
                "request_id": job.identity.request_id
            },
            "definition": {
                "job_type": job.definition.job_type.value,
                "input_params": job.definition.input_params,
                "priority": job.definition.priority.value,
                "retry_policy": {
                    "max_attempts": job.definition.retry_policy.max_attempts,
                    "backoff_strategy": job.definition.retry_policy.backoff_strategy.value,
                    "base_delay_sec": job.definition.retry_policy.base_delay_sec,
                    "max_delay_sec": job.definition.retry_policy.max_delay_sec
                },
                "timeout_policy": {
                    "job_timeout_sec": job.definition.timeout_policy.job_timeout_sec,
                    "phase_timeout_sec": job.definition.timeout_policy.phase_timeout_sec,
                    "step_timeout_sec": job.definition.timeout_policy.step_timeout_sec
                }
            },
            "state": job.state.value,
            "state_version": job.state_version,
            "progress": {
                "overall_percent": job.progress.overall_percent,
                "current_phase": job.progress.current_phase,
                "current_step": job.progress.current_step,
                "completed_steps": job.progress.completed_steps,
                "total_steps": job.progress.total_steps,
                "eta_seconds": job.progress.eta_seconds
            },
            "current_phase": job.current_phase,
            "current_step": job.current_step,
            "checkpoint_id": job.checkpoint_id,
            "attempt": job.attempt,
            "worker_id": job.worker_id,
            "lease_id": job.lease_id,
            "last_heartbeat": job.last_heartbeat,
            "created_at": job.created_at,
            "updated_at": job.updated_at,
            "completed_at": job.completed_at,
            "checkpoints": [
                {
                    "checkpoint_id": c.checkpoint_id,
                    "job_id": c.job_id,
                    "phase": c.phase,
                    "step": c.step,
                    "state_hash": c.state_hash,
                    "input_hash": c.input_hash,
                    "output_hash": c.output_hash,
                    "previous_checkpoint_id": c.previous_checkpoint_id,
                    "created_at": c.created_at
                }
                for c in self._checkpoints.get(job.identity.job_id, [])
            ],
            "events": [
                {
                    "event_id": e.event_id,
                    "job_id": e.job_id,
                    "event_type": e.event_type,
                    "state": e.state.value,
                    "timestamp": e.timestamp,
                    "payload": e.payload
                }
                for e in self._events.get(job.identity.job_id, [])
            ]
        }

    def _deserialize_job(self, data: Dict[str, Any]) -> Job:
        ident_data = data["identity"]
        identity = JobIdentity(
            job_id=ident_data["job_id"],
            asset_id=ident_data["asset_id"],
            semantic_id=ident_data["semantic_id"],
            project_id=ident_data.get("project_id", "DEFAULT_PROJECT"),
            request_id=ident_data.get("request_id", "REQ_001")
        )
        def_data = data["definition"]
        rp_data = def_data.get("retry_policy", {})
        retry_policy = RetryPolicy(
            max_attempts=rp_data.get("max_attempts", 3),
            backoff_strategy=BackoffStrategy(rp_data.get("backoff_strategy", "EXPONENTIAL")),
            base_delay_sec=rp_data.get("base_delay_sec", 1.0),
            max_delay_sec=rp_data.get("max_delay_sec", 30.0)
        )
        tp_data = def_data.get("timeout_policy", {})
        timeout_policy = TimeoutPolicy(
            job_timeout_sec=tp_data.get("job_timeout_sec", 3600.0),
            phase_timeout_sec=tp_data.get("phase_timeout_sec", 600.0),
            step_timeout_sec=tp_data.get("step_timeout_sec", 120.0)
        )
        definition = JobDefinition(
            job_type=JobType(def_data["job_type"]),
            input_params=def_data.get("input_params", {}),
            priority=JobPriority(def_data.get("priority", "NORMAL")),
            retry_policy=retry_policy,
            timeout_policy=timeout_policy
        )
        prog_data = data.get("progress", {})
        progress = JobProgress(
            overall_percent=prog_data.get("overall_percent", 0.0),
            current_phase=prog_data.get("current_phase", "INIT"),
            current_step=prog_data.get("current_step", "STEP_0"),
            completed_steps=prog_data.get("completed_steps", 0),
            total_steps=prog_data.get("total_steps", 10),
            eta_seconds=prog_data.get("eta_seconds")
        )
        job = Job(
            identity=identity,
            definition=definition,
            state=JobState(data["state"]),
            state_version=data.get("state_version", 1),
            progress=progress,
            current_phase=data.get("current_phase", "NONE"),
            current_step=data.get("current_step", "NONE"),
            checkpoint_id=data.get("checkpoint_id"),
            attempt=data.get("attempt", 1),
            worker_id=data.get("worker_id"),
            lease_id=data.get("lease_id"),
            last_heartbeat=data.get("last_heartbeat", 0.0),
            created_at=data.get("created_at", 0.0),
            updated_at=data.get("updated_at", 0.0),
            completed_at=data.get("completed_at")
        )

        # Reconstruct checkpoints
        ckpts = []
        for c in data.get("checkpoints", []):
            ckpts.append(JobCheckpoint(
                checkpoint_id=c["checkpoint_id"],
                job_id=c["job_id"],
                phase=c["phase"],
                step=c["step"],
                state_hash=c["state_hash"],
                input_hash=c.get("input_hash", ""),
                output_hash=c.get("output_hash", ""),
                previous_checkpoint_id=c.get("previous_checkpoint_id"),
                created_at=c.get("created_at", 0.0)
            ))
        self._checkpoints[job.identity.job_id] = ckpts

        # Reconstruct events
        evts = []
        for e in data.get("events", []):
            evts.append(JobEvent(
                event_id=e["event_id"],
                job_id=e["job_id"],
                event_type=e["event_type"],
                state=JobState(e["state"]),
                timestamp=e.get("timestamp", 0.0),
                payload=e.get("payload", {})
            ))
        self._events[job.identity.job_id] = evts

        return job

    def _persist_job_to_disk(self, job: Job):
        if not self.storage_dir:
            return
        filepath = self._get_job_file(job.identity.job_id)
        temp_filepath = filepath + ".tmp"
        data = self._serialize_job(job)
        with open(temp_filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        if os.path.exists(filepath):
            os.replace(temp_filepath, filepath)
        else:
            os.rename(temp_filepath, filepath)

    def _load_from_disk(self):
        if not self.storage_dir or not os.path.exists(self.storage_dir):
            return
        for fname in os.listdir(self.storage_dir):
            if fname.endswith(".json") and not fname.endswith(".tmp"):
                filepath = os.path.join(self.storage_dir, fname)
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    job = self._deserialize_job(data)
                    self._jobs[job.identity.job_id] = job
                except Exception:
                    pass

    def save_job(self, job: Job):
        job.updated_at = time.time()
        job.state_version += 1
        self._jobs[job.identity.job_id] = job
        self._persist_job_to_disk(job)

    def get_job(self, job_id: str) -> Optional[Job]:
        return self._jobs.get(job_id)

    def list_jobs(self, state: Optional[JobState] = None) -> List[Job]:
        if state:
            return [j for j in self._jobs.values() if j.state == state]
        return list(self._jobs.values())

    def save_checkpoint(self, checkpoint: JobCheckpoint):
        if checkpoint.job_id not in self._checkpoints:
            self._checkpoints[checkpoint.job_id] = []
        self._checkpoints[checkpoint.job_id].append(checkpoint)
        job = self._jobs.get(checkpoint.job_id)
        if job:
            self._persist_job_to_disk(job)

    def get_latest_checkpoint(self, job_id: str) -> Optional[JobCheckpoint]:
        ckpts = self._checkpoints.get(job_id, [])
        return ckpts[-1] if ckpts else None

    def get_all_checkpoints(self, job_id: str) -> List[JobCheckpoint]:
        return self._checkpoints.get(job_id, [])

    def record_event(self, event: JobEvent):
        if event.job_id not in self._events:
            self._events[event.job_id] = []
        self._events[event.job_id].append(event)
        job = self._jobs.get(event.job_id)
        if job:
            self._persist_job_to_disk(job)

    def get_events(self, job_id: str) -> List[JobEvent]:
        return self._events.get(job_id, [])
