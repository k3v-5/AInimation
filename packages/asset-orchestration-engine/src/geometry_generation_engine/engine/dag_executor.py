from typing import List, Dict, Any, Tuple
from ..core.geom_types import OperationState
from ..core.geom_schema import GenerationContext
from ..operations.primitive_ops import CreatePrimitiveOp
from ..operations.transform_ops import TransformOp, SetPivotOp
from ..operations.modifier_ops import ApplyBevelOp, ApplyMirrorOp, ApplyArrayOp, ApplyBooleanOp
from .parameter_resolver import ParameterResolver

class DAGExecutor:
    @classmethod
    def execute_dag(
        cls,
        context: GenerationContext,
        initial_state: Dict[str, Any]
    ) -> Tuple[Dict[str, Any], List[Dict[str, Any]], List[str]]:
        state = initial_state
        trace: List[Dict[str, Any]] = []
        errors: List[str] = []

        executed_ops = []
        execution_graph = getattr(context.strategy_plan, "execution_graph", [])
        raw_params = getattr(context.strategy_plan, "parameters", [])

        target_set = set(context.target_components) if context.target_components else None

        for op_spec in execution_graph:
            target_comp = getattr(op_spec, "target_component", "comp_01")
            op_type = getattr(op_spec, "operation_type", "CREATE")
            if hasattr(op_type, "value"):
                op_type = op_type.value

            # Si es regeneración parcial y el componente no está afectado, omitir
            if target_set and target_comp not in target_set:
                trace.append({
                    "operation_id": getattr(op_spec, "operation_id", ""),
                    "status": OperationState.SKIPPED.value,
                    "target_component": target_comp
                })
                continue

            resolved_params = ParameterResolver.resolve_parameters(
                getattr(op_spec, "parameters", {}),
                raw_params
            )

            # Factory de Operaciones
            op_inst = None
            if "CREATE" in op_type:
                op_inst = CreatePrimitiveOp(op_spec.operation_id, target_comp, resolved_params)
            elif "BEVEL" in op_type:
                op_inst = ApplyBevelOp(op_spec.operation_id, target_comp, resolved_params)
            elif "MIRROR" in op_type:
                op_inst = ApplyMirrorOp(op_spec.operation_id, target_comp, resolved_params)
            elif "ARRAY" in op_type:
                op_inst = ApplyArrayOp(op_spec.operation_id, target_comp, resolved_params)
            elif "BOOLEAN" in op_type:
                op_inst = ApplyBooleanOp(op_spec.operation_id, target_comp, resolved_params)
            elif "PIVOT" in op_type:
                op_inst = SetPivotOp(op_spec.operation_id, target_comp, resolved_params)
            else:
                op_inst = TransformOp(op_spec.operation_id, target_comp, resolved_params)

            # 1. Validación
            val = op_inst.validate(context)
            if not val.is_valid:
                errors.extend(val.errors)
                trace.append({
                    "operation_id": op_spec.operation_id,
                    "status": OperationState.FAILED.value,
                    "errors": val.errors
                })
                break

            # 2. Ejecución
            try:
                state = op_inst.execute(context, state)
                executed_ops.append(op_inst)
                trace.append({
                    "operation_id": op_spec.operation_id,
                    "status": OperationState.SUCCESS.value,
                    "target_component": target_comp
                })
            except Exception as e:
                errors.append(f"EXECUTION_ERROR: {str(e)}")
                trace.append({
                    "operation_id": op_spec.operation_id,
                    "status": OperationState.FAILED.value,
                    "error": str(e)
                })
                # Rollback compensatorio
                for prev_op in reversed(executed_ops):
                    prev_op.rollback(context, state)
                break

        return state, trace, errors
