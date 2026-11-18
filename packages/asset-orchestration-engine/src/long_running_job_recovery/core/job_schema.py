from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from .job_types import (
    JobType, JobState, JobPriority, BackoffStrategy,
    ErrorCategory, RecoveryAction
)

@dataclass
class JobIdentity:
    job_id: str
    asset_id: str
    semantic_id: str
    project_id: str = "DEFAULT_PROJECT"
    request_id: str = "REQ_001"

@dataclass
class RetryPolicy:
    max_attempts: int = 3
    backoff_strategy: BackoffStrategy = BackoffStrategy.EXPONENTIAL
    base_delay_sec: float = 1.0
    max_delay_sec: float = 30.0

@dataclass
class TimeoutPolicy:
    job_timeout_sec: float = 3600.0
    phase_timeout_sec: float = 600.0
    step_timeout_sec: float = 120.0

@dataclass
class JobDefinition:
    job_type: JobType
    input_params: Dict[str, Any] = field(default_factory=dict)
    priority: JobPriority = JobPriority.NORMAL
    retry_policy: RetryPolicy = field(default_factory=RetryPolicy)
    timeout_policy: TimeoutPolicy = field(default_factory=TimeoutPolicy)

@dataclass
class JobProgress:
    overall_percent: float = 0.0
    current_phase: str = "INITIALIZING"
    current_step: str = "STEP_0"
    completed_steps: int = 0
    total_steps: int = 10
    eta_seconds: Optional[float] = None

@dataclass
class JobCheckpoint:
    checkpoint_id: str
    job_id: str
    phase: str
    step: str
    state_hash: str
    input_hash: str
    output_hash: str
    previous_checkpoint_id: Optional[str] = None
    created_at: float = 0.0

@dataclass
class JobError:
    error_id: str
    error_type: str
    category: ErrorCategory
    message: str
    phase: str
    step: str
    recoverable: bool = True
    timestamp: float = 0.0

@dataclass
class JobEvent:
    event_id: str
    job_id: str
    event_type: str
    state: JobState
    timestamp: float
    payload: Dict[str, Any] = field(default_factory=dict)

@dataclass
class WorkerIdentity:
    worker_id: str
    process_id: int
    host_id: str
    started_at: float

@dataclass
class Job:
    identity: JobIdentity
    definition: JobDefinition
    state: JobState = JobState.CREATED
    state_version: int = 1
    progress: JobProgress = field(default_factory=JobProgress)
    current_phase: str = "NONE"
    current_step: str = "NONE"
    checkpoint_id: Optional[str] = None
    attempt: int = 1
    worker_id: Optional[str] = None
    lease_id: Optional[str] = None
    last_heartbeat: float = 0.0
    errors: List[JobError] = field(default_factory=list)
    created_at: float = 0.0
    updated_at: float = 0.0
    completed_at: Optional[float] = None

@dataclass
class RecoveryReport:
    job_id: str
    previous_state: JobState
    failure_reason: str
    checkpoint_used: Optional[str]
    action_taken: RecoveryAction
    final_state: JobState
    recovered: bool

@dataclass
class RecoverableJob:
    job_id: str
    asset_id: str
    semantic_id: str
    job_type: JobType
    state: JobState
    current_phase: str
    progress: JobProgress
    checkpoint_id: Optional[str]
    checkpoint_hash: str
    attempt: int
    last_heartbeat: float
    errors: List[JobError] = field(default_factory=list)
    recovery_history: List[RecoveryReport] = field(default_factory=list)

@dataclass
class JobValidationResult:
    is_valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
