import time
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from enum import Enum

class JobStatus(str, Enum):
    CREATED = "CREATED"
    PLANNED = "PLANNED"
    QUEUED = "QUEUED"
    RUNNING = "RUNNING"
    WAITING = "WAITING"
    EVALUATING = "EVALUATING"
    CORRECTING = "CORRECTING"
    OPTIMIZING = "OPTIMIZING"
    REGRESSION_CHECK = "REGRESSION_CHECK"
    PACKAGING = "PACKAGING"
    DELIVERING = "DELIVERING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"
    PAUSED = "PAUSED"
    RECOVERING = "RECOVERING"
    REJECTED = "REJECTED"

@dataclass
class ProductionJob:
    job_id: str
    project_id: str = "DarX"
    request_id: str = ""
    asset_semantic_id: str = ""
    asset_type: str = "WEAPON"
    input_specification: Dict[str, Any] = field(default_factory=dict)
    reference_set: List[str] = field(default_factory=list)
    strategy: Dict[str, Any] = field(default_factory=dict)
    pipeline_plan: Dict[str, Any] = field(default_factory=dict)
    priority: str = "NORMAL"
    budget: Dict[str, Any] = field(default_factory=lambda: {
        "max_execution_time": 180.0,
        "max_blender_runs": 5,
        "max_correction_iterations": 3,
        "max_memory_mb": 512.0
    })
    performance_budget: Dict[str, Any] = field(default_factory=dict)
    quality_threshold: float = 0.90
    current_stage: str = "REQUEST_INGESTION"
    current_agent: str = "agent.orchestrator"
    status: JobStatus = JobStatus.CREATED
    attempt: int = 1
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    deadline: Optional[float] = None
    parent_job_id: Optional[str] = None
    checkpoint_id: Optional[str] = None
    evaluation_id: Optional[str] = None
    benchmark_id: Optional[str] = None
    regression_baseline_id: Optional[str] = None
    package_id: Optional[str] = None
    delivery_id: Optional[str] = None
    failure_state: Optional[Dict[str, Any]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "job_id": self.job_id,
            "project_id": self.project_id,
            "request_id": self.request_id,
            "asset_semantic_id": self.asset_semantic_id,
            "asset_type": self.asset_type,
            "input_specification": self.input_specification,
            "reference_set": self.reference_set,
            "strategy": self.strategy,
            "pipeline_plan": self.pipeline_plan,
            "priority": self.priority,
            "budget": self.budget,
            "performance_budget": self.performance_budget,
            "quality_threshold": round(self.quality_threshold, 4),
            "current_stage": self.current_stage,
            "current_agent": self.current_agent,
            "status": self.status.value,
            "attempt": self.attempt,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "deadline": self.deadline,
            "parent_job_id": self.parent_job_id,
            "checkpoint_id": self.checkpoint_id,
            "evaluation_id": self.evaluation_id,
            "benchmark_id": self.benchmark_id,
            "regression_baseline_id": self.regression_baseline_id,
            "package_id": self.package_id,
            "delivery_id": self.delivery_id,
            "failure_state": self.failure_state,
            "metadata": self.metadata
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ProductionJob":
        return cls(
            job_id=data["job_id"],
            project_id=data.get("project_id", "DarX"),
            request_id=data.get("request_id", ""),
            asset_semantic_id=data.get("asset_semantic_id", ""),
            asset_type=data.get("asset_type", "WEAPON"),
            input_specification=data.get("input_specification", {}),
            reference_set=data.get("reference_set", []),
            strategy=data.get("strategy", {}),
            pipeline_plan=data.get("pipeline_plan", {}),
            priority=data.get("priority", "NORMAL"),
            budget=data.get("budget", {}),
            performance_budget=data.get("performance_budget", {}),
            quality_threshold=data.get("quality_threshold", 0.90),
            current_stage=data.get("current_stage", "REQUEST_INGESTION"),
            current_agent=data.get("current_agent", "agent.orchestrator"),
            status=JobStatus(data.get("status", "CREATED")),
            attempt=data.get("attempt", 1),
            created_at=data.get("created_at", time.time()),
            updated_at=data.get("updated_at", time.time()),
            deadline=data.get("deadline"),
            parent_job_id=data.get("parent_job_id"),
            checkpoint_id=data.get("checkpoint_id"),
            evaluation_id=data.get("evaluation_id"),
            benchmark_id=data.get("benchmark_id"),
            regression_baseline_id=data.get("regression_baseline_id"),
            package_id=data.get("package_id"),
            delivery_id=data.get("delivery_id"),
            failure_state=data.get("failure_state"),
            metadata=data.get("metadata", {})
        )
