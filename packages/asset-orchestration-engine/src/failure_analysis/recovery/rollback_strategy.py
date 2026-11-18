from typing import Optional, Dict, Any

class RollbackStrategy:
    """Manages restoration to stable checkpoints upon critical failure or regression."""

    @staticmethod
    def plan_rollback(checkpoint_id: Optional[str], asset_semantic_id: str) -> Dict[str, Any]:
        return {
            "checkpoint_id": checkpoint_id or "CHECKPOINT_INIT",
            "semantic_id": asset_semantic_id,
            "action": "RESTORE_CHECKPOINT",
            "preserve_valid_meshes": True
        }

class InterventionPolicy:
    """Decides if human intervention or operator escalation is required."""

    @staticmethod
    def requires_human_intervention(attempt_count: int, severity: str, is_governance_denied: bool) -> bool:
        if attempt_count >= 3:
            return True
        if severity == "FATAL":
            return True
        if is_governance_denied:
            return True
        return False
