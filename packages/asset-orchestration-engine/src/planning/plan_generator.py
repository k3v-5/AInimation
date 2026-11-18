from typing import Dict, Any, Optional, List
from ..intent.intent_types import NormalizedIntent, IntentType, ModifierType
from ..intent.target_resolver import TargetResolver
from ..intent.confidence_system import ConfidenceSystem, ConfidenceAction
from ..core.scene_graph import SceneGraph, DimensionsSpec
from ..core.id_manager import IdManager
from .planner import ExecutionPlan, PlannedOperation, ChangeBudget
from .change_analyzer import ChangeAnalyzer
from .scope_manager import ScopeManager, ScopeSpec
from .budget_manager import BudgetManager
from .constraint_engine import ConstraintEngine

class PlanGenerator:
    def __init__(
        self,
        change_analyzer: Optional[ChangeAnalyzer] = None,
        confidence_system: Optional[ConfidenceSystem] = None,
        constraint_engine: Optional[ConstraintEngine] = None
    ):
        self.change_analyzer = change_analyzer or ChangeAnalyzer()
        self.confidence_system = confidence_system or ConfidenceSystem()
        self.constraint_engine = constraint_engine or ConstraintEngine()

    def generate_plan(
        self,
        intent: NormalizedIntent,
        graph: Optional[SceneGraph] = None,
        scope: Optional[ScopeSpec] = None,
        budget: Optional[ChangeBudget] = None
    ) -> ExecutionPlan:
        task_id = IdManager.generate_task_id()
        asset_id = intent.asset_id or (graph.asset_id if graph else "asset_001")
        plan = ExecutionPlan(task_id=task_id, asset_id=asset_id)

        # 1. Evaluar Confianza del Intent
        conf_action, conf_msg = self.confidence_system.evaluate(intent.confidence)
        if conf_action == ConfidenceAction.REQUIRE_CLARIFICATION or intent.clarification_needed:
            plan.error_message = f"CLARIFICATION_REQUIRED: {intent.clarification_question or conf_msg}"
            return plan

        # 2. INTENT: CREATE_ASSET
        if intent.intent_type == IntentType.CREATE_ASSET:
            dim = float(intent.value) if intent.value is not None else 1.0
            ptype = intent.parameters.get("type", "cube")
            
            # Operación de creación del componente principal
            comp_id = f"{asset_id}.body"
            op = PlannedOperation(
                operation_id=IdManager.generate_operation_id(),
                operation_type="CREATE_COMPONENT",
                target_id=comp_id,
                parameters={
                    "name": "body",
                    "primitive": "cylinder" if ptype in ["barrel", "cylinder"] else ("sphere" if ptype == "sphere" else "box"),
                    "dimensions": (dim, dim, dim),
                    "materials": ["default_material"]
                }
            )
            plan.operations.append(op)
            plan.affected_objects.append(comp_id)
            return plan

        # Para modificaciones se requiere un SceneGraph activo
        if not graph:
            plan.error_message = f"ASSET_NOT_FOUND: No active scene graph for asset '{asset_id}'."
            return plan

        # 3. Resolución de Target Component
        raw_target = intent.target_component or "body"
        target_id, target_conf, candidates = TargetResolver.resolve_component(raw_target, graph)

        if not target_id:
            if len(candidates) > 1:
                plan.error_message = f"AMBIGUOUS_TARGET: Multiple components match '{raw_target}': {candidates}."
            else:
                plan.error_message = f"COMPONENT_NOT_FOUND: Component '{raw_target}' not found in asset '{asset_id}'."
            return plan

        # 4. Validación de Scope
        is_del = (intent.parameters.get("action") == "delete")
        scope_ok, scope_err_code, scope_err_msg = ScopeManager.validate_action(
            scope=scope,
            asset_id=asset_id,
            target_component_id=target_id,
            is_delete_op=is_del
        )
        if not scope_ok:
            plan.error_message = f"{scope_err_code}: {scope_err_msg}"
            return plan

        node = graph.get_node(target_id)
        if not node:
            plan.error_message = f"COMPONENT_NOT_FOUND: Node '{target_id}' not found."
            return plan

        # 5. Cálculo del Nuevo Estado según ModifierType
        axis = intent.dimension_axis or "height"
        current_w = node.dimensions.width
        current_d = node.dimensions.depth
        current_h = node.dimensions.height

        new_w, new_d, new_h = current_w, current_d, current_h
        val = intent.value if intent.value is not None else 1.0

        if intent.modifier_type == ModifierType.SET:
            if axis in ["height", "total_length", "largo", "alto"]: new_h = float(val)
            elif axis in ["width", "ancho"]: new_w = float(val)
            elif axis in ["depth", "grosor", "profundo"]: new_d = float(val)
            elif axis == "all": new_w, new_d, new_h = float(val), float(val), float(val)

        elif intent.modifier_type == ModifierType.INCREMENT:
            if axis in ["height", "total_length", "largo", "alto"]: new_h = current_h + float(val)
            elif axis in ["width", "ancho"]: new_w = current_w + float(val)
            elif axis in ["depth", "grosor", "profundo"]: new_d = current_d + float(val)
            elif axis == "all": new_w += float(val); new_d += float(val); new_h += float(val)

        elif intent.modifier_type == ModifierType.MULTIPLY:
            factor = float(val)
            if axis in ["height", "total_length", "largo", "alto"]: new_h = current_h * factor
            elif axis in ["width", "ancho"]: new_w = current_w * factor
            elif axis in ["depth", "grosor", "profundo"]: new_d = current_d * factor
            elif axis == "all": new_w *= factor; new_d *= factor; new_h *= factor

        # 6. Validación de Restricciones (Constraints)
        c_ok, c_msg = self.constraint_engine.validate_value(f"{target_id}.{axis}", new_h if axis == "height" else new_w)
        if not c_ok:
            plan.error_message = f"CONSTRAINT_VIOLATION: {c_msg}"
            return plan

        # 7. Detección de NO_OP vía ChangeAnalyzer
        is_no_op, real_changes = self.change_analyzer.analyze_node_modification(
            node,
            {"dimensions": DimensionsSpec(width=new_w, depth=new_d, height=new_h)}
        )

        if is_no_op:
            op = PlannedOperation(
                operation_id=IdManager.generate_operation_id(),
                operation_type="NO_OP",
                target_id=target_id,
                parameters={"reason": "TARGET_ALREADY_MATCHES_REQUEST", "current_dimensions": (current_w, current_d, current_h)},
                is_no_op=True
            )
            plan.operations.append(op)
            return plan

        # 8. Generar Operación Determinista
        op = PlannedOperation(
            operation_id=IdManager.generate_operation_id(),
            operation_type="SET_DIMENSIONS",
            target_id=target_id,
            parameters={
                "property": "dimensions",
                "value": (new_w, new_d, new_h),
                "axis_modified": axis,
                "previous_value": (current_w, current_d, current_h)
            }
        )
        plan.operations.append(op)
        plan.affected_objects.append(target_id)

        # 9. Validación de Presupuesto (Change Budget)
        b_ok, b_msg = BudgetManager.validate_budget(budget, len(plan.operations), len(plan.affected_objects))
        if not b_ok:
            plan.budget_exceeded = True
            plan.error_message = b_msg

        return plan
