from typing import Dict, Any, List, Optional, Tuple
from ..core.control_types import (
    TaskState, AgentRole, ToolEffect, LockType, DecisionAction, ApprovalStatus
)
from ..core.control_schema import (
    Task, AgentDefinition, ToolDefinition, AgentResult,
    ResourceLock, ExecutionTrace, ControlPlan
)
from ..engine.control_plane import ControlPlane
from ..registry.tool_guard import ToolGuard

class ControlPlaneAPI:
    """
    Multi-Agent Orchestration & Antigravity Control Plane API (AOE v49)
    
    Regla Fundamental:
    ANTIGRAVITY NO ES EL AGENTE QUE HACE TODO. ES EL DIRECTOR QUE DECIDE QUÉ DEBE OCURRIR.
    EL CONTROL PLANE ASIGNA TAREAS A LOS 8 AGENTES ESPECIALIZADOS,
    ADMINISTRA LOCKS DE RECURSOS, DETECTA RENDIMIENTOS DECRECIENTES, RECONCILIA ESTADOS TRAS TIMEOUTS
    Y SALVAGUARDA LA CALIDAD SIN REINICIAR PROCESOS DESDE CERO.
    """
    def __init__(self, max_mcp_calls: int = 30):
        self.control_plane = ControlPlane(max_mcp_calls=max_mcp_calls)

    def plan_user_intent(self, intent: str) -> ControlPlan:
        return self.control_plane.compile_intent_to_plan(intent)

    def acquire_resource_lock(self, lock_type: LockType, resource_id: str, owner_task_id: str) -> ResourceLock:
        return self.control_plane.lock_mgr.acquire_lock(lock_type, resource_id, owner_task_id)

    def release_resource_lock(self, lock_type: LockType, resource_id: str, owner_task_id: str) -> bool:
        return self.control_plane.lock_mgr.release_lock(lock_type, resource_id, owner_task_id)

    def evaluate_critic_action(
        self,
        task_id: str,
        current_score: float,
        score_history: List[float]
    ) -> Tuple[DecisionAction, str]:
        return self.control_plane.execute_critic_evaluation(task_id, current_score, score_history)

    def reconcile_mcp_timeout(
        self,
        task_id: str,
        expected_object_name: str,
        scene_objects: List[str]
    ) -> Dict[str, Any]:
        return self.control_plane.handle_mcp_timeout_reconciliation(task_id, expected_object_name, scene_objects)

    def execute_task(self, task: Task, requested_mcp_calls: int) -> AgentResult:
        return self.control_plane.execute_with_budget(task, requested_mcp_calls)

    def validate_agent_output(self, result: AgentResult) -> bool:
        return ToolGuard.validate_agent_result(result)

    def salvage_partial_failure(
        self,
        task_id: str,
        artifacts_status: Dict[str, bool]
    ) -> Dict[str, Any]:
        return self.control_plane.salvage_partial_outputs(task_id, artifacts_status)
