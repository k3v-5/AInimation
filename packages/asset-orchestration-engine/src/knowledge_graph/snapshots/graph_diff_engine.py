from dataclasses import dataclass, field
from typing import Dict, Any, List
from ..nodes.graph_node import GraphNode
from ..edges.graph_edge import GraphEdge

@dataclass
class GraphDiff:
    nodes_added: List[str] = field(default_factory=list)
    nodes_removed: List[str] = field(default_factory=list)
    nodes_changed: List[str] = field(default_factory=list)
    edges_added: List[str] = field(default_factory=list)
    edges_removed: List[str] = field(default_factory=list)
    edges_changed: List[str] = field(default_factory=list)

    @property
    def has_changes(self) -> bool:
        return bool(
            self.nodes_added or self.nodes_removed or self.nodes_changed or
            self.edges_added or self.edges_removed or self.edges_changed
        )

class GraphDiffEngine:
    """Calculates delta differences between two knowledge graph snapshots or states."""
    
    @classmethod
    def compute_diff(
        cls,
        before_nodes: Dict[str, GraphNode],
        before_edges: Dict[str, GraphEdge],
        after_nodes: Dict[str, GraphNode],
        after_edges: Dict[str, GraphEdge]
    ) -> GraphDiff:
        diff = GraphDiff()

        # Nodes diff
        before_node_keys = set(before_nodes.keys())
        after_node_keys = set(after_nodes.keys())

        diff.nodes_added = sorted(list(after_node_keys - before_node_keys))
        diff.nodes_removed = sorted(list(before_node_keys - after_node_keys))

        for k in before_node_keys.intersection(after_node_keys):
            if before_nodes[k].integrity_hash != after_nodes[k].integrity_hash:
                diff.nodes_changed.append(k)

        # Edges diff
        before_edge_keys = set(before_edges.keys())
        after_edge_keys = set(after_edges.keys())

        diff.edges_added = sorted(list(after_edge_keys - before_edge_keys))
        diff.edges_removed = sorted(list(before_edge_keys - after_edge_keys))

        for k in before_edge_keys.intersection(after_edge_keys):
            if before_edges[k].integrity_hash != after_edges[k].integrity_hash:
                diff.edges_changed.append(k)

        return diff
