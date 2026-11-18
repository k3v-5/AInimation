from typing import List, Optional, Tuple, Dict, Set
from collections import deque
from ..nodes.graph_node import GraphNode
from ..nodes.node_types import NodeType
from ..edges.graph_edge import GraphEdge
from ..edges.edge_types import RelationshipType
from ..storage.graph_store import ProjectKnowledgeGraphStore

class GraphQueryEngine:
    """
    Query and graph traversal engine for navigating project relationships.
    """
    def __init__(self, store: ProjectKnowledgeGraphStore):
        self.store = store

    def get_node(self, node_id: str) -> Optional[GraphNode]:
        return self.store.get_node(node_id)

    def find_nodes(self, node_type: NodeType) -> List[GraphNode]:
        return self.store.list_nodes(node_type)

    def find_by_semantic_id(self, semantic_id: str) -> Optional[GraphNode]:
        return self.store.get_node_by_semantic_id(semantic_id)

    def neighbors(self, node_id: str, direction: str = "OUT") -> List[Tuple[GraphNode, GraphEdge]]:
        results = []
        edges = self.store.list_edges()
        if direction.upper() in ("OUT", "BOTH"):
            for e in edges:
                if e.source_node == node_id:
                    target = self.store.get_node(e.target_node)
                    if target:
                        results.append((target, e))
        if direction.upper() in ("IN", "BOTH"):
            for e in edges:
                if e.target_node == node_id:
                    source = self.store.get_node(e.source_node)
                    if source:
                        results.append((source, e))
        return results

    def find_related(self, node_id: str, relationship_type: RelationshipType) -> List[GraphNode]:
        nodes = []
        for e in self.store.list_edges(relationship_type):
            if e.source_node == node_id:
                target = self.store.get_node(e.target_node)
                if target:
                    nodes.append(target)
        return nodes

    def find_dependencies(self, node_id: str) -> List[GraphNode]:
        """Finds all nodes that the given node directly or indirectly depends on."""
        visited = set()
        dep_nodes = []
        queue = deque([node_id])
        forward_deps = {RelationshipType.USES, RelationshipType.DEPENDS_ON, RelationshipType.CONTAINS, RelationshipType.DERIVED_FROM, RelationshipType.PART_OF}

        while queue:
            curr = queue.popleft()
            if curr in visited:
                continue
            visited.add(curr)

            for e in self.store.list_edges():
                # Forward dependency (A USES B / A PART_OF B / A CONTAINS B / A DEPENDS_ON B)
                if e.source_node == curr and e.relationship_type in forward_deps:
                    target = self.store.get_node(e.target_node)
                    if target and target.node_id not in visited:
                        dep_nodes.append(target)
                        queue.append(target.node_id)
        return dep_nodes

    def find_dependents(self, node_id: str) -> List[GraphNode]:
        """Finds all nodes that depend on the given node."""
        visited = set()
        dep_nodes = []
        queue = deque([node_id])
        incoming_deps = {RelationshipType.USES, RelationshipType.DEPENDS_ON, RelationshipType.CONTAINS, RelationshipType.DERIVED_FROM, RelationshipType.PART_OF}

        while queue:
            curr = queue.popleft()
            if curr in visited:
                continue
            visited.add(curr)

            for e in self.store.list_edges():
                # Incoming dependency (A USES curr / A PART_OF curr / A CONTAINS curr -> A is affected/dependent)
                if e.target_node == curr and e.relationship_type in incoming_deps:
                    source = self.store.get_node(e.source_node)
                    if source and source.node_id not in visited:
                        dep_nodes.append(source)
                        queue.append(source.node_id)
                # If curr is PART_OF A, then A contains curr, so modifying curr affects A
                elif e.source_node == curr and e.relationship_type == RelationshipType.PART_OF:
                    target = self.store.get_node(e.target_node)
                    if target and target.node_id not in visited:
                        dep_nodes.append(target)
                        queue.append(target.node_id)
        return dep_nodes

    def find_path(self, source_id: str, target_id: str) -> Optional[List[str]]:
        """BFS shortest path between two nodes."""
        if source_id == target_id:
            return [source_id]
        visited = set()
        queue = deque([[source_id]])

        while queue:
            path = queue.popleft()
            curr = path[-1]
            if curr == target_id:
                return path
            if curr in visited:
                continue
            visited.add(curr)

            for target_node, _ in self.neighbors(curr, direction="OUT"):
                if target_node.node_id not in visited:
                    queue.append(path + [target_node.node_id])
        return None
