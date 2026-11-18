"""
DependencyGraph manages asset component dependencies and detects cycles.
UAF-81.1 Sections 25, 26.
"""

from typing import Dict, List, Set, Optional
from ...core.diagnostics.errors import SpecificationError


class CyclicDependencyError(SpecificationError):
    """Raised when a circular reference loop is detected in asset dependencies."""
    def __init__(self, cycle_path: List[str]):
        msg = f"Circular dependency cycle detected: {' -> '.join(cycle_path)}"
        super().__init__(message=msg, code="CYCLIC_DEPENDENCY", details={"cycle": cycle_path})
        self.cycle_path = cycle_path


class DependencyGraph:
    """
    Directed graph representing dependencies between asset specifications or component modules.
    """
    def __init__(self):
        self._adj: Dict[str, Set[str]] = {}

    def add_node(self, node_id: str) -> None:
        if node_id not in self._adj:
            self._adj[node_id] = set()

    def add_dependency(self, node_id: str, depends_on: str) -> None:
        """Declares that node_id depends on depends_on."""
        self.add_node(node_id)
        self.add_node(depends_on)
        self._adj[node_id].add(depends_on)

    def detect_cycle(self) -> Optional[List[str]]:
        """
        Detects if a cycle exists in the dependency graph.
        Returns the cycle path if found, or None.
        """
        visited: Dict[str, int] = {}  # 0: unvisited, 1: visiting, 2: visited
        parent: Dict[str, str] = {}
        for node in self._adj:
            visited[node] = 0

        def dfs(u: str, path: List[str]) -> Optional[List[str]]:
            visited[u] = 1
            path.append(u)

            for v in self._adj.get(u, set()):
                if visited[v] == 1:
                    # Found cycle
                    cycle_start_idx = path.index(v)
                    return path[cycle_start_idx:] + [v]
                if visited[v] == 0:
                    parent[v] = u
                    result = dfs(v, path)
                    if result:
                        return result

            path.pop()
            visited[u] = 2
            return None

        for node in list(self._adj.keys()):
            if visited[node] == 0:
                cycle = dfs(node, [])
                if cycle:
                    return cycle

        return None

    def validate_acyclic(self) -> None:
        cycle = self.detect_cycle()
        if cycle:
            raise CyclicDependencyError(cycle_path=cycle)

    def topological_sort(self) -> List[str]:
        """
        Returns nodes ordered such that all dependencies appear before dependent nodes.
        Raises CyclicDependencyError if graph contains cycles.
        """
        self.validate_acyclic()

        visited: Set[str] = set()
        order: List[str] = []

        def dfs(u: str):
            visited.add(u)
            for v in self._adj.get(u, set()):
                if v not in visited:
                    dfs(v)
            order.append(u)

        for node in self._adj:
            if node not in visited:
                dfs(node)

        return order
