import time
import copy
from typing import Dict, Any, List, Optional
from ..core.twin_types import (
    GraphNodeType, GraphRelationType, ComponentLifecycleState
)
from ..core.twin_schema import (
    SemanticComponentNode, SemanticRelationship, AssetSnapshot
)

class SemanticAssetGraph:
    def __init__(self, asset_id: str):
        self.asset_id = asset_id
        self.nodes: Dict[str, SemanticComponentNode] = {}
        self.relationships: List[SemanticRelationship] = []
        self._semantic_index: Dict[str, str] = {} # semantic_id -> component_id

    def add_node(self, node: SemanticComponentNode):
        self.nodes[node.component_id] = node
        self._semantic_index[node.semantic_id] = node.component_id

    def get_node_by_semantic_id(self, semantic_id: str) -> Optional[SemanticComponentNode]:
        cid = self._semantic_index.get(semantic_id)
        return self.nodes.get(cid) if cid else None

    def add_relationship(self, source_id: str, target_id: str, rel_type: GraphRelationType, metadata: Optional[Dict[str, Any]] = None):
        rel = SemanticRelationship(source_id=source_id, target_id=target_id, relation_type=rel_type, metadata=metadata or {})
        self.relationships.append(rel)

    def get_dependents(self, component_id: str) -> List[str]:
        # Componentes que dependen de este component_id
        deps = []
        for rel in self.relationships:
            if rel.target_id == component_id and rel.relation_type == GraphRelationType.DEPENDS_ON:
                deps.append(rel.source_id)
        return deps

    def create_snapshot(self, snapshot_id: str) -> AssetSnapshot:
        nodes_copy = {cid: copy.deepcopy(node) for cid, node in self.nodes.items()}
        return AssetSnapshot(
            snapshot_id=snapshot_id,
            asset_id=self.asset_id,
            timestamp=time.time(),
            nodes=nodes_copy,
            relationships=copy.deepcopy(self.relationships)
        )

    def restore_snapshot(self, snapshot: AssetSnapshot):
        self.nodes = {cid: copy.deepcopy(node) for cid, node in snapshot.nodes.items()}
        self.relationships = copy.deepcopy(snapshot.relationships)
        self._semantic_index = {node.semantic_id: node.component_id for node in self.nodes.values()}
