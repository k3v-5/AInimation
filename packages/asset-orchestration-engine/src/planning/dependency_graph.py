from typing import Dict, List, Set, Optional

class DependencyGraph:
    def __init__(self):
        self.dependencies: Dict[str, Set[str]] = {} # node_id -> set of dependencies (parents)

    def add_node(self, node_id: str, depends_on: Optional[List[str]] = None):
        if node_id not in self.dependencies:
            self.dependencies[node_id] = set()
        if depends_on:
            for dep in depends_on:
                if dep:
                    self.dependencies[node_id].add(dep)

    def get_execution_order(self) -> List[str]:
        visited: Set[str] = set()
        temp_mark: Set[str] = set()
        order: List[str] = []

        def visit(node: str):
            if node in temp_mark:
                raise ValueError(f"Cyclic dependency detected involving node: {node}")
            if node not in visited:
                temp_mark.add(node)
                for dep in self.dependencies.get(node, set()):
                    if dep in self.dependencies:
                        visit(dep)
                temp_mark.remove(node)
                visited.add(node)
                order.append(node)

        for node in list(self.dependencies.keys()):
            if node not in visited:
                visit(node)

        return order
