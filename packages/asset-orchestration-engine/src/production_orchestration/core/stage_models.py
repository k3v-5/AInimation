import time
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from enum import Enum

class PipelineStage(str, Enum):
    REQUEST_INGESTION = "REQUEST_INGESTION"
    REQUIREMENT_COMPILATION = "REQUIREMENT_COMPILATION"
    REFERENCE_ANALYSIS = "REFERENCE_ANALYSIS"
    STRATEGY_SELECTION = "STRATEGY_SELECTION"
    RESOURCE_PLANNING = "RESOURCE_PLANNING"
    AGENT_ASSIGNMENT = "AGENT_ASSIGNMENT"
    ASSET_GENERATION = "ASSET_GENERATION"
    BLENDER_EXECUTION = "BLENDER_EXECUTION"
    STRUCTURAL_VALIDATION = "STRUCTURAL_VALIDATION"
    VISUAL_EVALUATION = "VISUAL_EVALUATION"
    QUALITY_EVALUATION = "QUALITY_EVALUATION"
    FAILURE_ANALYSIS = "FAILURE_ANALYSIS"
    CORRECTION = "CORRECTION"
    OPTIMIZATION = "OPTIMIZATION"
    REGRESSION_CHECK = "REGRESSION_CHECK"
    ACCEPTANCE = "ACCEPTANCE"
    PACKAGING = "PACKAGING"
    DELIVERY = "DELIVERY"
    FINALIZATION = "FINALIZATION"

class StageStatus(str, Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    SKIPPED = "SKIPPED"
    FAILED = "FAILED"
    RECOVERED = "RECOVERED"

@dataclass
class StageResult:
    stage_id: PipelineStage
    status: StageStatus = StageStatus.PENDING
    input_hash: str = ""
    output_hash: str = ""
    started_at: float = field(default_factory=time.time)
    completed_at: Optional[float] = None
    agent_id: str = "agent.orchestrator"
    capabilities_used: List[str] = field(default_factory=list)
    artifacts_created: List[str] = field(default_factory=list)
    artifacts_modified: List[str] = field(default_factory=list)
    metrics: Dict[str, Any] = field(default_factory=dict)
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    checkpoint_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "stage_id": self.stage_id.value,
            "status": self.status.value,
            "input_hash": self.input_hash,
            "output_hash": self.output_hash,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "agent_id": self.agent_id,
            "capabilities_used": self.capabilities_used,
            "artifacts_created": self.artifacts_created,
            "artifacts_modified": self.artifacts_modified,
            "metrics": self.metrics,
            "warnings": self.warnings,
            "errors": self.errors,
            "checkpoint_id": self.checkpoint_id
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "StageResult":
        return cls(
            stage_id=PipelineStage(data["stage_id"]),
            status=StageStatus(data.get("status", "PENDING")),
            input_hash=data.get("input_hash", ""),
            output_hash=data.get("output_hash", ""),
            started_at=data.get("started_at", time.time()),
            completed_at=data.get("completed_at"),
            agent_id=data.get("agent_id", "agent.orchestrator"),
            capabilities_used=data.get("capabilities_used", []),
            artifacts_created=data.get("artifacts_created", []),
            artifacts_modified=data.get("artifacts_modified", []),
            metrics=data.get("metrics", {}),
            warnings=data.get("warnings", []),
            errors=data.get("errors", []),
            checkpoint_id=data.get("checkpoint_id")
        )
