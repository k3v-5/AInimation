from typing import List, Dict, Set, Tuple
from ..core.construction_plan import ConstructionOperation

class ConstructionDependencyGraph:
    @staticmethod
    def sort_operations(operations: List[ConstructionOperation]) -> Tuple[bool, List[ConstructionOperation], str]:
        op_map = {op.operation_id: op for op in operations}
        in_degree = {op.operation_id: 0 for op in operations}
        adj = {op.operation_id: [] for op in operations}

        for op in operations:
            for dep in op.dependencies:
                if dep in adj:
                    adj[dep].append(op.operation_id)
                    in_degree[op.operation_id] += 1

        queue = [op_id for op_id, deg in in_degree.items() if deg == 0]
        sorted_ops = []

        while queue:
            curr = queue.pop(0)
            sorted_ops.append(op_map[curr])
            for neighbor in adj[curr]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

        if len(sorted_ops) != len(operations):
            return False, [], "INVALID_CONSTRUCTION_GRAPH: Circular dependency detected in construction operations."

        return True, sorted_ops, "Sorted successfully."
