from dataclasses import dataclass, field
from typing import List, Dict, Set
from ..nodes.graph_node import GraphNode
from ..edges.graph_edge import GraphEdge
from ..edges.edge_types import RelationshipType
from ..storage.graph_store import ProjectKnowledgeGraphStore

class DependencyCycleDetectedError(Exception):
    """Raised when an illegal cyclic dependency is detected in the graph."""
    pass

@dataclass
class GraphConsistencyReport:
    is_valid: bool = True
    orphan_nodes: List[str] = field(default_factory=list)
    broken_edges: List[str] = field(default_factory=list)
    duplicate_nodes: List[str] = field(default_factory=list)
    cycles_detected: List[List[str]] = field(default_factory=list)

class GraphConsistencyValidator:
    """Validates structural integrity, orphan detection, and dependency cycles in the knowledge graph."""
    def __init__(self, store: ProjectKnowledgeGraphStore):
        self.store = store

    def validate_consistency(self) -> GraphConsistencyReport:
        report = GraphConsistencyReport()
        nodes = self.store.list_nodes()
        edges = self.store.list_edges()
        node_ids = {n.node_id for n in nodes}

        # 1. Broken Edges Check
        connected_node_ids = set()
        for e in edges:
            if e.source_node not in node_ids or e.target_node not in node_ids:
                report.broken_edges.append(e.edge_id)
                report.is_valid = False
            else:
                connected_node_ids.add(e.source_node)
                connected_node_ids.add(e.target_node)

        # 2. Orphan Nodes Check (nodes with zero connections)
        if len(nodes) > 1:
            for n in nodes:
                if n.node_id not in connected_node_ids:
                    report.orphan_nodes.append(n.node_id)

        # 3. Cycle Detection in Dependencies (USES, DEPENDS_ON, PART_OF)
        dep_edges = [e for e in edges if e.relationship_type in (RelationshipType.USES, RelationshipType.DEPENDS_ON, RelationshipType.PART_OF)]
        adj: Dict[str, List[str]] = {}
        for e in dep_edges:
            if e.source_node not in adj:
                adj[e.source_node] = []
            adj[e.source_node].append(e.target_node)

        visited = set()
        rec_stack = set()

        def dfs(node, path):
            visited.add(node)
            rec_stack.add(node)
            for neighbor in adj.get(node, []):
                if neighbor not in visited:
                    dfs(neighbor, path + [neighbor])
                elif neighbor in rec_stack:
                    cycle = path + [neighbor]
                    report.cycles_detected.append(cycle)
                    report.is_valid = False
            rec_stack.remove(node)

        for n in node_ids:
            if n not in visited:
                dfs(n, [n])

        return report
