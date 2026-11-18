import os
import json
import time
import threading
from typing import Dict, List, Optional, Any
from ..nodes.graph_node import GraphNode
from ..nodes.node_types import NodeType
from ..edges.graph_edge import GraphEdge
from ..edges.edge_types import RelationshipType

class DuplicateSemanticIdentityError(Exception):
    """Raised when an asset with duplicate primary semantic_id is registered."""
    pass

class ProjectKnowledgeGraphStore:
    """
    Persistent, transactional graph storage for the Project Knowledge Graph (F74).
    """
    def __init__(self, persistence_path: Optional[str] = None):
        self._nodes: Dict[str, GraphNode] = {}
        self._edges: Dict[str, GraphEdge] = {}
        self._semantic_index: Dict[str, str] = {} # semantic_id -> node_id
        self._lock = threading.RLock()
        self.persistence_path = persistence_path or r"E:\Darx_Proyect\Saved\KnowledgeGraph\darx_knowledge_graph.json"
        
        # Transaction snapshot buffers
        self._tx_nodes: Optional[Dict[str, GraphNode]] = None
        self._tx_edges: Optional[Dict[str, GraphEdge]] = None

        if self.persistence_path and os.path.exists(self.persistence_path):
            self.load_from_disk()

    def add_node(self, node: GraphNode) -> GraphNode:
        with self._lock:
            # Semantic identity uniqueness check for ASSET nodes
            if node.node_type == NodeType.ASSET and node.semantic_id:
                existing_node_id = self._semantic_index.get(node.semantic_id)
                if existing_node_id and existing_node_id != node.node_id:
                    raise DuplicateSemanticIdentityError(
                        f"Semantic ID '{node.semantic_id}' already assigned to node '{existing_node_id}'."
                    )
                self._semantic_index[node.semantic_id] = node.node_id

            node.updated_at = time.time()
            node.integrity_hash = node.compute_hash()
            self._nodes[node.node_id] = node
            self.save_to_disk()
            return node

    def get_node(self, node_id: str) -> Optional[GraphNode]:
        with self._lock:
            return self._nodes.get(node_id)

    def get_node_by_semantic_id(self, semantic_id: str) -> Optional[GraphNode]:
        with self._lock:
            node_id = self._semantic_index.get(semantic_id)
            if node_id:
                return self._nodes.get(node_id)
            for n in self._nodes.values():
                if n.semantic_id == semantic_id:
                    return n
            return None

    def remove_node(self, node_id: str):
        with self._lock:
            if node_id in self._nodes:
                node = self._nodes[node_id]
                if node.semantic_id in self._semantic_index:
                    del self._semantic_index[node.semantic_id]
                del self._nodes[node_id]
                # Remove connected edges
                self._edges = {k: v for k, v in self._edges.items() if v.source_node != node_id and v.target_node != node_id}
                self.save_to_disk()

    def list_nodes(self, node_type: Optional[NodeType] = None) -> List[GraphNode]:
        with self._lock:
            if node_type:
                return [n for n in self._nodes.values() if n.node_type == node_type]
            return list(self._nodes.values())

    def add_edge(self, edge: GraphEdge) -> GraphEdge:
        with self._lock:
            edge.integrity_hash = edge.compute_hash()
            self._edges[edge.edge_id] = edge
            self.save_to_disk()
            return edge

    def get_edge(self, edge_id: str) -> Optional[GraphEdge]:
        with self._lock:
            return self._edges.get(edge_id)

    def remove_edge(self, edge_id: str):
        with self._lock:
            if edge_id in self._edges:
                del self._edges[edge_id]
                self.save_to_disk()

    def list_edges(self, relationship_type: Optional[RelationshipType] = None) -> List[GraphEdge]:
        with self._lock:
            if relationship_type:
                return [e for e in self._edges.values() if e.relationship_type == relationship_type]
            return list(self._edges.values())

    # --- Transactions ---

    def begin_transaction(self):
        with self._lock:
            self._tx_nodes = {k: GraphNode.from_dict(v.to_dict()) for k, v in self._nodes.items()}
            self._tx_edges = {k: GraphEdge.from_dict(v.to_dict()) for k, v in self._edges.items()}

    def commit(self):
        with self._lock:
            self._tx_nodes = None
            self._tx_edges = None
            self.save_to_disk()

    def rollback(self):
        with self._lock:
            if self._tx_nodes is not None and self._tx_edges is not None:
                self._nodes = self._tx_nodes
                self._edges = self._tx_edges
                self._semantic_index = {n.semantic_id: n.node_id for n in self._nodes.values() if n.semantic_id}
                self._tx_nodes = None
                self._tx_edges = None
                self.save_to_disk()

    # --- Disk Persistence ---

    def save_to_disk(self):
        if not self.persistence_path:
            return
        os.makedirs(os.path.dirname(self.persistence_path), exist_ok=True)
        with self._lock:
            data = {
                "nodes": {k: v.to_dict() for k, v in self._nodes.items()},
                "edges": {k: v.to_dict() for k, v in self._edges.items()}
            }
            with open(self.persistence_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

    def load_from_disk(self):
        if not self.persistence_path or not os.path.exists(self.persistence_path):
            return
        if os.path.getsize(self.persistence_path) == 0:
            return
        with self._lock:
            try:
                with open(self.persistence_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self._nodes = {k: GraphNode.from_dict(v) for k, v in data.get("nodes", {}).items()}
                    self._edges = {k: GraphEdge.from_dict(v) for k, v in data.get("edges", {}).items()}
                    self._semantic_index = {n.semantic_id: n.node_id for n in self._nodes.values() if n.semantic_id}
            except Exception as e:
                print(f"[KnowledgeGraphStore] Warning loading from disk: {e}")
