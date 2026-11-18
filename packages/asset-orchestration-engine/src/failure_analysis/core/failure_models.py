import time
import json
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from .failure_types import FailureType, FailureSeverity, FailureStatus

@dataclass
class FailureRecord:
    failure_id: str
    semantic_id: str
    message: str
    job_id: Optional[str] = None
    agent_id: str = "agent.visual.critic"
    contract_id: str = "contract.critic.v2"
    asset_id: Optional[str] = None
    timestamp: float = field(default_factory=time.time)
    pipeline_phase: str = "PHASE_77"
    pipeline_stage: str = "EXECUTION"
    operation: str = "GENERATE_ASSET"
    failure_type: FailureType = FailureType.UNKNOWN_ERROR
    failure_category: str = "GENERAL"
    severity: FailureSeverity = FailureSeverity.ERROR
    status: FailureStatus = FailureStatus.DETECTED
    retryable: bool = True
    recoverable: bool = True
    requires_human: bool = False
    confidence: float = 1.0
    exception_type: str = "Exception"
    exception_message: str = ""
    stack_trace: str = ""
    input_snapshot: Dict[str, Any] = field(default_factory=dict)
    expected_state: Dict[str, Any] = field(default_factory=dict)
    actual_state: Dict[str, Any] = field(default_factory=dict)
    changed_objects: List[str] = field(default_factory=list)
    affected_resources: List[str] = field(default_factory=list)
    affected_files: List[str] = field(default_factory=list)
    affected_assets: List[str] = field(default_factory=list)
    checkpoint_id: Optional[str] = None
    previous_checkpoint_id: Optional[str] = None
    environment_snapshot: Dict[str, Any] = field(default_factory=dict)
    blender_version: str = "4.2.0"
    engine_version: str = "5.4.0"
    capability: str = "CAP_GEOMETRY"
    tool: str = "BlenderTool"
    governance_decision: str = "ALLOWED"
    evidence: List[Dict[str, Any]] = field(default_factory=list)
    probable_root_cause: str = ""
    alternative_causes: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    recommended_action: str = "RETRY"
    correction_plan: Dict[str, Any] = field(default_factory=dict)
    recovery_plan: Dict[str, Any] = field(default_factory=dict)
    attempt_number: int = 1
    previous_attempts: List[Dict[str, Any]] = field(default_factory=list)
    correction_id: Optional[str] = None
    parent_failure_id: Optional[str] = None
    related_failure_ids: List[str] = field(default_factory=list)
    regression_risk: str = "LOW"
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    resolved_at: Optional[float] = None
    resolution: str = "UNRESOLVED"
    resolution_evidence: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "failure_id": self.failure_id,
            "job_id": self.job_id,
            "agent_id": self.agent_id,
            "contract_id": self.contract_id,
            "semantic_id": self.semantic_id,
            "asset_id": self.asset_id,
            "timestamp": self.timestamp,
            "pipeline_phase": self.pipeline_phase,
            "pipeline_stage": self.pipeline_stage,
            "operation": self.operation,
            "failure_type": self.failure_type.value,
            "failure_category": self.failure_category,
            "severity": self.severity.value,
            "status": self.status.value,
            "retryable": self.retryable,
            "recoverable": self.recoverable,
            "requires_human": self.requires_human,
            "confidence": round(self.confidence, 4),
            "message": self.message,
            "exception_type": self.exception_type,
            "exception_message": self.exception_message,
            "stack_trace": self.stack_trace,
            "input_snapshot": self.input_snapshot,
            "expected_state": self.expected_state,
            "actual_state": self.actual_state,
            "changed_objects": self.changed_objects,
            "affected_resources": self.affected_resources,
            "affected_files": self.affected_files,
            "affected_assets": self.affected_assets,
            "checkpoint_id": self.checkpoint_id,
            "previous_checkpoint_id": self.previous_checkpoint_id,
            "environment_snapshot": self.environment_snapshot,
            "blender_version": self.blender_version,
            "engine_version": self.engine_version,
            "capability": self.capability,
            "tool": self.tool,
            "governance_decision": self.governance_decision,
            "evidence": self.evidence,
            "probable_root_cause": self.probable_root_cause,
            "alternative_causes": self.alternative_causes,
            "dependencies": self.dependencies,
            "recommended_action": self.recommended_action,
            "correction_plan": self.correction_plan,
            "recovery_plan": self.recovery_plan,
            "attempt_number": self.attempt_number,
            "previous_attempts": self.previous_attempts,
            "correction_id": self.correction_id,
            "parent_failure_id": self.parent_failure_id,
            "related_failure_ids": self.related_failure_ids,
            "regression_risk": self.regression_risk,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "resolved_at": self.resolved_at,
            "resolution": self.resolution,
            "resolution_evidence": self.resolution_evidence
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "FailureRecord":
        return cls(
            failure_id=data["failure_id"],
            job_id=data.get("job_id"),
            agent_id=data.get("agent_id", "agent.visual.critic"),
            contract_id=data.get("contract_id", "contract.critic.v2"),
            semantic_id=data.get("semantic_id", "asset.default"),
            asset_id=data.get("asset_id"),
            timestamp=data.get("timestamp", time.time()),
            pipeline_phase=data.get("pipeline_phase", "PHASE_77"),
            pipeline_stage=data.get("pipeline_stage", "EXECUTION"),
            operation=data.get("operation", "GENERATE_ASSET"),
            failure_type=FailureType(data.get("failure_type", "UNKNOWN_ERROR")),
            failure_category=data.get("failure_category", "GENERAL"),
            severity=FailureSeverity(data.get("severity", "ERROR")),
            status=FailureStatus(data.get("status", "DETECTED")),
            retryable=data.get("retryable", True),
            recoverable=data.get("recoverable", True),
            requires_human=data.get("requires_human", False),
            confidence=data.get("confidence", 1.0),
            message=data.get("message", ""),
            exception_type=data.get("exception_type", "Exception"),
            exception_message=data.get("exception_message", ""),
            stack_trace=data.get("stack_trace", ""),
            input_snapshot=data.get("input_snapshot", {}),
            expected_state=data.get("expected_state", {}),
            actual_state=data.get("actual_state", {}),
            changed_objects=data.get("changed_objects", []),
            affected_resources=data.get("affected_resources", []),
            affected_files=data.get("affected_files", []),
            affected_assets=data.get("affected_assets", []),
            checkpoint_id=data.get("checkpoint_id"),
            previous_checkpoint_id=data.get("previous_checkpoint_id"),
            environment_snapshot=data.get("environment_snapshot", {}),
            blender_version=data.get("blender_version", "4.2.0"),
            engine_version=data.get("engine_version", "5.4.0"),
            capability=data.get("capability", "CAP_GEOMETRY"),
            tool=data.get("tool", "BlenderTool"),
            governance_decision=data.get("governance_decision", "ALLOWED"),
            evidence=data.get("evidence", []),
            probable_root_cause=data.get("probable_root_cause", ""),
            alternative_causes=data.get("alternative_causes", []),
            dependencies=data.get("dependencies", []),
            recommended_action=data.get("recommended_action", "RETRY"),
            correction_plan=data.get("correction_plan", {}),
            recovery_plan=data.get("recovery_plan", {}),
            attempt_number=data.get("attempt_number", 1),
            previous_attempts=data.get("previous_attempts", []),
            correction_id=data.get("correction_id"),
            parent_failure_id=data.get("parent_failure_id"),
            related_failure_ids=data.get("related_failure_ids", []),
            regression_risk=data.get("regression_risk", "LOW"),
            created_at=data.get("created_at", time.time()),
            updated_at=data.get("updated_at", time.time()),
            resolved_at=data.get("resolved_at"),
            resolution=data.get("resolution", "UNRESOLVED"),
            resolution_evidence=data.get("resolution_evidence", {})
        )
