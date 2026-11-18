import time
from typing import Dict, Any, List, Optional, Tuple
from ..core.control_types import (
    TaskState, AgentRole, DecisionAction, LockType
)
from ..core.control_schema import (
    Task, AgentResult, ControlPlan, ExecutionTrace
)
from ..registry.agent_registry import AgentRegistry
from ..registry.tool_guard import ToolGuard
from ..scheduler.resource_lock_manager import ResourceLockManager
from ..scheduler.task_scheduler import TaskScheduler

class ControlPlane:
    def __init__(self, max_mcp_calls: int = 30):
        self.max_mcp_calls = max_mcp_calls
        self.registry = AgentRegistry()
        self.lock_mgr = ResourceLockManager()
        self.scheduler = TaskScheduler()
        self.traces: List[ExecutionTrace] = []
        self.total_mcp_calls: int = 0

    def compile_intent_to_plan(self, user_intent: str) -> ControlPlan:
        # Standard Agent Pipeline
        pipeline = [
            AgentRole.SPECIFICATION,
            AgentRole.DEPENDENCY,
            AgentRole.BLENDER,
            AgentRole.VALIDATION,
            AgentRole.CRITIC,
            AgentRole.UNREAL,
            AgentRole.VALIDATION
        ]
        subtasks = [
            Task(task_id=f"TASK_{role.value}", intent=f"Execute {role.value} stage for: {user_intent}", assigned_agent=role)
            for role in pipeline
        ]
        return ControlPlan(
            plan_id=f"PLAN_{int(time.time()*1000)}",
            intent=user_intent,
            agent_pipeline=pipeline,
            subtasks=subtasks,
            estimated_mcp_calls=12
        )

    def execute_critic_evaluation(
        self,
        task_id: str,
        current_score: float,
        score_history: List[float]
    ) -> Tuple[DecisionAction, str]:
        # 1. Diminishing returns detection
        if len(score_history) >= 2:
            delta = current_score - score_history[-1]
            if 0.0 <= delta < 0.02:
                return DecisionAction.ESCALATE, f"DIMINISHING_RETURNS: Score delta is only {delta:.3f}. Refinement halted."

        # 2. Decision Action
        if current_score >= 0.85:
            return DecisionAction.ACCEPT, "Quality target satisfied."
        elif current_score >= 0.40:
            return DecisionAction.REFINE, "Score is improvable. Requesting minimal parameter refinement."
        else:
            return DecisionAction.REGENERATE, "Score below acceptable floor. Component regeneration required."

    def handle_mcp_timeout_reconciliation(
        self,
        task_id: str,
        expected_object_name: str,
        simulated_blender_scene_objects: List[str]
    ) -> Dict[str, Any]:
        # Anti-Duplicate Check: Query actual state before retry
        if expected_object_name in simulated_blender_scene_objects:
            return {
                "action": "RECONCILE",
                "message": f"Asset '{expected_object_name}' was already created in Blender despite timeout. Operation reconciled without duplicate execution."
            }
        else:
            return {
                "action": "RETRY",
                "message": f"Asset '{expected_object_name}' not found in Blender. Safe to retry."
            }

    def execute_with_budget(self, task: Task, requested_mcp_calls: int) -> AgentResult:
        if self.total_mcp_calls + requested_mcp_calls > self.max_mcp_calls:
            task.status = TaskState.BLOCKED
            return AgentResult(
                task_id=task.task_id,
                agent_id="CONTROL_PLANE",
                status=TaskState.BLOCKED,
                is_valid=False,
                error_message=f"BUDGET_EXCEEDED: Exceeded max MCP calls ({self.max_mcp_calls}). Invoking RecoveryAgent.",
                mcp_calls_used=0
            )

        self.total_mcp_calls += requested_mcp_calls
        task.status = TaskState.COMPLETED
        return AgentResult(
            task_id=task.task_id,
            agent_id=str(task.assigned_agent.value if task.assigned_agent else "SYSTEM"),
            status=TaskState.COMPLETED,
            outputs={"result": "SUCCESS"},
            is_valid=True,
            mcp_calls_used=requested_mcp_calls
        )

    def salvage_partial_outputs(
        self,
        task_id: str,
        generated_artifacts: Dict[str, bool]
    ) -> Dict[str, Any]:
        # RecoveryAgent parcial salvage
        retained = [art for art, valid in generated_artifacts.items() if valid]
        discarded = [art for art, valid in generated_artifacts.items() if not valid]
        return {
            "task_id": task_id,
            "retained_outputs": retained,
            "discarded_outputs": discarded,
            "recovery_action": "REGENERATE_DISCARDED_ONLY",
            "message": f"Retained {len(retained)} valid outputs ({retained}). Discarded {len(discarded)} ({discarded}). Avoided full restart."
        }
