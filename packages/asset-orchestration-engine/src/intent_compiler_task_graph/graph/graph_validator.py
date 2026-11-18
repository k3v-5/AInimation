from typing import List, Set, Dict
from ..core.intent_schema import TaskGraphDAG, CompiledIntent

class GraphValidator:
    @staticmethod
    def validate_graph(dag: TaskGraphDAG, available_capabilities: List[str], intent: CompiledIntent):
        # 1. Detección de Ciclos (Cycle Detection)
        visited: Set[str] = set()
        rec_stack: Set[str] = set()

        def has_cycle(node_id: str) -> bool:
            visited.add(node_id)
            rec_stack.add(node_id)
            node = dag.nodes.get(node_id)
            if node:
                for req in node.requires:
                    if req not in visited:
                        if has_cycle(req):
                            return True
                    elif req in rec_stack:
                        return True
            rec_stack.remove(node_id)
            return False

        for node_id in dag.nodes:
            if node_id not in visited:
                if has_cycle(node_id):
                    raise ValueError(f"DAG_CYCLE_DETECTED: Task graph contains a circular dependency involving '{node_id}'.")

        # 2. Validación de Capacidades Requeridas
        for node in dag.nodes.values():
            for cap in node.required_capabilities:
                if cap not in available_capabilities:
                    raise ValueError(f"UNSUPPORTED: Missing required executor capability '{cap}' for task '{node.node_id}'.")

        # 3. Trazabilidad: Comprobar Requisitos No Implementados (UNIMPLEMENTED_REQUIREMENT)
        produced_outputs = set()
        for node in dag.nodes.values():
            produced_outputs.update(node.produces)

        for req in intent.requirements:
            if req.key == "window_count" and "windows" not in produced_outputs:
                raise ValueError(f"UNIMPLEMENTED_REQUIREMENT: Requirement '{req.description}' has no producer node in DAG.")
            if req.key == "roof_type" and "roof" not in produced_outputs:
                raise ValueError(f"UNIMPLEMENTED_REQUIREMENT: Requirement '{req.description}' has no producer node in DAG.")
