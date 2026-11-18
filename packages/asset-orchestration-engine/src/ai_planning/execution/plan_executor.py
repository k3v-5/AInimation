from typing import Dict, Any, List, Optional, Tuple
from ..tasks.task_graph import TaskGraph, PlannedTask, TaskStatus
from ...unreal.core.unreal_engine import UnrealEngine
from ...gameplay.core.gameplay_engine import GameplayEngine

class PlanExecutor:
    def __init__(
        self,
        unreal_engine: Optional[UnrealEngine] = None,
        gameplay_engine: Optional[GameplayEngine] = None,
        max_repair_attempts: int = 2
    ):
        self.ue = unreal_engine
        self.gp = gameplay_engine
        self.max_repair_attempts = max_repair_attempts

    def execute_plan(
        self,
        task_graph: TaskGraph,
        dry_run: bool = False
    ) -> Dict[str, Any]:
        executed_tasks: List[str] = []
        mcp_calls = 0

        for task in task_graph.list_tasks():
            if dry_run:
                executed_tasks.append(task.task_id)
                mcp_calls += 1
                continue

            attempts = 0
            success = False
            error_msg = None

            while attempts <= self.max_repair_attempts and not success:
                attempts += 1
                task.attempts = attempts
                task.status = TaskStatus.RUNNING

                try:
                    res = self._execute_task(task)
                    mcp_calls += 1
                    if res.get("success", False):
                        task.status = TaskStatus.SUCCESS
                        success = True
                        executed_tasks.append(task.task_id)
                    else:
                        error_msg = res.get("message", "Task execution error.")
                except Exception as e:
                    error_msg = str(e)

            if not success:
                task.status = TaskStatus.FAILED
                return {
                    "success": False,
                    "error_code": "REPAIR_LIMIT_REACHED",
                    "failed_task": task.task_id,
                    "attempts": attempts,
                    "message": f"Task '{task.task_id}' failed after {attempts} attempts. Error: {error_msg}",
                    "executed_tasks": executed_tasks,
                    "mcp_calls": mcp_calls
                }

        return {
            "success": True,
            "status": "COMPLETED",
            "executed_tasks": executed_tasks,
            "mcp_calls": mcp_calls,
            "stop_rule_triggered": True # STOP RULE: Emit STOP immediately upon goal completion
        }

    def _execute_task(self, task: PlannedTask) -> Dict[str, Any]:
        t_type = task.task_type
        params = task.parameters

        if t_type == "MOVE_ACTOR" and self.ue:
            return self.ue.move_actor(task.target, delta=params.get("delta"), new_location=params.get("new_location"))

        elif t_type == "ATTACH_ACTOR" and self.ue:
            return self.ue.attach_actor(task.target, params.get("parent_id"), socket_name=params.get("socket_name"))

        elif t_type == "ADD_CAPABILITY" and self.gp:
            return self.gp.add_capability(task.target, params.get("capability"))

        elif t_type == "SET_GAMEPLAY_DATA" and self.gp:
            return self.gp.set_gameplay_data(task.target, params.get("property"), params.get("value"))

        elif t_type == "PLACE_ON" and self.ue:
            return self.ue.apply_spatial_relation(task.target, params.get("relation", "ON_TOP_OF"), params.get("reference_target"))

        elif t_type == "DELETE_ACTOR" and self.ue:
            return self.ue.delete_actor(task.target)

        elif t_type == "FAIL_SIMULATION": # Para pruebas de error
            return {"success": False, "message": "Simulated hardware error."}

        return {"success": True}
