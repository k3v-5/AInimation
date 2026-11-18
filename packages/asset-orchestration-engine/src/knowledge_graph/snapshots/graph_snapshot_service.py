import time
import hashlib
import json
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from ..nodes.graph_node import GraphNode
from ..edges.graph_edge import GraphEdge
from .graph_diff_engine import GraphDiff, GraphDiffEngine
from ..storage.graph_store import ProjectKnowledgeGraphStore

@dataclass
class GraphSnapshotRecord:
    snapshot_id: str
    timestamp: float = field(default_factory=time.time)
    nodes: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    edges: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    snapshot_hash: str = ""

    def __post_init__(self):
        if not self.snapshot_hash:
            self.snapshot_hash = self.compute_hash()

    def compute_hash(self) -> str:
        raw = json.dumps({
            "snapshot_id": self.snapshot_id,
            "nodes": self.nodes,
            "edges": self.edges
        }, sort_keys=True, default=str)
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

class GraphSnapshotService:
    """Manages creation, restoration, and diff comparison of knowledge graph snapshots."""
    def __init__(self, store: ProjectKnowledgeGraphStore):
        self.store = store
        self._snapshots: Dict[str, GraphSnapshotRecord] = {}

    def create_graph_snapshot(self, snapshot_id: str) -> GraphSnapshotRecord:
        nodes_dict = {n.node_id: n.to_dict() for n in self.store.list_nodes()}
        edges_dict = {e.edge_id: e.to_dict() for e in self.store.list_edges()}
        snap = GraphSnapshotRecord(
            snapshot_id=snapshot_id,
            nodes=nodes_dict,
            edges=edges_dict
        )
        self._snapshots[snapshot_id] = snap
        return snap

    def get_snapshot(self, snapshot_id: str) -> Optional[GraphSnapshotRecord]:
        return self._snapshots.get(snapshot_id)

    def restore_graph_snapshot(self, snapshot_id: str):
        snap = self.get_snapshot(snapshot_id)
        if not snap:
            raise KeyError(f"Graph snapshot {snapshot_id} not found.")
        self.store._nodes = {k: GraphNode.from_dict(v) for k, v in snap.nodes.items()}
        self.store._edges = {k: GraphEdge.from_dict(v) for k, v in snap.edges.items()}
        self.store._semantic_index = {n.semantic_id: n.node_id for n in self.store._nodes.values() if n.semantic_id}
        self.store.save_to_disk()

    def compare_graph_snapshots(self, snapshot_id_a: str, snapshot_id_b: str) -> GraphDiff:
        snap_a = self.get_snapshot(snapshot_id_a)
        snap_b = self.get_snapshot(snapshot_id_b)
        if not snap_a or not snap_b:
            raise KeyError("Both snapshots must exist to perform comparison.")

        nodes_a = {k: GraphNode.from_dict(v) for k, v in snap_a.nodes.items()}
        edges_a = {k: GraphEdge.from_dict(v) for k, v in snap_a.edges.items()}
        nodes_b = {k: GraphNode.from_dict(v) for k, v in snap_b.nodes.items()}
        edges_b = {k: GraphEdge.from_dict(v) for k, v in snap_b.edges.items()}

        return GraphDiffEngine.compute_diff(nodes_a, edges_a, nodes_b, edges_b)
