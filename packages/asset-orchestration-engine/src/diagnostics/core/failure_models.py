import time
import hashlib
import json
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from .failure_types import FailureStatus, FailureType
from .severity import FailureSeverity

@dataclass
class FailureRecord:
    failure_id: str
    semantic_id: str
    message: str
    job_id: Optional[str] = None
    asset_id: Optional[str] = None
    timestamp: float = field(default_factory=time.time)
    phase: str = "PHASE_77"
    stage: str = "EXECUTION"
    agent_id: str = "agent.visual.critic"
    operation: str = "GENERATE_ASSET"
    failure_type: FailureType = FailureType.UNKNOWN
    severity: FailureSeverity = FailureSeverity.ERROR
    error_code: str = "ERR_UNKNOWN"
    normalized_message: str = ""
    exception_type: str = "Exception"
    stack_trace: str = ""
    tool: str = "BlenderTool"
    capability: str = "CAP_GEOMETRY"
    resource: str = "weapon_vandal"
    checkpoint_id: Optional[str] = None
    state_before: Dict[str, Any] = field(default_factory=dict)
    state_after: Dict[str, Any] = field(default_factory=dict)
    environment: Dict[str, Any] = field(default_factory=dict)
    evidence_ids: List[str] = field(default_factory=list)
    parent_failure_id: Optional[str] = None
    correlation_id: str = field(default_factory=lambda: hashlib.sha256(str(time.time()).encode("utf-8")).hexdigest()[:12])
    retry_count: int = 0
    recoverable: bool = True
    status: FailureStatus = FailureStatus.DETECTED

    def to_dict(self) -> Dict[str, Any]:
        return {
            "failure_id": self.failure_id,
            "job_id": self.job_id,
            "semantic_id": self.semantic_id,
            "asset_id": self.asset_id,
            "timestamp": self.timestamp,
            "phase": self.phase,
            "stage": self.stage,
            "agent_id": self.agent_id,
            "operation": self.operation,
            "failure_type": self.failure_type.value,
            "severity": self.severity.value,
            "error_code": self.error_code,
            "message": self.message,
            "normalized_message": self.normalized_message,
            "exception_type": self.exception_type,
            "stack_trace": self.stack_trace,
            "tool": self.tool,
            "capability": self.capability,
            "resource": self.resource,
            "checkpoint_id": self.checkpoint_id,
            "state_before": self.state_before,
            "state_after": self.state_after,
            "environment": self.environment,
            "evidence_ids": self.evidence_ids,
            "parent_failure_id": self.parent_failure_id,
            "correlation_id": self.correlation_id,
            "retry_count": self.retry_count,
            "recoverable": self.recoverable,
            "status": self.status.value
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "FailureRecord":
        return cls(
            failure_id=data["failure_id"],
            job_id=data.get("job_id"),
            semantic_id=data.get("semantic_id", "asset.default"),
            asset_id=data.get("asset_id"),
            timestamp=data.get("timestamp", time.time()),
            phase=data.get("phase", "PHASE_77"),
            stage=data.get("stage", "EXECUTION"),
            agent_id=data.get("agent_id", "agent.visual.critic"),
            operation=data.get("operation", "GENERATE_ASSET"),
            failure_type=FailureType(data.get("failure_type", "UNKNOWN")),
            severity=FailureSeverity(data.get("severity", "ERROR")),
            error_code=data.get("error_code", "ERR_UNKNOWN"),
            message=data.get("message", ""),
            normalized_message=data.get("normalized_message", ""),
            exception_type=data.get("exception_type", "Exception"),
            stack_trace=data.get("stack_trace", ""),
            tool=data.get("tool", "BlenderTool"),
            capability=data.get("capability", "CAP_GEOMETRY"),
            resource=data.get("resource", "weapon_vandal"),
            checkpoint_id=data.get("checkpoint_id"),
            state_before=data.get("state_before", {}),
            state_after=data.get("state_after", {}),
            environment=data.get("environment", {}),
            evidence_ids=data.get("evidence_ids", []),
            parent_failure_id=data.get("parent_failure_id"),
            correlation_id=data.get("correlation_id", "corr_default"),
            retry_count=data.get("retry_count", 0),
            recoverable=data.get("recoverable", True),
            status=FailureStatus(data.get("status", "DETECTED"))
        )
