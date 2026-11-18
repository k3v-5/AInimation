"""
SurfaceDependencyTracker manages selective invalidation between geometry and surface artifacts.
UAF-81.4 Sections 79, 80, 94.
"""

from typing import Dict, List, Set, Optional


class SurfaceDependencyTracker:
    """
    Manages dependency edges across geometry, bakes, masks, textures, and material instances.
    Enforces selective dirty invalidation without monolithic full rebuilding.
    UAF-81.4 Section 94.
    """
    def __init__(self):
        # target_node -> set of upstream dependencies it relies upon
        self._dependencies: Dict[str, Set[str]] = {}
        # source_node -> set of downstream dependents that depend on it
        self._dependents: Dict[str, Set[str]] = {}
        # Set of dirty/invalidated nodes
        self._dirty_nodes: Set[str] = set()

    def add_dependency(self, target: str, depends_on: str) -> None:
        if target not in self._dependencies:
            self._dependencies[target] = set()
        self._dependencies[target].add(depends_on)

        if depends_on not in self._dependents:
            self._dependents[depends_on] = set()
        self._dependents[depends_on].add(target)

    def mark_dirty(self, changed_node: str) -> Set[str]:
        """
        Marks a node as dirty and recursively invalidates only downstream dependent artifacts.
        Returns the set of all newly invalidated artifacts.
        """
        invalidated: Set[str] = set()
        queue = [changed_node]

        while queue:
            curr = queue.pop(0)
            if curr not in self._dirty_nodes:
                self._dirty_nodes.add(curr)
                invalidated.add(curr)
                # Propagate downstream
                for dep in self._dependents.get(curr, set()):
                    if dep not in self._dirty_nodes:
                        queue.append(dep)

        return invalidated

    def is_dirty(self, node: str) -> bool:
        return node in self._dirty_nodes

    def clear_dirty(self, node: str) -> None:
        self._dirty_nodes.discard(node)

    def get_dirty_nodes(self) -> Set[str]:
        return set(self._dirty_nodes)
