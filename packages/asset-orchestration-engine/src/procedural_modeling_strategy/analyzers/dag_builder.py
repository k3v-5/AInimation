from typing import List, Dict, Any
from ..core.msp_types import GeometricOperationType
from ..core.msp_schema import GeometricOperation, ComponentStrategy

class DAGBuilder:
    @classmethod
    def build_execution_dag(cls, component_strategies: List[ComponentStrategy]) -> List[GeometricOperation]:
        dag: List[GeometricOperation] = []
        op_count = 1

        # 1. Operaciones de Creación Base (Primarias primero)
        primary_comps = [c for c in component_strategies if c.parent_component_id is None]
        secondary_comps = [c for c in component_strategies if c.parent_component_id is not None]

        created_ops: Dict[str, str] = {}

        for comp in primary_comps:
            op_id = f"OP_{op_count:03d}_CREATE_{comp.component_id.upper()}"
            op = GeometricOperation(
                operation_id=op_id,
                operation_type=GeometricOperationType.CREATE,
                target_component=comp.component_id,
                parameters={"primitive": comp.base_geometry.value, "dimensions": comp.dimensions},
                dependencies=[]
            )
            dag.append(op)
            created_ops[comp.component_id] = op_id
            op_count += 1

            # Modifiers / Booleans sobre primaria
            if comp.modifiers:
                for mod in comp.modifiers:
                    mod_op_id = f"OP_{op_count:03d}_MOD_{mod.modifier_type.upper()}_{comp.component_id.upper()}"
                    dag.append(GeometricOperation(
                        operation_id=mod_op_id,
                        operation_type=GeometricOperationType.BEVEL if "bevel" in mod.modifier_type.lower() else GeometricOperationType.MIRROR,
                        target_component=comp.component_id,
                        parameters=mod.parameters,
                        dependencies=[created_ops[comp.component_id]]
                    ))
                    op_count += 1

        for comp in secondary_comps:
            parent_op = created_ops.get(comp.parent_component_id, dag[0].operation_id if dag else "")
            op_id = f"OP_{op_count:03d}_CREATE_{comp.component_id.upper()}"
            op = GeometricOperation(
                operation_id=op_id,
                operation_type=GeometricOperationType.ARRAY if comp.method.value == "ARRAY_BASED" else GeometricOperationType.CREATE,
                target_component=comp.component_id,
                parameters={"primitive": comp.base_geometry.value, "dimensions": comp.dimensions},
                dependencies=[parent_op] if parent_op else []
            )
            dag.append(op)
            created_ops[comp.component_id] = op_id
            op_count += 1

        return dag

    @classmethod
    def check_circular_dependencies(cls, dependencies: Dict[str, List[str]]) -> bool:
        # Detecta ciclos en grafo dirigido
        visited = set()
        rec_stack = set()

        def is_cyclic(node):
            visited.add(node)
            rec_stack.add(node)
            for neighbor in dependencies.get(node, []):
                if neighbor not in visited:
                    if is_cyclic(neighbor):
                        return True
                elif neighbor in rec_stack:
                    return True
            rec_stack.remove(node)
            return False

        for node in dependencies:
            if node not in visited:
                if is_cyclic(node):
                    return True
        return False
