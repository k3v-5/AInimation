from typing import Dict, Any, List, Optional
from ..planning.planner import ExecutionPlan
from ..core.scene_graph import SceneGraph

class PlanValidator:
    @staticmethod
    def validate_plan(plan: ExecutionPlan, graph: Optional[SceneGraph] = None) -> Dict[str, Any]:
        errors: List[str] = []
        warnings: List[str] = []

        if plan.error_message:
            errors.append(plan.error_message)

        if plan.budget_exceeded:
            errors.append("Plan exceeds allocated Change Budget.")

        if not plan.operations and not plan.error_message:
            warnings.append("Plan contains zero operations.")

        # Verificar que cada operación tiene ID y target
        for op in plan.operations:
            if not op.operation_id:
                errors.append("Operation is missing unique operation_id.")
            if not op.target_id:
                errors.append("Operation is missing target_id.")

        return {
            "task_id": plan.task_id,
            "asset_id": plan.asset_id,
            "is_valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "operations_count": len(plan.operations)
        }
