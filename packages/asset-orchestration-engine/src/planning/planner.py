from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from ..core.scene_graph import SceneGraph, SceneNode
from ..specification.asset_schema import AssetSpecification, DimensionsSpec
from .dependency_graph import DependencyGraph
from .change_analyzer import ChangeAnalyzer
from ..core.id_manager import IdManager

@dataclass
class ChangeBudget:
    max_operations: int = 20
    max_objects_affected: int = 5
    allow_destructive_operations: bool = False
    allow_new_components: bool = True

@dataclass
class PlannedOperation:
    operation_id: str
    operation_type: str # CREATE_COMPONENT, MODIFY_COMPONENT, SET_DIMENSIONS, NO_OP
    target_id: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    is_no_op: bool = False

@dataclass
class ExecutionPlan:
    task_id: str
    asset_id: str
    operations: List[PlannedOperation] = field(default_factory=list)
    affected_objects: List[str] = field(default_factory=list)
    is_dry_run: bool = False
    budget_exceeded: bool = False
    error_message: Optional[str] = None

class Planner:
    def __init__(self, change_analyzer: Optional[ChangeAnalyzer] = None):
        self.change_analyzer = change_analyzer or ChangeAnalyzer()

    def plan_creation(self, spec: AssetSpecification, graph: SceneGraph) -> ExecutionPlan:
        task_id = IdManager.generate_task_id()
        plan = ExecutionPlan(task_id=task_id, asset_id=spec.asset_id)

        # Usar dependency graph para el orden de creación
        dep_graph = DependencyGraph()
        for c in spec.components:
            cid = IdManager.make_component_id(spec.asset_id, c.id)
            pid = IdManager.make_component_id(spec.asset_id, c.parent_id) if c.parent_id else None
            dep_graph.add_node(cid, [pid] if pid else None)

        try:
            creation_order = dep_graph.get_execution_order()
        except ValueError as e:
            plan.error_message = str(e)
            return plan

        for comp_id in creation_order:
            node = graph.get_node(comp_id)
            if not node:
                continue
            op = PlannedOperation(
                operation_id=IdManager.generate_operation_id(),
                operation_type="CREATE_COMPONENT",
                target_id=comp_id,
                parameters={
                    "name": node.name,
                    "primitive": node.primitive_type.value,
                    "parent_id": node.parent_id,
                    "dimensions": node.dimensions.to_tuple() if node.dimensions else (1.0, 1.0, 1.0),
                    "transform": {
                        "location": node.local_transform.location,
                        "rotation": node.local_transform.rotation,
                        "scale": node.local_transform.scale
                    },
                    "materials": node.material_references
                }
            )
            plan.operations.append(op)
            plan.affected_objects.append(comp_id)

        return plan

    def plan_modification(
        self,
        graph: SceneGraph,
        target_id: str,
        changes: Dict[str, Any],
        budget: Optional[ChangeBudget] = None
    ) -> ExecutionPlan:
        task_id = IdManager.generate_task_id()
        plan = ExecutionPlan(task_id=task_id, asset_id=graph.asset_id)
        budget = budget or ChangeBudget()

        node = graph.get_node(target_id)
        if not node:
            # Buscar por nombre relativo
            node = graph.find_node_by_name(target_id)

        if not node:
            plan.error_message = f"COMPONENT_NOT_FOUND: Component '{target_id}' does not exist in asset '{graph.asset_id}'."
            return plan

        is_no_op, real_changes = self.change_analyzer.analyze_node_modification(node, changes)

        if is_no_op:
            op = PlannedOperation(
                operation_id=IdManager.generate_operation_id(),
                operation_type="NO_OP",
                target_id=node.id,
                parameters={"reason": "State already matches desired parameters within tolerance."},
                is_no_op=True
            )
            plan.operations.append(op)
            return plan

        # Generar operaciones quirúrgicas para cada cambio real
        for prop, val in real_changes.items():
            op_type = "MODIFY_COMPONENT"
            if prop == "dimensions":
                op_type = "SET_DIMENSIONS"
            elif prop == "local_transform":
                op_type = "SET_TRANSFORM"

            op = PlannedOperation(
                operation_id=IdManager.generate_operation_id(),
                operation_type=op_type,
                target_id=node.id,
                parameters={"property": prop, "value": val}
            )
            plan.operations.append(op)

        plan.affected_objects.append(node.id)

        # Validar presupuesto de cambios
        if len(plan.operations) > budget.max_operations or len(plan.affected_objects) > budget.max_objects_affected:
            plan.budget_exceeded = True
            plan.error_message = "CHANGE_BUDGET_EXCEEDED: Requested change exceeds allowed operation/object budget."

        return plan
