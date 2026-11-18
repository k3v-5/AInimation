import uuid
from typing import Dict, Any, Optional, List, Tuple
from ..core.request_schema import AIRequest, RequestSource
from ..core.ai_gateway import AIRequestGateway
from ..intent.intent_parser import AdvancedIntentParser, PlanningIntentType
from ..state.gap_analyzer import GapAnalyzer, GoalSpec
from ..tasks.task_graph import TaskGraph, PlannedTask
from ..optimization.plan_optimizer import PlanOptimizer
from ..validation.destructive_guard import DestructiveOperationGuard, RiskLevel
from ..execution.plan_executor import PlanExecutor
from ...unreal.core.unreal_engine import UnrealEngine
from ...gameplay.core.gameplay_engine import GameplayEngine

class AIPlanningAPI:
    """
    AI Planning, Intent Parsing & Task Decomposition API (AOE v9)
    
    Invariante:
    DO NOT CREATE UNTIL YOU HAVE PROVEN THAT REUSE OR MODIFICATION IS NOT SUFFICIENT.
    """
    def __init__(
        self,
        unreal_engine: Optional[UnrealEngine] = None,
        gameplay_engine: Optional[GameplayEngine] = None,
        max_mcp_calls_budget: int = 20
    ):
        self.ue = unreal_engine
        self.gp = gameplay_engine
        self.gateway = AIRequestGateway()
        self.executor = PlanExecutor(unreal_engine, gameplay_engine)
        self.max_mcp_calls_budget = max_mcp_calls_budget

    def process_request(
        self,
        user_text: str,
        context_target: Optional[str] = None,
        request_id: Optional[str] = None,
        scope: Optional[List[str]] = None,
        dry_run: bool = False
    ) -> Dict[str, Any]:
        req_id = request_id or f"req_{uuid.uuid4().hex[:6]}"
        req = AIRequest(request_id=req_id, user_text=user_text)

        # 1. Idempotencia
        is_cached, cached_res = self.gateway.receive_request(req)
        if is_cached:
            return {"success": True, "status": "DUPLICATE_REQUEST", "cached_result": cached_res}

        # 2. Detección de Ambigüedad de Target si hay múltiples coincidencias en escena
        target = context_target
        if not target and self.ue:
            # Buscar si el texto menciona "espada" o "sword"
            if "espada" in user_text.lower() or "sword" in user_text.lower():
                swords = self.ue.scene.registry.find_by_tag("Weapon")
                if len(swords) > 1:
                    return {"success": False, "error_code": "AMBIGUOUS_TARGET", "message": f"Multiple matching targets ({len(swords)}) found in scene without explicit selection."}
                elif len(swords) == 1:
                    target = swords[0].actor_id

        # 3. Parseo de Intención
        intents = AdvancedIntentParser.parse_user_request(user_text, context_target=target)
        if not intents:
            return {"success": False, "error_code": "INTENT_PARSE_FAILED", "message": "No actionable intent recognized."}

        # 4. Construcción del TaskGraph
        raw_tasks: List[PlannedTask] = []
        for idx, intent in enumerate(intents):
            tgt = intent.target_id or target or "unknown_target"
            
            if intent.intent_type == PlanningIntentType.MAKE_PICKABLE:
                raw_tasks.append(PlannedTask(task_id=f"task_{idx}_pick", task_type="ADD_CAPABILITY", target=tgt, parameters={"capability": "PICKUP"}))
            
            elif intent.intent_type == PlanningIntentType.MAKE_EQUIPPABLE:
                raw_tasks.append(PlannedTask(task_id=f"task_{idx}_equip", task_type="ADD_CAPABILITY", target=tgt, parameters={"capability": "EQUIPPABLE"}))
            
            elif intent.intent_type == PlanningIntentType.MODIFY_PROPERTY:
                raw_tasks.append(PlannedTask(task_id=f"task_{idx}_prop", task_type="SET_GAMEPLAY_DATA", target=tgt, parameters=intent.parameters))
            
            elif intent.intent_type == PlanningIntentType.PLACE_ON:
                raw_tasks.append(PlannedTask(task_id=f"task_{idx}_place", task_type="PLACE_ON", target=tgt, parameters=intent.parameters))

            elif intent.intent_type == PlanningIntentType.DELETE:
                raw_tasks.append(PlannedTask(task_id=f"task_{idx}_del", task_type="DELETE_ACTOR", target=tgt, parameters=intent.parameters))

        # 5. Optimización del Plan (Deduplicación & Plegado)
        optimized_tasks = PlanOptimizer.optimize_tasks(raw_tasks)

        # 6. Comprobación de Presupuesto MCP
        if len(optimized_tasks) > self.max_mcp_calls_budget:
            return {"success": False, "error_code": "PLAN_EXCEEDS_BUDGET", "message": f"Plan requires {len(optimized_tasks)} operations, exceeding budget limit of {self.max_mcp_calls_budget}."}

        # 7. Evaluación de Riesgo y Operaciones Destructivas
        for t in optimized_tasks:
            risk = DestructiveOperationGuard.classify_risk(t.task_type, t.parameters.get("scope", "target"))
            if risk == RiskLevel.CRITICAL and not dry_run:
                return {
                    "success": False,
                    "error_code": "CRITICAL_RISK_CONFIRMATION_REQUIRED",
                    "risk_level": "CRITICAL",
                    "message": f"Critical destructive operation '{t.task_type}' requires explicit human confirmation."
                }

        # 8. Comprobación de NO_OP contra el estado actual
        if target and self.gp and len(optimized_tasks) == 1 and optimized_tasks[0].task_type == "SET_GAMEPLAY_DATA":
            prop_name = optimized_tasks[0].parameters.get("property")
            prop_val = optimized_tasks[0].parameters.get("value")
            cur_data = self.gp.actor_data.get(target)
            if cur_data and cur_data.get_effective(prop_name) == prop_val:
                return {"success": True, "status": "NO_OP", "target": target, "mcp_calls": 0}

        # 9. Construir Grafo Final
        graph = TaskGraph()
        for t in optimized_tasks:
            graph.add_task(t)

        # 10. Ejecución
        exec_res = self.executor.execute_plan(graph, dry_run=dry_run)
        
        final_res = {
            "success": exec_res["success"],
            "status": "dry_run" if dry_run else ("COMPLETED" if exec_res["success"] else exec_res.get("error_code")),
            "request_id": req_id,
            "target": target,
            "tasks_count": len(optimized_tasks),
            "mcp_calls": exec_res["mcp_calls"],
            "stop_rule_triggered": exec_res.get("stop_rule_triggered", False),
            "details": exec_res
        }

        if exec_res["success"] and not dry_run:
            self.gateway.store_result(req_id, final_res)

        return final_res
