from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from .scene_types import SpatialRelationType

@dataclass
class GraphNode:
    node_id: str
    node_type: str # SCENE, REGION, AREA, ASSET, PROP
    asset_type: Optional[str] = None
    parent_id: Optional[str] = None
    parameters: Dict[str, Any] = field(default_factory=dict)
    transform: Dict[str, float] = field(default_factory=lambda: {"x": 0.0, "y": 0.0, "z": 0.0})

@dataclass
class GraphEdge:
    source_id: str
    target_id: str
    relation_type: SpatialRelationType
    metadata: Dict[str, Any] = field(default_factory=dict)

class CompositionGraph:
    def __init__(self):
        self.nodes: Dict[str, GraphNode] = {}
        self.edges: List[GraphEdge] = []

    def add_node(self, node: GraphNode):
        self.nodes[node.node_id] = node

    def add_edge(self, source_id: str, target_id: str, relation_type: SpatialRelationType, metadata: Dict[str, Any] = None):
        self.edges.append(GraphEdge(source_id, target_id, relation_type, metadata or {}))

    def get_children(self, parent_id: str) -> List[GraphNode]:
        return [n for n in self.nodes.values() if n.parent_id == parent_id]

    def get_relations_for_node(self, node_id: str) -> List[GraphEdge]:
        return [e for e in self.edges if e.source_id == node_id or e.target_id == node_id]
