from typing import Optional, Dict, Any, List
from .operations import OperationResult
from .transaction_manager import TransactionManager
from ..planning.planner import ExecutionPlan, PlannedOperation
from ..core.scene_graph import SceneGraph, DimensionsSpec, Transform
from ..blender.blender_adapter import BlenderAdapter

class PlanExecutor:
    def __init__(self, transaction_manager: TransactionManager, adapter: Optional[BlenderAdapter] = None):
        self.transaction_manager = transaction_manager
        self.adapter = adapter or BlenderAdapter()

    def execute_plan(self, plan: ExecutionPlan, graph: SceneGraph, dry_run: bool = False) -> Dict[str, Any]:
        if plan.budget_exceeded or plan.error_message:
            return {
                "task_id": plan.task_id,
                "status": "failed",
                "asset_id": plan.asset_id,
                "error_code": "PLANNING_ERROR" if not plan.budget_exceeded else "CHANGE_BUDGET_EXCEEDED",
                "message": plan.error_message or "Plan contains errors."
            }

        if dry_run or plan.is_dry_run:
            return {
                "task_id": plan.task_id,
                "status": "dry_run_success",
                "asset_id": plan.asset_id,
                "operations_count": len(plan.operations),
                "affected_objects": plan.affected_objects,
                "is_dry_run": True
            }

        # Iniciar transacción
        tx = self.transaction_manager.begin_transaction(plan.task_id, graph)
        results: List[OperationResult] = []

        try:
            for op in plan.operations:
                if op.is_no_op:
                    res = OperationResult(operation_id=op.operation_id, success=True, status="NO_OP", message="Operation skipped as state is identical.")
                    results.append(res)
                    continue

                # Preconditions
                target_node = graph.get_node(op.target_id)
                if op.operation_type != "CREATE_COMPONENT" and not target_node:
                    raise ValueError(f"PRECONDITION_FAILED: Target {op.target_id} does not exist.")

                # Ejecutar modificación en el Scene Graph
                if op.operation_type == "CREATE_COMPONENT":
                    # El nodo ya se añadió al graph durante setup o se añade aquí
                    pass
                elif op.operation_type == "SET_DIMENSIONS":
                    val = op.parameters["value"]
                    if isinstance(val, (tuple, list)):
                        target_node.dimensions = DimensionsSpec(width=val[0], depth=val[1], height=val[2])
                    elif isinstance(val, dict):
                        target_node.dimensions = DimensionsSpec(**val)
                    elif isinstance(val, DimensionsSpec):
                        target_node.dimensions = val
                    target_node.version += 1
                elif op.operation_type == "SET_TRANSFORM":
                    val = op.parameters["value"]
                    if isinstance(val, dict):
                        target_node.local_transform = Transform(**val)
                    elif isinstance(val, Transform):
                        target_node.local_transform = val
                    target_node.version += 1
                elif op.operation_type == "MODIFY_COMPONENT":
                    prop = op.parameters["property"]
                    val = op.parameters["value"]
                    if hasattr(target_node, prop):
                        setattr(target_node, prop, val)
                    target_node.version += 1

                # Ejecutar en el Blender Adapter
                adapter_res = self.adapter.execute_operation(op, graph)
                if not adapter_res.get("success", False):
                    raise RuntimeError(f"BLENDER_ERROR: {adapter_res.get('message', 'Adapter operation failed')}")

                results.append(OperationResult(operation_id=op.operation_id, success=True, status="SUCCESS"))

            # Commit transacción
            self.transaction_manager.commit(plan.task_id)
            return {
                "task_id": plan.task_id,
                "status": "completed",
                "asset_id": plan.asset_id,
                "operations": len(results),
                "objects_modified": plan.affected_objects,
                "results": [r.__dict__ for r in results]
            }

        except Exception as e:
            # Rollback automático ante cualquier fallo
            self.transaction_manager.rollback(plan.task_id)
            return {
                "task_id": plan.task_id,
                "status": "failed",
                "asset_id": plan.asset_id,
                "error_code": "TRANSACTION_FAILED",
                "message": f"Transaction rolled back due to error: {str(e)}"
            }
