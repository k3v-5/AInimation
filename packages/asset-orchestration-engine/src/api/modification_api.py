from typing import Dict, Any, Optional
from ..core.state_manager import StateManager
from ..planning.planner import Planner, ChangeBudget
from ..execution.executor import PlanExecutor
from ..validation.validator import QualityGateValidator
from ..history.snapshot_manager import SnapshotManager
from ..history.version_manager import VersionManager
from ..history.operation_log import OperationLog

class ModificationAPI:
    def __init__(
        self,
        state_manager: StateManager,
        planner: Planner,
        executor: PlanExecutor,
        validator: QualityGateValidator,
        snapshot_mgr: SnapshotManager,
        version_mgr: VersionManager,
        op_log: OperationLog
    ):
        self.state_manager = state_manager
        self.planner = planner
        self.executor = executor
        self.validator = validator
        self.snapshot_mgr = snapshot_mgr
        self.version_mgr = version_mgr
        self.op_log = op_log

    def plan_change(
        self,
        asset_id: str,
        target_component: str,
        changes: Dict[str, Any],
        budget: Optional[ChangeBudget] = None
    ) -> Dict[str, Any]:
        graph = self.state_manager.get_graph(asset_id)
        if not graph:
            return {"success": False, "error_code": "ASSET_NOT_FOUND", "message": f"Asset '{asset_id}' not found."}

        plan = self.planner.plan_modification(graph, target_component, changes, budget)
        if plan.error_message:
            return {
                "success": False,
                "status": "failed",
                "error_code": "CHANGE_BUDGET_EXCEEDED" if plan.budget_exceeded else "COMPONENT_NOT_FOUND",
                "message": plan.error_message
            }

        return {
            "success": True,
            "task_id": plan.task_id,
            "asset_id": asset_id,
            "operations_count": len(plan.operations),
            "affected_objects": plan.affected_objects,
            "operations": [op.__dict__ for op in plan.operations],
            "is_no_op": all(op.is_no_op for op in plan.operations)
        }

    def apply_change(
        self,
        asset_id: str,
        target_component: str,
        changes: Dict[str, Any],
        budget: Optional[ChangeBudget] = None,
        dry_run: bool = False
    ) -> Dict[str, Any]:
        graph = self.state_manager.get_graph(asset_id)
        if not graph:
            return {"success": False, "error_code": "ASSET_NOT_FOUND", "message": f"Asset '{asset_id}' not found."}

        # 1. Planificar cambio
        plan = self.planner.plan_modification(graph, target_component, changes, budget)
        if plan.error_message:
            return {
                "success": False,
                "status": "failed",
                "error_code": "CHANGE_BUDGET_EXCEEDED" if plan.budget_exceeded else "COMPONENT_NOT_FOUND",
                "message": plan.error_message
            }

        # 2. Ejecutar plan
        exec_res = self.executor.execute_plan(plan, graph, dry_run=dry_run)
        if exec_res.get("status") == "failed":
            return {
                "success": False,
                "status": "failed",
                "error_code": exec_res.get("error_code"),
                "message": exec_res.get("message")
            }

        # 3. Validar
        spec = self.state_manager.get_spec(asset_id)
        val_res = self.validator.validate_asset(graph, spec)

        # 4. Incrementar versión y guardar snapshot
        new_version = self.version_mgr.increment_version(asset_id)
        self.snapshot_mgr.capture_snapshot(asset_id, new_version, graph)
        self.op_log.record(
            task_id=plan.task_id,
            asset_id=asset_id,
            operation_type="MODIFY_ASSET",
            target_id=target_component,
            parameters=changes,
            status="SUCCESS" if val_res["passed"] else "VALIDATION_FAILED"
        )

        return {
            "success": val_res["passed"],
            "task_id": plan.task_id,
            "status": "completed" if val_res["passed"] else "validation_failed",
            "asset_id": asset_id,
            "version": new_version,
            "operations": len(plan.operations),
            "objects_modified": plan.affected_objects,
            "validation": val_res
        }
