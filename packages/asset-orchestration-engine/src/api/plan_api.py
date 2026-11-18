from typing import Dict, Any, Optional, Union, List
from ..intent.intent_parser import IntentParser
from ..intent.intent_types import NormalizedIntent
from ..planning.plan_generator import PlanGenerator
from ..planning.planner import ExecutionPlan, ChangeBudget
from ..planning.scope_manager import ScopeSpec
from ..validation.plan_validator import PlanValidator
from ..core.state_manager import StateManager
from ..execution.executor import PlanExecutor

class PlanAPI:
    def __init__(self, state_manager: StateManager, plan_generator: PlanGenerator, executor: PlanExecutor):
        self.state_manager = state_manager
        self.plan_generator = plan_generator
        self.executor = executor

    def plan_intent(
        self,
        request: Union[str, Dict[str, Any]],
        active_asset_id: Optional[str] = None,
        scope: Optional[ScopeSpec] = None,
        budget: Optional[ChangeBudget] = None
    ) -> Dict[str, Any]:
        # 1. Parsear Intent
        intent = IntentParser.parse_intent(request, active_asset_id)
        
        # 2. Obtener SceneGraph si existe
        asset_id = intent.asset_id or active_asset_id
        graph = self.state_manager.get_graph(asset_id) if asset_id else None

        # 3. Generar Plan
        plan = self.plan_generator.generate_plan(intent, graph, scope, budget)

        # 4. Validar Plan
        val_report = PlanValidator.validate_plan(plan, graph)

        return {
            "success": val_report["is_valid"],
            "task_id": plan.task_id,
            "asset_id": plan.asset_id,
            "intent": intent.__dict__,
            "plan_valid": val_report["is_valid"],
            "operations_count": len(plan.operations),
            "affected_objects": plan.affected_objects,
            "operations": [op.__dict__ for op in plan.operations],
            "is_no_op": all(op.is_no_op for op in plan.operations) if plan.operations else False,
            "validation_report": val_report,
            "error_message": plan.error_message
        }

    def explain_plan(self, plan_dict_or_plan: Union[Dict[str, Any], ExecutionPlan]) -> Dict[str, Any]:
        """
        Convierte un plan técnico en una explicación estructurada y legible para humanos/IA.
        """
        if isinstance(plan_dict_or_plan, dict):
            task_id = plan_dict_or_plan.get("task_id", "")
            asset_id = plan_dict_or_plan.get("asset_id", "")
            ops = plan_dict_or_plan.get("operations", [])
            affected = plan_dict_or_plan.get("affected_objects", [])
            is_no_op = plan_dict_or_plan.get("is_no_op", False)
        else:
            task_id = plan_dict_or_plan.task_id
            asset_id = plan_dict_or_plan.asset_id
            ops = [op.__dict__ for op in plan_dict_or_plan.operations]
            affected = plan_dict_or_plan.affected_objects
            is_no_op = all(op.is_no_op for op in plan_dict_or_plan.operations) if plan_dict_or_plan.operations else False

        steps_explanation = []
        for i, op in enumerate(ops, 1):
            op_type = op.get("operation_type")
            target = op.get("target_id")
            params = op.get("parameters", {})
            if op.get("is_no_op"):
                steps_explanation.append(f"{i}. NO-OP: Target '{target}' already matches requested parameters.")
            elif op_type == "SET_DIMENSIONS":
                steps_explanation.append(f"{i}. SET_DIMENSION: Set dimensions of '{target}' to {params.get('value')}.")
            elif op_type == "CREATE_COMPONENT":
                steps_explanation.append(f"{i}. CREATE_COMPONENT: Create component '{target}' ({params.get('primitive')}).")
            else:
                steps_explanation.append(f"{i}. {op_type}: Modify '{target}' with {params}.")

        return {
            "task_id": task_id,
            "asset_id": asset_id,
            "summary": f"Plan with {len(ops)} operations affecting {len(affected)} object(s).",
            "is_no_op": is_no_op,
            "destructive_operations_count": 0,
            "steps": steps_explanation
        }
