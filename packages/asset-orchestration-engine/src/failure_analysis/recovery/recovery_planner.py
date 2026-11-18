import time
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from ..core.failure_types import RecoveryActionType

@dataclass
class RecoveryPlan:
    plan_id: str
    failure_id: str
    semantic_id: str
    action: RecoveryActionType
    scope: str = "COMPONENT"
    checkpoint_id: Optional[str] = None
    rollback_required: bool = False
    retry_required: bool = True
    regeneration_required: bool = False
    affected_objects: List[str] = field(default_factory=list)
    affected_files: List[str] = field(default_factory=list)
    risk: str = "LOW"
    expected_result: str = "RESTORE_VALID_STATE"
    verification_method: str = "F75_BENCHMARK"
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "plan_id": self.plan_id,
            "failure_id": self.failure_id,
            "semantic_id": self.semantic_id,
            "action": self.action.value,
            "scope": self.scope,
            "checkpoint_id": self.checkpoint_id,
            "rollback_required": self.rollback_required,
            "retry_required": self.retry_required,
            "regeneration_required": self.regeneration_required,
            "affected_objects": self.affected_objects,
            "affected_files": self.affected_files,
            "risk": self.risk,
            "expected_result": self.expected_result,
            "verification_method": self.verification_method,
            "timestamp": self.timestamp
        }

class RecoveryPlanner:
    """Plans recovery actions enforcing minimal regeneration boundaries."""

    @staticmethod
    def plan(failure_id: str, semantic_id: str, action_type: RecoveryActionType, checkpoint_id: Optional[str] = None) -> RecoveryPlan:
        return RecoveryPlan(
            plan_id=f"REC_PLAN_{int(time.time()*1000)}_{semantic_id.replace('.', '_')}",
            failure_id=failure_id,
            semantic_id=semantic_id,
            action=action_type,
            checkpoint_id=checkpoint_id,
            rollback_required=(action_type == RecoveryActionType.ROLLBACK),
            retry_required=(action_type in (RecoveryActionType.RETRY, RecoveryActionType.RESUME)),
            regeneration_required=(action_type in (
                RecoveryActionType.REGENERATE_COMPONENT,
                RecoveryActionType.REGENERATE_SUBTREE,
                RecoveryActionType.REGENERATE_ASSET,
                RecoveryActionType.REBUILD_MATERIAL,
                RecoveryActionType.REBUILD_UV,
                RecoveryActionType.REBUILD_LODS,
                RecoveryActionType.REBUILD_COLLISION
            ))
        )
