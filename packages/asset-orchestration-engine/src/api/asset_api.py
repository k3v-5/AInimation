from typing import Dict, Any, Optional, Union
from ..specification.parser import SpecificationParser
from ..core.asset_manager import AssetManager
from ..planning.planner import Planner
from ..execution.executor import PlanExecutor
from ..validation.validator import QualityGateValidator
from ..history.snapshot_manager import SnapshotManager
from ..history.version_manager import VersionManager
from ..history.operation_log import OperationLog

class AssetAPI:
    def __init__(
        self,
        asset_manager: AssetManager,
        planner: Planner,
        executor: PlanExecutor,
        validator: QualityGateValidator,
        snapshot_mgr: SnapshotManager,
        version_mgr: VersionManager,
        op_log: OperationLog
    ):
        self.asset_manager = asset_manager
        self.planner = planner
        self.executor = executor
        self.validator = validator
        self.snapshot_mgr = snapshot_mgr
        self.version_mgr = version_mgr
        self.op_log = op_log

    def create_asset(self, spec_input: Union[Dict[str, Any], str], dry_run: bool = False) -> Dict[str, Any]:
        if isinstance(spec_input, str):
            spec = SpecificationParser.parse_json(spec_input)
        else:
            spec = SpecificationParser.parse_dict(spec_input)

        # 1. Crear SceneGraph en memoria
        graph = self.asset_manager.create_from_specification(spec)

        # 2. Planificar creación
        plan = self.planner.plan_creation(spec, graph)
        if plan.error_message:
            return {
                "success": False,
                "status": "failed",
                "asset_id": spec.asset_id,
                "error_code": "PLANNING_ERROR",
                "message": plan.error_message
            }

        # 3. Ejecutar plan
        exec_res = self.executor.execute_plan(plan, graph, dry_run=dry_run)
        if exec_res.get("status") == "failed":
            return {
                "success": False,
                "status": "failed",
                "asset_id": spec.asset_id,
                "error_code": exec_res.get("error_code"),
                "message": exec_res.get("message")
            }

        # 4. Validar
        val_res = self.validator.validate_asset(graph, spec)

        # 5. Registrar snapshot y versión
        self.snapshot_mgr.capture_snapshot(spec.asset_id, 1, graph)
        self.op_log.record(
            task_id=plan.task_id,
            asset_id=spec.asset_id,
            operation_type="CREATE_ASSET",
            target_id=spec.asset_id,
            parameters={"components_count": len(spec.components)},
            status="SUCCESS" if val_res["passed"] else "VALIDATION_FAILED"
        )

        return {
            "success": val_res["passed"],
            "task_id": plan.task_id,
            "status": "completed" if val_res["passed"] else "validation_failed",
            "asset_id": spec.asset_id,
            "operations": len(plan.operations),
            "objects_modified": plan.affected_objects,
            "validation": val_res
        }
